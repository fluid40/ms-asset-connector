using csharp_connector_template.Models;
using Microsoft.AspNetCore.Mvc;

namespace csharp_connector_template.Controllers
{
    [ApiController]
    [Route("/")]
    public class ConnectorApiServiceController: ControllerBase
    {
        [HttpPost("set-config")]
        public IActionResult SetConfig([FromBody] SetConfigPayload payload)
        {
            // Revert escaped quotes (replace \" with ") if necessary
            string rawJson = payload.jsonContent.Replace("\\\"", "\"");

            // TODO: use an AAS SDK to deserialize the content as Submodel

            // TODO: store the deserialized AID Submodel class, e.g., as global variable

            return Ok(new
            {
                message = $"Successfully invoked `/set-config` with raw JSON in payload:\n\n{rawJson}"
            });
        }

        [HttpPost("get-value")]
        public IActionResult GetValue([FromBody] GetValuePayload payload)
        {
            // Revert escaped quotes (replace \" with ") if necessary
            string rawJson = payload.jsonContent.Replace("\\\"", "\"");

            // TODO: use an AAS SDK to deserialize the content as Reference

            // TODO: find the SMC in the cached AID Submodel to which the reference points

            // TODO: read the details in the SMC and use it to establish a connection to the asset

            // TODO: return the value
            var result = "myResult";

            return Ok(new
            {
                message = $"Successfully invoked `/get-value` with raw JSON in payload:\n\n{rawJson}",
                value = result
            });
        }
    }
}
