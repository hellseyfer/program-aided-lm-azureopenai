import asyncio
import json
from typing import List
from langchain.tools import BaseTool
from langchain.pydantic_v1 import BaseModel, Field
from typing import Literal, Optional, Type
from langchain.callbacks.manager import (
    CallbackManagerForToolRun,
)

from langchain_core.agents import AgentActionMessageLog, AgentFinish
from langchain.agents import AgentExecutor

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import AzureChatOpenAI

from langchain.agents.format_scratchpad import format_to_openai_function_messages
from dotenv import load_dotenv
load_dotenv()
from icecream import ic 
from langchain.memory import ChatMessageHistory
import os

api_endpoint = os.getenv("OPENAI_API_BASE")
api_key = os.getenv("OPENAI_API_KEY")
deployment_name = os.getenv("OPENAI_DEPLOYMENT_NAME")
api_version = os.getenv("OPENAI_VERSION")

llm = AzureChatOpenAI(
    api_key=api_key, api_version=api_version, azure_endpoint=api_endpoint
)

# TOOL
class CreateCloudSourceArgs(BaseModel):
    name: str = Field(description="The name of the cloud source. Required")
    protocol: Literal["RTMP", "SRT"] = Field("SRT", description="Ingest protocol")
    max_output_connections: int = Field(1, description="Number of output connections")
    redundancy_mode: Literal["NONE", "ACTIVE-ACTIVE", "ACTIVE-STANDBY"] = Field(
        "NONE", description="Redundancy mode"
    )
    stream_count: int = Field(1, description="Number of streams")

class CreateLiveEventArgs(BaseModel):
    name: str = Field(description="The name of the live event. Required.")
    cloud_source_id: str = Field(
        description="The id of the cloud source rqquired by the live event. Required."
    )
    cloud_source_id_type: Literal["OPERATION_ID", "RESOURCE_ID"] = Field(
        "RESOURCE_ID",
        description="""The type of the cloud source id. 
        OPERATION_ID if the user asked for the creation of a new cloud source and the 
        cloud source still doesn't exist. 
        RESOURCE_ID if the user provided the id of an existing cloud source.
        """,
    )
    transcoding_profile: str = Field(
        "my_profile", description="The encoding profile of the live event"
    )
    publish_name: str = Field(
        "publish_name",
        description="Name used in the URLs to identify the event. This needs to be unique and no space and special characters. If not specified, generated id will be used in URL.",
    )

class CreateCloudSourceTool(BaseTool):
    name = "CreateCloudSource"
    description = """ 
        Tool used to create a cloud source to ingest the live stream. The output can
        be used by live events.
        Depends on: TopicDataNeededTool"""

    args_schema: Optional[Type[CreateCloudSourceArgs]] = CreateCloudSourceArgs

    def _run(
        self,
        name: str,
        protocol: Literal["RTMP", "SRT"] = "SRT",
        max_output_connections: int = 1,
        redundancy_mode: Literal["NONE", "ACTIVE-ACTIVE", "ACTIVE-STANDBY"] = "NONE",
        stream_count: int = 1,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool."""

        return json.dumps(
            {
                "message": f"The creation of the cloud source has started."
            }
        )

class CreateLiveEventTool(BaseTool):
    name = "CreateLiveEvent"
    description = """
        tool used to create a live event. It depends on a cloud source to setup the live
        event. When the Live Event is created, it stays in an offline state (it is not live yet) and also provides the user with the preview URL.
        """

    args_schema: Optional[Type[CreateLiveEventArgs]] = CreateLiveEventArgs

    def _run(
        self,
        name: str,
        cloud_source_id: str,
        cloud_source_id_type: Literal["OPERATION_ID", "RESOURCE_ID"] = "RESOURCE_ID",
        transcoding_profile: str = "my_profile",
        publish_name: str = "publish_name",
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool."""

        return json.dumps(
            {
                "message": f"The creation of the live event has started."
            }
        )

def parse(output):
    #ic(output)
    # If no function was invoked, return to user
    if "function_call" not in output.additional_kwargs:
        return AgentFinish(return_values={"answer": output.content}, log=output.content)

    # Parse out the function call
    function_call = output.additional_kwargs["function_call"]
    name = function_call["name"]
    inputs = json.loads(function_call["arguments"])

    # If the Response function was invoked, return to the user with the function inputs
    if name == "Response":
        return AgentFinish(return_values=inputs, log=str(function_call))
    # Otherwise, return an agent action
    else:
        return AgentActionMessageLog(
            tool=name, tool_input=inputs, log="", message_log=[output]
        )

default_prompt = """"You are a helpful assistant. If you don't know the answer, just say so."
                    You don't know anything about: create cloud source, creat live events, etc.."""

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", default_prompt),
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ]
)

llm_with_tools = llm.bind_functions([CreateCloudSourceTool(), CreateLiveEventTool()])

memory = ChatMessageHistory()
agent = (
    {
        "chat_history": lambda x: x["chat_history"],
        "input": lambda x: x["input"],
        # Format agent scratchpad from intermediate steps
        "agent_scratchpad": lambda x:  format_to_openai_function_messages(
            x["intermediate_steps"]
        )
    }
    | prompt
    | llm_with_tools.with_config({"tags": ["agent_llm"]})
    | parse
)

agent_executor = AgentExecutor(tools=[CreateCloudSourceTool(), CreateLiveEventTool()], agent=agent, verbose=True).with_config(
    {"run_name": "Agent"}
)

async def print_events(agent_exec, query, chat_history):
    async for event in agent_exec.astream_events(
        {"input": query, "chat_history": chat_history},
        version="v1",
    ):
        kind = event["event"]
        if kind == "on_chain_start":
            if (
                event["name"] == "Agent"
            ):  # Was assigned when creating the agent with `.with_config({"run_name": "Agent"})`
                # print(
                #     f"Starting agent: {event['name']} with input: {event['data'].get('input')}"
                # )
                pass
        elif kind == "on_chain_end":
            if (
                event["name"] == "Agent"
            ):  # Was assigned when creating the agent with `.with_config({"run_name": "Agent"})`
                # print()
                # print("--")
                # print(
                #     f"Done agent: {event['name']} with output: {event['data'].get('output')['answer']}"
                # )
                # print(
                #     f"formSchema: {event['data'].get('output')['formSchema']}"
                # )
                #return event["data"].get("output")
                pass
        if kind == "on_chat_model_stream":
            content = event["data"]["chunk"].content
            if content:
                # Empty content in the context of OpenAI means
                # that the model is asking for a tool to be invoked.
                # So we only print non-empty content
                print(content, end="|")
                yield f"{content}"
        elif kind == "on_tool_start":
            print("--")
            print(
                f"Starting tool: {event['name']} with inputs: {event['data'].get('input')}"
            )
        elif kind == "on_tool_end":
            print(f"Done tool: {event['name']}")
            print(f"Tool output was: {event['data'].get('output')}")
            print("--")

#output = agent_executor.invoke(
#    {"input": "create a cloud source, name it as juan-test and keep the rest as default"},
#    return_only_outputs=True,
#)

# print(output)
# Start the conversation loop
# async def main():
#     while True:
#         user_input = input("You: ")

#         # Invoke the agent with user input
#         memory.add_user_message(user_input)
#         response = await print_events(agent_executor, user_input, memory.messages)

#         memory.add_ai_message(response["answer"])
#         # Check if the user wants to close the connection
#         if user_input.lower() == "exit":
#             break

# asyncio.run(main())