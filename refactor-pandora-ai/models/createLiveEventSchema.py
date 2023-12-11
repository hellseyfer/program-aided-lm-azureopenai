from typing import List, Optional
from pydantic import BaseModel, HttpUrl, Field

class LiveTranscription(BaseModel):
    enableLiveTranscription: bool

class InputLossSlate(BaseModel):
    enableInputLossSlate: bool
    imageUrl: HttpUrl

class OutputItem(BaseModel):
    encryptionMethod: str
    packageType: str

class AddOns(BaseModel):
    pass  # Placeholder for now, you can define specific fields if needed

class CreateLiveEventSchema(BaseModel):
    name: str
    input: dict  # You can create a more specific Pydantic model for the 'input' field if needed
    transcodingProfile: str
    liveTranscription: LiveTranscription
    inputLossSlate: InputLossSlate
    packagingProfile: str
    publishName: str
    output: List[OutputItem]
    addOns: AddOns
    goLiveTime: str
    endTime: str
