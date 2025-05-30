using System.Text.Json.Serialization;

namespace csharp_connector_template.Models
{
    public class GetValuePayload
    {
        /// <summary>
        /// We introduce this class to wrap the parameters that are passed via the `get_value` GET method.
        /// For now, it only includes raw JSON content.
        /// 
        /// The JSON content is a Reference (AAS type) to a property in the AID submodel.
        /// We pass it raw to that you, the developer, can choose your favorite AAS SDK to deserialize it as Reference class.
        /// </summary>
        [JsonPropertyName("jsonContent")]
        public string jsonContent { get; set; }
    }
}
