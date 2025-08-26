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
            // TODO: store the AID Submodel object, e.g., as global variable

            return Ok(new ResponseBody()
            {
                Payload = payload.aidSm,
                Message = "Successfully received AID config",
                StatusCode = 200
            });
        }

        [HttpPost("get-value")]
        public IActionResult GetValue([FromBody] GetValuePayload payload)
        {

            // TODO: find the SMC in the cached AID Submodel to which the reference points

            // TODO: read the details in the SMC and use it to establish a connection to the asset

            // TODO: return the value
            var result = "myResult";

            return Ok(new ResponseBody()
            {
                Payload = payload.reference,
                Message = "Successfully received Reference to AID",
                StatusCode = 200,
                Value = result
            });
        }
    }
}
