using DatingApp.Llm.Providers;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;

namespace DatingApp.Llm;

public static class LlmServiceCollectionExtensions
{
    /// <summary>
    /// Register LLM providers, router, and options from configuration.
    /// Expects an "Llm" section in the configuration.
    /// </summary>
    public static IServiceCollection AddLlm(this IServiceCollection services, IConfiguration configuration)
    {
        services.Configure<LlmOptions>(configuration.GetSection(LlmOptions.SectionName));

        services.AddHttpClient<GeminiLlmProvider>();
        services.AddHttpClient<GroqLlmProvider>();
        services.AddHttpClient<OllamaLlmProvider>();

        services.AddSingleton<ILlmProvider>(sp => sp.GetRequiredService<GeminiLlmProvider>());
        services.AddSingleton<ILlmProvider>(sp => sp.GetRequiredService<GroqLlmProvider>());
        services.AddSingleton<ILlmProvider>(sp => sp.GetRequiredService<OllamaLlmProvider>());

        services.AddSingleton<LlmRouter>();

        return services;
    }
}
