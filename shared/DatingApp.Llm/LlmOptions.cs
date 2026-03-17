namespace DatingApp.Llm;

/// <summary>
/// LLM provider configuration — which providers to use, models, budgets.
/// API keys should be set via environment variables (GEMINI_API_KEY, GROQ_API_KEY)
/// with appsettings as fallback.
/// </summary>
public class LlmOptions
{
    public const string SectionName = "Llm";

    public string PrimaryProvider { get; set; } = "gemini";
    public string FallbackProvider { get; set; } = "groq";
    public long DailyTokenBudget { get; set; } = 500_000;
    public int MaxTokensPerMessage { get; set; } = 150;
    public double Temperature { get; set; } = 0.7;
    public string GeminiModel { get; set; } = "gemini-2.0-flash-lite";
    public string GroqModel { get; set; } = "llama-3.3-70b-versatile";
    public string OllamaModel { get; set; } = "qwen3:8b";
    public string OllamaBaseUrl { get; set; } = "http://localhost:11434";
    public Dictionary<string, string> ApiKeys { get; set; } = new();
}
