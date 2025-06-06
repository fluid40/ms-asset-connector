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
    