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
    
    content: str = Field(
        default="{}",
        description="Json content of the response.",
        alias="Content",
        example="",
    )
    
def create_response(status_code: int = 200, message: str = "Successfully", content: str = "{}") -> ResponseBody:
    """
    Create a ResponseBody instance with the given parameters.
    
    :param status_code: The HTTP status code of the response.
    :param message: A message providing additional information about the response.
    :param content: Json content of the response.
    :return: An instance of ResponseBody.
    """
    return ResponseBody(status_code=status_code, message=message, content=content)