using System.Text.Json.Serialization;
using AasCore.Aas3_0;

namespace csharp_connector_template.Models
{
    public class SetConfigPayload
    {
        /// <summary>
        /// We introduce this class to wrap the configuration that is passed via the set_config POST method.
        /// For now, it only includes raw JSON content.
        /// 
        /// The JSON content is exactly the AID submodel.
        /// We pass it raw so you can use your favorite AAS SDK to deserialize it as a Submodel class.
        /// </summary>
        [JsonPropertyName("Aid")]
        public Submodel aidSm { get; set; }
    }
}
