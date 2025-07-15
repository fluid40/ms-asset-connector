from pydantic import BaseModel, Field


class GetValuePayload(BaseModel):
    """
    We introduce this class to wrap the parameters that are passed via the `get_value` GET method.
    For now, it only includes raw JSON content.

    The JSON content is a Reference (AAS type) to a property in the AID submodel.
    We pass it raw to that you, the developer, can choose your favorite AAS SDK to deserialize it as Reference class.
    """
    json_content: str = Field(..., alias="jsonContent")
