using System.Diagnostics;
using System.Text;
using System.Text.Json;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Options;

namespace DatingApp.Llm.Providers;

/// <summary>
/// Google Gemini provider — primary (FREE tier: excellent Swedish).
/// </summary>
public class GeminiLlmProvider : ILlmProvider
{
    private readonly HttpClient _http;
    private readonly ILogger<GeminiLlmProvider> _logger;
    private readonly LlmOptions _options;

    private static readonly JsonSerializerOptions JsonOpts = new()
    {
        PropertyNamingPolicy = JsonNamingPolicy.CamelCase,
        PropertyNameCaseInsensitive = true
    };

    public string ProviderName => "gemini";

    public GeminiLlmProvider(HttpClient http, IOptions<LlmOptions> options, ILogger<GeminiLlmProvider> logger)
    {
        _http = http;
        _logger = logger;
        _options = options.Value;
        _http.Timeout = TimeSpan.FromSeconds(30);
    }

    public async Task<LlmResponse> GenerateAsync(LlmRequest request, CancellationToken ct = default)
    {
        var apiKey = GetApiKey();
        if (string.IsNullOrEmpty(apiKey))
            return LlmResponse.Failure(ProviderName, "GEMINI_API_KEY not configured");

        var model = _options.GeminiModel;
        var url = $"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={apiKey}";

        var contents = new List<object>();
        var systemInstruction = new { parts = new[] { new { text = request.SystemPrompt } } };

        foreach (var msg in request.Messages)
        {
            contents.Add(new
            {
                role = msg.Role == "assistant" ? "model" : "user",
                parts = new[] { new { text = msg.Content } }
            });
        }

        if (contents.Count == 0)
            contents.Add(new { role = "user", parts = new[] { new { text = "Hej!" } } });

        var payload = new
        {
            system_instruction = systemInstruction,
            contents,
            generationConfig = new
            {
                maxOutputTokens = request.MaxTokens,
                temperature = request.Temperature,
                topP = 0.95
            }
        };

        var sw = Stopwatch.StartNew();
        try
        {
            var json = JsonSerializer.Serialize(payload, JsonOpts);
            var httpReq = new HttpRequestMessage(HttpMethod.Post, url)
            {
                Content = new StringContent(json, Encoding.UTF8, "application/json")
            };

            var response = await _http.SendAsync(httpReq, ct);
            sw.Stop();

            if (!response.IsSuccessStatusCode)
            {
                var errorBody = await response.Content.ReadAsStringAsync(ct);
                _logger.LogWarning("Gemini API {Status}: {Body}", response.StatusCode, errorBody[..Math.Min(200, errorBody.Length)]);

                if ((int)response.StatusCode == 429)
                    return LlmResponse.Failure(ProviderName, "rate_limited");

                return LlmResponse.Failure(ProviderName, $"HTTP {response.StatusCode}");
            }

            var respJson = await response.Content.ReadAsStringAsync(ct);
            using var doc = JsonDocument.Parse(respJson);

            var text = doc.RootElement
                .GetProperty("candidates")[0]
                .GetProperty("content")
                .GetProperty("parts")[0]
                .GetProperty("text")
                .GetString() ?? string.Empty;

            var tokensUsed = 0;
            if (doc.RootElement.TryGetProperty("usageMetadata", out var usage))
            {
                if (usage.TryGetProperty("totalTokenCount", out var total))
                    tokensUsed = total.GetInt32();
            }

            return new LlmResponse
            {
                Content = text.Trim(),
                TokensUsed = tokensUsed,
                LatencyMs = sw.ElapsedMilliseconds,
                Provider = ProviderName,
                Success = true
            };
        }
        catch (TaskCanceledException) when (!ct.IsCancellationRequested)
        {
            return LlmResponse.Failure(ProviderName, "timeout");
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Gemini API call failed after {Ms}ms", sw.ElapsedMilliseconds);
            return LlmResponse.Failure(ProviderName, ex.Message);
        }
    }

    public async Task<bool> IsAvailableAsync(CancellationToken ct = default)
    {
        var apiKey = GetApiKey();
        if (string.IsNullOrEmpty(apiKey)) return false;
        try
        {
            var url = $"https://generativelanguage.googleapis.com/v1beta/models?key={apiKey}";
            var resp = await _http.GetAsync(url, ct);
            return resp.IsSuccessStatusCode;
        }
        catch { return false; }
    }

    private string GetApiKey() =>
        Environment.GetEnvironmentVariable("GEMINI_API_KEY") ?? _options.ApiKeys.GetValueOrDefault("gemini", "");
}
