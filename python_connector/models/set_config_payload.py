import json
from typing import Any

from basyx.aas.adapter.json import AASFromJsonDecoder
from basyx.aas.model import Submodel
from pydantic import BaseModel, Field, PrivateAttr


class SetConfigPayload(BaseModel):  # noqa: D101
    """Defines the model class of the payload for the `add_or_update_config` (URL `/add-config`) endpoint
    of this application using Pydantic.

    The JSON payload must contain exactly the following fields:
    - `Aid`

    Inside the `Aid`-field, a properly serialized AID submodel according to the AAS JSON serialization must be provided.
    Will be parsed as `basyx.aas.model.Submodel`.

    Example:
    ```
    {
      "Aid": {
         "idShort": "AssetInterfacesDescription",
         "id": "https://example.com/ids/sm/1234_5678_90",
         "kind": "Instance",
         // ...
      }
    }
    ```
    """

    aid_dict: dict = Field(..., alias="Aid", exclude=True)

    _aid_sm: Submodel = PrivateAttr(default=None)

    def __init__(self, **data: Any):  # noqa: D107
        super().__init__(**data)
        aid_string = json.dumps(self.aid_dict)
        self._aid_sm = json.loads(aid_string, cls=AASFromJsonDecoder)
        # self._aid_sm = AASFromJsonDecoder.object_hook(self.aid_dict) NOT WORKING FOR LOOPING ELEMENTS
