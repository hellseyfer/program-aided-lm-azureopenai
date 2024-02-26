from typing import Annotated, List, Optional, Type
from pydantic import BaseModel, HttpUrl, Field, StrictBool
import requests
from langchain.tools import BaseTool, StructuredTool
import json
from typing import Literal
from langchain.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
import os 

base_url = os.getenv("BACKEND_BASE")


class InputCloudSource(BaseModel):
    cloudSourceId: str = Field(description="The cloud source id returned after its creation. Required field")
class LiveTranscription(BaseModel):
    enableLiveTranscription: StrictBool

class InputLossSlate(BaseModel):
    enableInputLossSlate: StrictBool
    imageUrl: str  = Field(description="Image's URL. The default value is https://harmonicinc.app.box.com/s/ihapp8m4hrkpuikprxdi5x5c9081k991")

class OutputItem(BaseModel):
    encryptionMethod: str  = Field(description="Encryption method. default is Clear")
    packageType: Literal["cmaf-dash", "cmaf-hls"]
    "output type. Default is cmaf-dash"

class AddOns(BaseModel):
    pass  # Placeholder for now, you can define specific fields if needed

class CreateLiveEventInputSchema(BaseModel):
    """Input for Creating a live event. requires a cloudsourceId that comes from the create_cloud_source response."""
    name: str = Field(description="Live event name. Put a random name if not specified")
    input: InputCloudSource
    transcodingProfile: str = Field(description="Transcoding profile. Default is Standard")
    liveTranscription: LiveTranscription
    inputLossSlate: InputLossSlate
    packagingProfile: str = Field(description="Packaging Profile, default is Standard")
    publishName: str = Field(description="Publish Name. Default is simplified version of name property")
    output: List[OutputItem]
    addOns: AddOns
    goLiveTime: str = Field(description="UTC datetime string. Default is current date.")
    endTime: str = Field(description="UTC datetime strin. Default is an hour after current date.")

class CreateLiveEventTool(BaseTool):
    name="create_live_event"
    description="""Function to create a live event. Add transcoding presets, packaging formats, DRM preference and any add-on features to your live event. 
    Once the live event is created, you can get the ingestion URL endpoint.
    It requires to first call create_cloud_source in order to use the cloudsourceId returned."""
    args_schema: Optional[Type[BaseModel]] = CreateLiveEventInputSchema
    
    def _run(
        self,
        name: str,
        input: InputCloudSource,
        transcodingProfile: str,
        liveTranscription: LiveTranscription,
        inputLossSlate: InputLossSlate,
        packagingProfile: str,
        publishName: str,
        output: List[OutputItem],
        addOns: AddOns,
        goLiveTime: str,
        endTime: str
        ) -> str:
        """Use the tool."""
        url = f"{base_url}/live/v1/events"
        
          # Create an instance of CreateLiveEventSchema directly from the parameters
        data = CreateLiveEventInputSchema(
            name=name,
            input=input,
            transcodingProfile=transcodingProfile,
            liveTranscription=liveTranscription,
            inputLossSlate=inputLossSlate,
            packagingProfile=packagingProfile,
            publishName=publishName,
            output=output,
            addOns=addOns,
            goLiveTime=goLiveTime,
            endTime=endTime
        )
        
        # Use the json() method to get a JSON string directly from the Pydantic model
        json_data = data.json()
        result = requests.post(url, json=json_data, timeout=3)
        return result.text
        
    async def _arun(
        self, query: str, run_manager: Optional[AsyncCallbackManagerForToolRun] = None
    ) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("create_live_event does not support async")

