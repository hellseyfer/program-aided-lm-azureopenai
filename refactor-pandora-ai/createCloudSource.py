import time
from typing import Any, Optional, Type
from fastapi import BackgroundTasks
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
import asyncio
import logging

base_url = os.getenv("BACKEND_BASE")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CryptoSetting(BaseModel):
    key: str = Field(description="Key for the encryption. The default value is 's3cr3t_k3y'")
    method: str = Field(description="Encryption method. The default value is 'AES_128'")
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
    labels: str = Field(description="Labels for the cloud source. Use the name of the cloud source if not specified")
    cryptoSetting: CryptoSetting = Field(description="Crypto setting for the cloud source. The default value is  {'key': 's3cr3t_k3y', 'method': 'AES_128'}")

async def background_task(message: str):
    # This function will be executed in the background
    await asyncio.sleep(9)
    with open("log.txt", mode="w") as email_file:
        content = f"notification: {message}"
        email_file.write(content)
        logger.info("Background task executed: %s" % message)


class CreateCloudSourceTool(BaseTool):
    name = "create_cloud_source"
    description = """Function to create a cloud source. A Cloud Source is an endpoint in the cloud taking stored video and content from outside sources. Once the cloud source is created, you can get the ingestion URL endpoint.
    In the meantime, you can get a Source Preview URL to verify that your ingested source is properly running on the cloud."""
    args_schema: Optional[Type[BaseModel]] = CloudSourceInputSchema
    background_tasks: set
    
    def _run(
        self, name: str, protocol: str, maxOutputConnections: int, redundancyMode: str, streamCount: int, labels: str, cryptoSetting: CryptoSetting
    ) -> str:
        """Use the tool."""
        url = f"{base_url}/live/v1/cloudsources"
        data = CloudSourceInputSchema(
            name= name,
            protocol= protocol,
            maxOutputConnections= maxOutputConnections,
            redundancyMode= redundancyMode,
            streamCount= streamCount,
            labels= labels,
            cryptoSetting= cryptoSetting
        )
        # Convert the dictionary to a JSON string
        dict_data = data.dict()

        message = f"Message to asd"
    
        # Enqueue the background task
        task = asyncio.create_task((background_task(message)))
        self.background_tasks.add(task)
        task.add_done_callback(self.background_tasks.discard)
        result = requests.post(url, json=dict_data)

        return result.text

    async def _arun(
        self, name: str, protocol: str, maxOutputConnections: int, redundancyMode: str, streamCount: int, labels: str, cryptoSetting: CryptoSetting
    ) -> str:
        """Use the tool."""
        url = f"{base_url}/live/v1/cloudsources"

        data = CloudSourceInputSchema(
            name= name,
            protocol= protocol,
            maxOutputConnections= maxOutputConnections,
            redundancyMode= redundancyMode,
            streamCount= streamCount,
            labels= labels,
            cryptoSetting= cryptoSetting
        )
        # Convert the dictionary to a JSON string
        dict_data = data.dict()

        message = f"Message to asd"
        # Enqueue the background task
        task = asyncio.create_task((background_task(message)))
        self.background_tasks.add(task)
        task.add_done_callback(self.background_tasks.discard)
        result = requests.post(url, json=dict_data)

        return result.text

async def async_operation():
    # Your asynchronous code here
    await asyncio.sleep(2)
    print("Async operation completed")
    return "Result from async operation"
