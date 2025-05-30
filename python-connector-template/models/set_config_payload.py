from pydantic import BaseModel


class ConfigPayload(BaseModel):
    """
    We introduce this class to wrap the configuration that is passed via the `set_config` POST method.
    For now, it only includes raw JSON content.

    The JSON content is exactly the AID submodel.
    We pass it raw to that you, the developer, can choose your favorite AAS SDK to deserialize it as Submodel class.
    """
    json_content: str
