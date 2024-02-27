import asyncio
import html
import io
import os
import threading
import time
from fastapi import FastAPI

#from langchain_openai import AzureOpenAI
from openai import AzureOpenAI
from datetime import datetime
from pathlib import Path
from typing import Iterable
from openai.types import FileObject
import yfinance as yf
from openai.types.beta import Thread
from openai.types.beta.threads import Run
from openai.types.beta.threads.message_content_image_file import MessageContentImageFile
from openai.types.beta.threads.message_content_text import MessageContentText
from openai.types.beta.threads.messages import MessageFile
from PIL import Image
from pydantic import BaseModel, Field
from uuid import uuid4
from typing import Annotated, List, Literal, Optional
from typing import Dict, List
import json
from icecream import ic
from fastapi.middleware.cors import CORSMiddleware
from models.index import BodyMessage, CloudSource, LiveEvent, MessageResponse, ThreadResponse
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Load the environment variables - These are secrets.

api_endpoint = os.getenv("OPENAI_API_URL")
api_key = os.getenv("OPENAI_API_KEY")
deployment_name = os.getenv("OPENAI_DEPLOYMENT_NAME")
api_version = os.getenv("OPENAI_VERSION")

# Create an OpenAI Azure client
client = AzureOpenAI(api_key=api_key, api_version=api_version, azure_endpoint=api_endpoint)

# Mock responses
create_cloud_source_response = """
{
  "id": "6498fcb731b0e90059941dba",
  "name": "live event 1",
  "state": "Creating",
  "version": "1.21.0.0.41",
  "ingress": {
    "protocol": "SRT",
    "platform": "AZURE_VM",
    "region": "westus2",
    "url": "srt://ingress-6498fcb731b0e90059941dba.lrs-preprod.vos360.video:7086",
    "cryptoSetting": null,
    "streamCount": 0
  },
  "backupIngress": null,
  "redundancyMode": "NONE",
  "statistics": null,
  "maxOutputConnections": 9,
  "labels": []
}
"""

create_live_event_response = """
{
  "id": "34fd01fc-fee6-11ed-be56-0242ac120002",
  "name": "College Football Final 2023",
  "state": "Preview",
  "input": {
      "cloudSourceId": "6498fcb731b0e90059941dba"
  },
  "transcodingProfile": "Standard",
  "liveTranscription": {
    "enableLiveTranscription": false
  },
  "inputLossSlate": {
    "enableInputLossSlate": true,
    "imageUrl": "https://harmonicinc.box.com/s/ihapp8m4hrkpuikprxdi5x5c9081k991"
  },
  "packagingProfile": "Standard",
  "publishName": "footballlFinal2003",
  "output": [
    {
      "encryptionMethod": "Clear",
      "packageType": "cmaf-dash"
    },
    {
      "encryptionMethod": "Clear",
      "packageType": "cmaf-hls"
    }
  ], 
  "addOns": {
  }, 
  "goLiveTime": "2023-08-1T12:23:00+0000",
  "endTime": "2023-08-1T15:33:00+0000" ,
  "playbackUrls": {
    "cdnUrls": {
      "cmafDashUrl": "https://cdn-vos-ppp-01.vos360.video/Content/CMAF/Live/channel(footballlFinal2003)/master.mpd",
      "cmafHlsUrl": "https://cdn-vos-ppp-01.vos360.video/Content/CMAF/Live/channel(footballlFinal2003)/master.m3u8"
    },
    "originUrls": {
      "cmafDashUrl": "https://origin-irp-vos-ppp-01.vos360.video/Content/CMAF/Live/channel(footballlFinal2003)/master.mpd",
      "cmafHlsUrl": "https://origin-irp-vos-ppp-01.vos360.video/Content/CMAF/Live/channel(footballlFinal2003)/master.m3u8"
    }
  }
}
"""

cloudSources: List[CloudSource] = []
liveEvents: List[LiveEvent] = []
def create_cloud_source(args) -> CloudSource:
    # ic(args)
    response: CloudSource = json.loads(create_cloud_source_response)
    uuid = str(uuid4())
    response.update({"id": uuid})
    response.update({"name": args['name']})
    response.update({"ingress": {"protocol": args['protocol'], 
                                 "streamCount": args['stream_count'],
                                 "cryptoSetting": args['crypto_setting']}})
    response.update({"redundancyMode": args['redundancy_mode']})
    response.update({"maxOutputConnections": args['max_output_connections']})
    response.update({"labels": [args['labels']]})
    #response.update({"labels": args.labels})
    ic(response)
    cloudSources.append(response)

    change_cloud_source_status(response, "ONLINE")
    return response

def change_cloud_source_status(cloud_source: CloudSource, status: str):
    #await asyncio.sleep(10)
    cloud_source['state'] = status
    ic('status changed', cloud_source)

def create_live_event(args) -> LiveEvent:
    response: LiveEvent = json.loads(create_live_event_response)
    uuid = str(uuid4())
    response.update({"id": uuid})
    response.update({"name": args['name']})
    response.update({"transcodingProfile": args['transcoding_profile']})
    response.update({"input": {"cloudSourceId": args['cloud_source_id']}})
    response.update({"labels": [args['labels']]})
    ic(response)
    liveEvents.append(response)

    return response

def find_by_id_or_name(array, target):
    for obj in array:
        if obj.get("id") == target or obj.get("name") == target:
            return obj
    return None

def get_cloud_source(args) -> CloudSource:
    cloudSource: CloudSource = find_by_id_or_name(cloudSources, args['id'])
    if(cloudSource):
        return cloudSource
    else:
        return "Cloud source not found"

def list_cloud_sources() -> List[CloudSource]:
    return cloudSources

def update_live_event(args) -> LiveEvent:
    liveEvent: LiveEvent = find_by_id_or_name(liveEvents, args['id'])
    if(liveEvents):
        liveEvent.update({"name": args['name']})
        liveEvent.update({"transcodingProfile": args['transcoding_profile']})
        liveEvent.update({"input": {"cloudSourceId": args['cloud_source_id']}})
        liveEvent.update({"labels": [args['labels']]})
        liveEvent.update({"publishName": args['publish_name']})
        ic(liveEvent)

        return liveEvent
    else:
        return "Live event not found"

tools_list = [
    {"type": "code_interpreter"},
    {
        "type": "function",
        "function": {
            "name": "create_cloud_source",
            "description": "Create a cloud source with the provided configuration.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string", 
                        "description": "The name of the cloud source. Required"
                    },
                    "protocol": {
                        "type": "string",
                        "enum": ["RTMP", "SRT"],
                        "default": "SRT",
                        "description": "Ingest protocol",
                    },
                    "max_output_connections": {
                        "type": "integer",
                        "default": 1,
                        "description": "Number of output connections. Required",
                    },
                    "redundancy_mode": {
                        "type": "string",
                        "enum": ["NONE", "ACTIVE-ACTIVE", "ACTIVE-STANDBY"],
                        "default": "NONE",
                        "description": "Redundancy mode. Required",
                    },
                    "stream_count": {
                        "type": "integer",
                        "default": 1,
                        "description": "Number of streams. Required",
                    },
                    "crypto_setting": {
                        "type": "object",
                        "properties": {
                            "key": {
                                "type": "string",
                                "default": "s3cr3t_k3y",
                                "description": "The key used for encryption. Required"
                            },
                            "method": {
                                "type": "string",
                                "default": "AES_123",
                                "description": "The encryption method. Required"
                            }
                        },
                        "required": ["key", "method"],
                        "description": "Crypto settings for the cloud source. Required"
                    },
                    "labels": {
                        "type": "string", 
                        "default": "",
                        "description": "The metadata labels used to identify the cloud source. Required"
                        },
                },
                "required": ["name", "protocol", "max_output_connections", "redundancy_mode", "stream_count", "crypto_setting", "labels"],
            },
            "returns": {"type": "string", "description": "A message indicating the success or failure of the cloud source creation."},
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_live_event",
            "description": "Create a live event with the provided configuration. It requires a cloud source ID, and the state of the cloud source with that ID must be 'ONLINE'.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "The name of the live event. Required."
                    },
                    "cloud_source_id": {
                        "type": "string",
                        "description": "Id of a cloud source. Required."
                    },
                    "cloud_source_id_type": {
                        "type": "string",
                        "enum": ["OPERATION_ID", "RESOURCE_ID"],
                        "default": "RESOURCE_ID",
                        "description": "The type of the cloud source id. Should be OPERATION_ID or RESOURCE_ID."
                    },
                    "transcoding_profile": {
                        "type": "string",
                        "enum": ["STANDARD", "PREMIUM", "PASSTHROUGH"],
                        "default": "STANDARD",
                        "description": "The encoding profile of the live event."
                    },
                    "publish_name": {
                        "type": "string",
                        "description": "Name used in the URLs to identify the event. Should be unique and have no spaces or special characters. If not specified, a generated id will be used in the URL."
                    },
                    "labels": {
                        "type": "string",
                        "description": "The metadata labels used to identify the live event."
                    }
                },
                "required": ["name", "cloud_source_id", "cloud_source_id_type", "transcoding_profile", "publish_name", "labels"],
            },
            "returns": {
                "type": "string",
                "description": "A message indicating the success or failure of the live event creation."
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "update_live_event",
            "description": "Updates a live event with the provided configuration.",
            "parameters": {
                "type": "object",
                "properties": {
                    "id": {
                    "type": "string",
                    "description": "Id of the live event to update. Required."
                    },
                    "name": {
                        "type": "string",
                        "description": "The name of the live event. Required."
                    },
                    "cloud_source_id": {
                        "type": "string",
                        "description": "Id of a cloud source. Required."
                    },
                    "cloud_source_id_type": {
                        "type": "string",
                        "enum": ["OPERATION_ID", "RESOURCE_ID"],
                        "default": "RESOURCE_ID",
                        "description": "The type of the cloud source id. Should be OPERATION_ID or RESOURCE_ID."
                    },
                    "transcoding_profile": {
                        "type": "string",
                        "enum": ["STANDARD", "PREMIUM", "PASSTHROUGH"],
                        "default": "STANDARD",
                        "description": "The encoding profile of the live event."
                    },
                    "publish_name": {
                        "type": "string",
                        "description": "Name used in the URLs to identify the event. Should be unique and have no spaces or special characters. If not specified, a generated id will be used in the URL."
                    },
                    "labels": {
                        "type": "string",
                        "description": "The metadata labels used to identify the live event."
                    }
                },
                "required": ["id", "name", "cloud_source_id", "cloud_source_id_type", "transcoding_profile", "publish_name", "labels"],
                },
                "returns": {
                    "type": "string",
                    "description": "A message indicating the success or failure of the live event update."
                }      
            }
        },
    {
        "type": "function",
        "function": {
            "name": "get_cloud_source",
            "description": "Retrieves a cloud source by its id.",
            "parameters": {
                "type": "object",
                "properties": {
                    "id": {
                        "type": "string",
                        "description": "Id of the cloud source to retrieve. Required."
                    }
                },
                "required": ["id"]
            },
            "returns": {
                "type": "string",
                "description": "A message indicating the success or failure of the cloud source retrieval."
            }     
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_cloud_sources",
            "description": "Retrieves user's cloud sources.",
            "parameters": {},
            "returns": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {
                            "type": "string",
                            "description": "Id of the cloud source."
                        },
                        "name": {
                            "type": "string",
                            "description": "Name of the cloud source."
                        },
                        "protocol": {
                            "type": "string",
                            "enum": ["RTMP", "SRT"],
                            "description": "Ingest protocol of the cloud source."
                        },
                        "max_output_connections": {
                            "type": "integer",
                            "description": "Number of output connections."
                        },
                        "redundancy_mode": {
                            "type": "string",
                            "enum": ["NONE", "ACTIVE-ACTIVE", "ACTIVE-STANDBY"],
                            "description": "Redundancy mode of the cloud source."
                        },
                        "stream_count": {
                            "type": "integer",
                            "description": "Number of streams."
                        },
                        "crypto_setting": {
                            "type": "object",
                            "properties": {
                                "key": {
                                    "type": "string",
                                    "description": "The key used for encryption."
                                },
                                "method": {
                                    "type": "string",
                                    "description": "The encryption method."
                                }
                            },
                            "description": "Crypto settings of the cloud source."
                        },
                        "labels": {
                            "type": "string",
                            "description": "Metadata labels used to identify the cloud source."
                        }
                    },
                    "required": ["id", "name", "protocol", "max_output_connections", "redundancy_mode", "stream_count"]
                },
                "description": "A list of the user's cloud sources."
            }
        }
    }
]

# Create an Asssitant with the code_interpreter tool
assistant = client.beta.assistants.create(
    name="VOS.io Assistant",
    instructions="""You are a live stream services assistant. Please be polite, professional, helpful, and friendly.
         Before creations, ask the user if he wants to configure parameters.
         After the user provides you the parameters, use default values for the missing ones.
         If question is not related to the tools or you cannot answer the question, say, 'contact a representative for more assistance.'
         If the user asks for help or says 'help', provide a list of sample questions that you can answer.""",
    tools=tools_list,
    model=deployment_name
)
# Function calling
def call_functions(client: AzureOpenAI, threadId: str, run: Run) -> None:
    print("Function Calling")
    required_actions = run.required_action.submit_tool_outputs.model_dump()
    print(required_actions)
    tool_outputs = []

    for action in required_actions["tool_calls"]:
        func_name = action["function"]["name"]
        arguments = json.loads(action["function"]["arguments"])

        if func_name == "create_cloud_source":
            print("Creating cloud source...")
            output = create_cloud_source(arguments)
            tool_outputs.append({"tool_call_id": action["id"], "output": 'Cloud source created with the following details: ' + json.dumps(output)})
        elif func_name == "create_live_event":
            print("Creating live event...")
            output = create_live_event(arguments)
            tool_outputs.append({"tool_call_id": action["id"], "output": 'Live event created with the following details:' + json.dumps(output)})
        elif func_name == "list_cloud_sources":
            print("Listing cloud sources...")
            output = list_cloud_sources()
            tool_outputs.append({"tool_call_id": action["id"], "output": json.dumps(output)})
        elif func_name == "get_cloud_source":
            print("Retrieving cloud source...")
            output = get_cloud_source(arguments)
            tool_outputs.append({"tool_call_id": action["id"], "output": json.dumps(output)})
        elif func_name == "update_live_event":
            print("Updating live event...")
            output = update_live_event(arguments)
            tool_outputs.append({"tool_call_id": action["id"], "output": json.dumps(output)})
        else:
            raise ValueError(f"Unknown function: {func_name}")

    print("Submitting outputs back to the Assistant...")
    client.beta.threads.runs.submit_tool_outputs(thread_id=threadId, run_id=run.id, tool_outputs=tool_outputs)

# Format and display the Assistant messages for text and images

def read_assistant_file(file_id:str):
    response_content = client.files.content(file_id)
    return response_content.read()

# Check the status of a Run
def print_messages(messages: Iterable[MessageFile]) -> None:
    message_list = []

    # Get all the messages till the last user message
    for message in messages:
        message_list.append(message)
        if message.role == "user":
            break

    # Reverse the messages to show the last user message first
    message_list.reverse()

    # Print the user or Assistant messages or images
    for message in message_list:
        for item in message.content:
            # Determine the content type
            if isinstance(item, MessageContentText):
                print(f"{message.role}:\n{item.text.value}\n")
                file_annotations = item.text.annotations
                if file_annotations:
                    for annotation in file_annotations:
                        file_id = annotation.file_path.file_id
                        content = read_assistant_file(file_id)
                        print(f"Annotation Content:\n{str(content)}\n")
            elif isinstance(item, MessageContentImageFile):
                # Retrieve image from file id                
                data_in_bytes = read_assistant_file(item.image_file.file_id)
                # Convert bytes to image
                readable_buffer = io.BytesIO(data_in_bytes)
                image = Image.open(readable_buffer)
                # Resize image to fit in terminal
                width, height = image.size
                image = image.resize((width // 2, height // 2), Image.LANCZOS)
                # Display image
                image.show()

def process_prompt(prompt: str, threadId: str) -> None:
    client.beta.threads.messages.create(thread_id=threadId, role="user", content=prompt)
    run = client.beta.threads.runs.create(
        thread_id=threadId,
        assistant_id=assistant.id,
        instructions=f"""Please address the user as Jane Doe. If he has a typo, ask him again.
         He might already have resources created, evaluate them before performing any alteration.
         Be assertive, accurate, and polite. Ask if the user has further questions. "
         The current date and time is: 
         {datetime.now().strftime("%x %X")}
         . """,
    )
    print("processing ...")
    while True:
        run = client.beta.threads.runs.retrieve(thread_id=threadId, run_id=run.id)
        if run.status == "completed":
            # Handle completed
            messages = client.beta.threads.messages.list(limit=1, thread_id=threadId)
            #print_messages(messages)
            messages_json = json.loads(messages.model_dump_json())
            message_content = messages_json['data'][0]['content']
            text = message_content[0].get('text', {}).get('value')
            return MessageResponse(message=text)
            break
        if run.status == "failed":
            messages = client.beta.threads.messages.list(thread_id=threadId)
            answer = messages.data[0].content[0].text.value
            logger.error(f"Failed: {prompt}\nAssistant:\n{answer}\n")
            return MessageResponse(message="Sorry, I couldn't help you with that. Please try again.")
            # Handle failed
            break
        if run.status == "expired":
            # Handle expired
            print(run)
            break
        if run.status == "cancelled":
            # Handle cancelled
            print(run)
            break
        if run.status == "requires_action":
            # Handle function calling and continue processing
            call_functions(client, threadId, run)
        else:
            time.sleep(5)

#process_prompt("Based on the provided portfolio, what investments do I own?")
#process_prompt("What is the value of my portfolio?")
#user_prompt =  "Please send a report to name@contoso.com with the details for each stock based on the latest stock prices, and list the best and worst performing stocks in my portfolio."
# user_prompt = "create a live event with PREMIUM transcoding profile and juan-live publish name."
#user_prompt = "create a live event with PREMIUM transcoding profile and juan-live-2 name. use this cloudsource id: test-cloud123"

# process_prompt(user_prompt)

# while True:
#     human_input = input("Human: ")
#     process_prompt(human_input)

#     if human_input.lower() == "exit":
#         break

@app.post("/message")
async def read_root(chat: BodyMessage):
    logger.info(f"Message arrived with thread ID: {chat.thread_id}")
    return process_prompt(prompt=chat.message, threadId=chat.thread_id)

@app.post("/thread", response_model=ThreadResponse)
async def thread():
    thread = client.beta.threads.create()
    logger.info(f"Thread created with ID: {thread.id}")
    return ThreadResponse(thread_id=thread.id)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)