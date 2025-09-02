using System.Text.Json;
using System.Text.Json.Nodes;
using System.Text.Json.Serialization;

// TODO: replace with Basyx import if you wish
using AasCore.Aas3_0;

namespace csharp_connector_template.Models;

public class ReferenceConverter: JsonConverter<Reference>
{
    public override Reference? Read(ref Utf8JsonReader reader, Type typeToConvert, JsonSerializerOptions options)
    {
        string rawJson = JsonDocument.ParseValue(ref reader).RootElement.GetRawText();
        
        // TODO: replace with Basyx logic if you wish
        return Jsonization.Deserialize.ReferenceFrom(JsonNode.Parse(rawJson) ?? new JsonObject());
    }

    public override void Write(Utf8JsonWriter writer, Reference value, JsonSerializerOptions options)
    {
        // TODO: replace with Basyx logic if you wish
        string json = Jsonization.Serialize.ToJsonObject(value).ToJsonString();
        
        using var doc = JsonDocument.Parse(json);
        doc.RootElement.WriteTo(writer);
    }
}