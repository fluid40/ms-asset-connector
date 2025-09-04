using System.Text.Json.Serialization;

namespace csharp_connector_template.Models;

public class ResponseBody
{
    /// <summary>
    /// The HTTP status code of the response.
    /// </summary>
    [JsonPropertyName("StatusCode")]
    public int StatusCode { get; set; } = 200;

    /// <summary>
    /// A message providing additional information about the response.
    /// </summary>
    [JsonPropertyName("Message")]
    public string Message { get; set; } = "Success";

    /// <summary>
    /// JSON content of the response.
    /// </summary>
    [JsonPropertyName("Payload")]
    public object Payload { get; set; } = new { };

    /// <summary>
    /// The value returned by the operation, if applicable.
    /// </summary>
    [JsonPropertyName("Value")]
    public string? Value { get; set; }
}