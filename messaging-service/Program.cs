using DatingApp.Shared.Middleware;
using FluentValidation;
using MessagingService.Data;
using MessagingService.Extensions;
using MessagingService.Hubs;
using MessagingService.Middleware;
using MessagingService.Services;
using Microsoft.AspNetCore.Authentication.JwtBearer;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.IdentityModel.Tokens;
using Microsoft.OpenApi.Models;
using System.Threading.Tasks;
using OpenTelemetry.Metrics;
using OpenTelemetry.Resources;
using OpenTelemetry.Trace;

var builder = WebApplication.CreateBuilder(args);

builder.Logging.AddSimpleConsole(options =>
{
    options.IncludeScopes = true;
    options.TimestampFormat = "yyyy-MM-dd HH:mm:ss ";
});

// Add services to the container.
var isDemoMode = Environment.GetEnvironmentVariable("DEMO_MODE") == "true";

if (isDemoMode)
{
    Console.WriteLine("MessagingService: Using in-memory database for demo mode");
    builder.Services.AddDbContext<MessagingDbContext>(options =>
        options.UseInMemoryDatabase("MessagingServiceDemo"));
}
else
{
    builder.Services.AddDbContext<MessagingDbContext>(options =>
        options.UseMySql(
            builder.Configuration.GetConnectionString("DefaultConnection"),
            new MySqlServerVersion(new Version(8, 0, 25))
        )
    );
}

// Add Authentication
builder.Services.AddKeycloakAuthentication(builder.Configuration, options =>
{
    options.Events = new JwtBearerEvents
    {
        OnMessageReceived = context =>
        {
            var accessToken = context.Request.Query["access_token"];
            var path = context.HttpContext.Request.Path;
            if (!string.IsNullOrEmpty(accessToken) && path.StartsWithSegments("/messagingHub"))
            {
                context.Token = accessToken;
            }
            return Task.CompletedTask;
        }
    };

    options.TokenValidationParameters.ClockSkew = TimeSpan.Zero;
});

// Add Authorization
builder.Services.AddAuthorization();

// Add Controllers
builder.Services.AddControllers();

// Add Health Checks
builder.Services.AddHealthChecks();

// Add SignalR
builder.Services.AddSignalR(options =>
{
    options.EnableDetailedErrors = true;
    options.KeepAliveInterval = TimeSpan.FromSeconds(15);
    options.ClientTimeoutInterval = TimeSpan.FromSeconds(30);
});

// Add Custom Services
builder.Services.AddScoped<IMessageService, MessageService>();
builder.Services.AddScoped<IMessageServiceSpec, MessageServiceSpec>();
builder.Services.AddScoped<IContentModerationService, ContentModerationService>();
builder.Services.AddScoped<ISpamDetectionService, SpamDetectionService>();
builder.Services.AddScoped<IPersonalInfoDetectionService, PersonalInfoDetectionService>();
builder.Services.AddScoped<IRateLimitingService, RateLimitingService>();
builder.Services.AddScoped<IReportingService, ReportingService>();
builder.Services.AddCorrelationIds();

// Internal API Key Authentication for service-to-service calls
builder.Services.AddScoped<InternalApiKeyAuthFilter>();
builder.Services.AddTransient<InternalApiKeyAuthHandler>();

// Add HttpClient for Safety Service
builder.Services.AddHttpClient<ISafetyServiceClient, SafetyServiceClient>(client =>
{
    client.BaseAddress = new Uri(builder.Configuration["Gateway:BaseUrl"] ?? "http://dejting-yarp:8080");
})
.AddHttpMessageHandler<InternalApiKeyAuthHandler>();

// Add HttpClient for MessageServiceSpec (to call MatchmakingService)
builder.Services.AddHttpClient<MessageServiceSpec>(client =>
{
    client.BaseAddress = new Uri(builder.Configuration["Gateway:BaseUrl"] ?? "http://dejting-yarp:8080");
})
.AddHttpMessageHandler<InternalApiKeyAuthHandler>();

// Add MediatR for CQRS
builder.Services.AddMediatR(cfg => cfg.RegisterServicesFromAssembly(typeof(Program).Assembly));

// Add FluentValidation
builder.Services.AddValidatorsFromAssembly(typeof(Program).Assembly);

// Add Memory Cache for rate limiting and content caching
builder.Services.AddMemoryCache();

// Add CORS
builder.Services.AddCors(options =>
{
    options.AddPolicy("AllowSpecificOrigins", policy =>
    {
        policy.WithOrigins("http://localhost:3000", "http://localhost:8080")
              .AllowAnyHeader()
              .AllowAnyMethod()
              .AllowCredentials();
    });
});

// Learn more about configuring Swagger/OpenAPI at https://aka.ms/aspnetcore/swashbuckle
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen(c =>
{
    c.SwaggerDoc("v1", new OpenApiInfo 
    { 
        Title = "Dating App Messaging Service API", 
        Version = "v1",
        Description = "Real-time messaging service with proactive safety features including content moderation, spam detection, and personal information protection."
    });
    
    // JWT Authentication
    c.AddSecurityDefinition("Bearer", new OpenApiSecurityScheme
    {
        Description = "JWT Authorization header using Bearer scheme. Enter 'Bearer' [space] and then your token.",
        Name = "Authorization",
        In = ParameterLocation.Header,
        Type = SecuritySchemeType.ApiKey,
        Scheme = "Bearer"
    });
    
    c.AddSecurityRequirement(new OpenApiSecurityRequirement
    {
        {
            new OpenApiSecurityScheme
            {
                Reference = new OpenApiReference
                {
                    Type = ReferenceType.SecurityScheme,
                    Id = "Bearer"
                }
            },
            Array.Empty<string>()
        }
    });
    
    var xmlFile = $"{System.Reflection.Assembly.GetExecutingAssembly().GetName().Name}.xml";
    var xmlPath = Path.Combine(AppContext.BaseDirectory, xmlFile);
    if (File.Exists(xmlPath))
    {
        c.IncludeXmlComments(xmlPath);
    }
});

// Configure OpenTelemetry for metrics and distributed tracing
builder.Services.AddOpenTelemetry()
    .ConfigureResource(resource => resource
        .AddService(serviceName: "messaging-service",
                    serviceVersion: "1.0.0"))
    .WithMetrics(metrics => metrics
        .AddAspNetCoreInstrumentation()
        .AddHttpClientInstrumentation()
        .AddRuntimeInstrumentation()
        .AddMeter("MessagingService")
        .AddPrometheusExporter())
    .WithTracing(tracing => tracing
        .AddAspNetCoreInstrumentation(options =>
        {
            options.RecordException = true;
            options.Filter = (httpContext) =>
            {
                // Don't trace health checks and metrics endpoints
                var path = httpContext.Request.Path.ToString();
                return !path.Contains("/health") && !path.Contains("/metrics");
            };
        })
        .AddHttpClientInstrumentation()
        .AddEntityFrameworkCoreInstrumentation(options =>
        {
            options.SetDbStatementForText = true;
            options.EnrichWithIDbCommand = (activity, command) =>
            {
                activity.SetTag("db.query", command.CommandText);
            };
        }));

// Create custom meters for business metrics
System.Diagnostics.Metrics.Meter customMeter = new("MessagingService");
var messagesSentCounter = customMeter.CreateCounter<long>("messages_sent_total", description: "Total number of messages sent");
var messagesModeratedCounter = customMeter.CreateCounter<long>("messages_moderated_total", description: "Total number of messages moderated/blocked");
var messageDeliveryDuration = customMeter.CreateHistogram<double>("message_delivery_duration_ms", description: "Duration of message delivery via SignalR in milliseconds");
var spamDetectionScore = customMeter.CreateHistogram<double>("spam_detection_score", description: "Distribution of spam detection scores");

var app = builder.Build();

// Configure the HTTP request pipeline.
if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}

app.UseHttpsRedirection();

app.UseCors("AllowSpecificOrigins");

app.UseCorrelationIds();

// Add custom rate limiting middleware
app.UseMiddleware<RateLimitingMiddleware>();

app.UseAuthentication();
app.UseAuthorization();

app.MapControllers();

app.MapHealthChecks("/health");

// Prometheus metrics endpoint
app.MapPrometheusScrapingEndpoint("/metrics");

// Map SignalR hub - Use the spec-compliant hub
app.MapHub<MessagingHubSpec>("/messagingHub");

// Ensure database is created
using (var scope = app.Services.CreateScope())
{
    var context = scope.ServiceProvider.GetRequiredService<MessagingDbContext>();
    if (isDemoMode)
    {
        Console.WriteLine("MessagingService: Using in-memory database, skipping migrations");
        context.Database.EnsureCreated();
    }
    else
    {
        context.Database.EnsureCreated();
    }
}

app.Run();
