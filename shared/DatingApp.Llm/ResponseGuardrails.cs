using System.Text.RegularExpressions;

namespace DatingApp.Llm;

/// <summary>
/// Post-processing guardrails for LLM output. Returns null if valid, or rejection reason.
/// </summary>
public static class ResponseGuardrails
{
    private static readonly Regex PhoneRegex = new(@"\d{3,}[\-\s]?\d{3,}", RegexOptions.Compiled);
    private static readonly Regex UrlRegex = new(@"(https?://|www\.|\.com|\.se|\.net|\.org)", RegexOptions.Compiled | RegexOptions.IgnoreCase);

    public static string? Validate(string content, int maxLength = 280)
    {
        if (string.IsNullOrWhiteSpace(content))
            return "empty_response";

        if (content.Length > maxLength)
            return "too_long";

        if (PhoneRegex.IsMatch(content))
            return "contains_phone_number";

        if (UrlRegex.IsMatch(content))
            return "contains_url";

        return null;
    }
}
