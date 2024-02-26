from typing import Optional, Type
from langchain.tools import BaseTool, StructuredTool, Tool, tool
from langchain.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
from typing import List, Optional
from typing import Literal
from pydantic import BaseModel, Field

import requests
import json
import os

base_url = os.getenv("BACKEND_BASE")

class CloudSourceInputSchema(BaseModel):
    """Input for Creating a cloud source."""
    name: str = Field(description="Cloud Source Name. Put a random name if not specified")
    protocol: Literal["SRT", "RTMP"]
    "Ingest protocol. The default value is 'SRT'"
    maxOutputConnections: int = Field(
        description="number of output connections. The default value is 1", lt=1000)
    redundancyMode: Literal["NONE", "ACTIVE-ACTIVE", "ACTIVE-STANDBY"]
    "Redundancy mode. The default value is 'NONE'"
    streamCount: int = Field(
        description="Number of streams. The default value is 1", lt=20, gt=0)

class CreateCloudSourceTool(BaseTool):
    name = "create_cloud_source"
    description = """Function to create a cloud source. A Cloud Source is an endpoint in the cloud taking stored video and content from outside sources. Once the cloud source is created, you can get the ingestion URL endpoint.
    In the meantime, you can get a Source Preview URL to verify that your ingested source is properly running on the cloud."""
    args_schema: Optional[Type[BaseModel]] = CloudSourceInputSchema
 
    def _run(
        self, name: str, protocol: str, maxOutputConnections: int, redundancyMode: str, streamCount: int
    ) -> str:
        """Use the tool."""
        url = f"{base_url}/live/v1/cloudsources"
        
        data = {
            "name": name,
            "protocol": protocol,
            "maxOutputConnections": maxOutputConnections,
            "redundancyMode": redundancyMode,
            "streamCount": streamCount
        }
        # Convert the dictionary to a JSON string
        json_data = json.dumps(data, indent=2)

        result = requests.post(url, json=json_data)
        return result.text

    async def _arun(
        self, query: str, run_manager: Optional[AsyncCallbackManagerForToolRun] = None
    ) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("create_cloud_source does not support async")

