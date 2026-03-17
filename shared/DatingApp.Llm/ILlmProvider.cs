namespace DatingApp.Llm;

/// <summary>
/// Provider-agnostic LLM interface. Each provider (Gemini, Groq, Ollama)
/// implements this to generate text completions.
/// </summary>
public interface ILlmProvider
{
    string ProviderName { get; }
    Task<LlmResponse> GenerateAsync(LlmRequest request, CancellationToken ct = default);
    Task<bool> IsAvailableAsync(CancellationToken ct = default);
}

public class LlmRequest
{
    public string SystemPrompt { get; set; } = string.Empty;
    public List<LlmMessage> Messages { get; set; } = new();
    public int MaxTokens { get; set; } = 150;
    public double Temperature { get; set; } = 0.7;
}

public class LlmMessage
{
    public string Role { get; set; } = "user";
    public string Content { get; set; } = string.Empty;

    public LlmMessage() { }
    public LlmMessage(string role, string content) { Role = role; Content = content; }
}

public class LlmResponse
{
    public string Content { get; set; } = string.Empty;
    public int TokensUsed { get; set; }
    public long LatencyMs { get; set; }
    public string Provider { get; set; } = string.Empty;
    public bool Success { get; set; }
    public string? Error { get; set; }

    public static LlmResponse Failure(string provider, string error) => new()
    {
        Provider = provider, Success = false, Error = error
    };
}
