from pydantic import BaseModel, Field

class ResponseBody(BaseModel):
    status_code: int = Field(
        default=200,
        description="The HTTP status code of the response.",
        alias="StatusCode",
        example=200,
    )
    
    message: str = Field(
        default="Successfully",
        description="A message providing additional information about the response.",
        alias="Message",
        example="Successfully invoked `/set-config` with raw JSON in payload",
    )
    
    payload: str = Field(
        default="{}",
        description="Json content of the response.",
        alias="Payload",
        example="",
    )
    
    value: str = Field(
        default="",
        description="The value returned by the operation, if applicable.",
        alias="Value",
        example="myResult",
    )    
    
def create_response(status_code: int, message: str, payload: str = "{}", value: str = "") -> ResponseBody:
    """
    Create a ResponseBody instance with the given parameters.
    
    :param status_code: The HTTP status code of the response.
    :param message: A message providing additional information about the response.
    :param payload: Json content of the response.
    :param value: The value returned by the operation, if applicable.
    :return: An instance of ResponseBody.
    """
    body = ResponseBody()
    body.status_code = status_code
    body.message = message
    body.payload = payload
    body.value = value
    
    return body