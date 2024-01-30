import json
from typing import List
from langchain.tools import BaseTool
from langchain_core.pydantic_v1 import BaseModel, Field
from typing import Literal, Optional, Type
from langchain.callbacks.manager import (
    CallbackManagerForToolRun,
)

from langchain_core.agents import AgentActionMessageLog, AgentFinish
from langchain.agents import AgentExecutor

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chat_models import AzureChatOpenAI
from langchain.agents.format_scratchpad.openai_functions import (
    format_to_openai_functions
)
from langchain.agents.format_scratchpad import format_to_openai_function_messages
from dotenv import load_dotenv
load_dotenv()
from icecream import ic 
 
llm = AzureChatOpenAI(
    deployment_name="gpt-4",
    model_name="gpt-4",
)

class Response(BaseModel):
    """Final response to the question being asked"""
    answer: str = Field(description = "The final answer to respond to the user")
    formSchema: str = Field(description="schema args of the desired tool to execute")

# TOOL
class CreateCloudSourceArgs(BaseModel):
    name: str = Field(description="The name of the cloud source", input_type="text")
    protocol: Literal["RTMP", "SRT"] = Field("SRT", description="Ingest protocol")
    max_output_connections: int = Field(1, description="Number of output connections")
    redundancy_mode: Literal["NONE", "ACTIVE-ACTIVE", "ACTIVE-STANDBY"] = Field(
        "NONE", description="Redundancy mode"
    )
    stream_count: int = Field(1, description="Number of streams")

class TopicInput(BaseModel):
    topic: str = Field(description="name of the desired tool to execute")
    
class TopicDataNeededTool(BaseTool):
    name = "TopicDataNeededTool"
    description = """ 
        Tool used to display the schema of the data needed to perform the desired operation.
        it returns a schema that the front-end must use to display a form to gather the data.
        Possibles topics are: CREATE_CLOUD_SOURCE, CREATE_LIVE_EVENT.
        Depends on: None"""

    args_schema: Type[BaseModel] = TopicInput

    def _run(
        self,
        topic: str,
    ) -> str:
        """Use the tool."""
        
        operation_schema_dict = {
            "CREATE_CLOUD_SOURCE": CreateCloudSourceArgs.schema(),
            #"CREATE_LIVE_EVENT": CreateLiveEventArgs.schema(),
            #"PREVIEW_LIVE_EVENT": PreviewLiveEventArgs.schema(),
        }

        return json.dumps(
            {
                "message": f"The creation of the {topic} has started.",
                "metadata": operation_schema_dict.get(topic, None)
            }
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



def parse(output):
    #ic(output)
    # If no function was invoked, return to user
    if "function_call" not in output.additional_kwargs:
        return AgentFinish(return_values={"answer": output.content, "formSchema": ""}, log=output.content)

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
        
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful assistant"),
        ("user", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ]
)

# lc_tools = [CreateCloudSourceTool(), Response]
#oai_tools = llm.bind(functions=[format_to_openai_function_messages(t) for t in lc_tools])
llm_with_tools = llm.bind_functions([TopicDataNeededTool(), CreateCloudSourceTool(), Response])

agent = (
    {
        "input": lambda x: x["input"],
        # Format agent scratchpad from intermediate steps
        "agent_scratchpad": lambda x:  format_to_openai_function_messages(
            x["intermediate_steps"]
        ),
    }
    | prompt
    | llm_with_tools
    | parse
)

agent_executor = AgentExecutor(tools=[TopicDataNeededTool(), CreateCloudSourceTool()], agent=agent, verbose=True)

#output = agent_executor.invoke(
#    {"input": "create a cloud source, name it as juan-test and keep the rest as default"},
#    return_only_outputs=True,
#)

# print(output)
# Start the conversation loop
while True:
    user_input = input("You: ")

    # Invoke the agent with user input
    response = agent_executor.invoke({"input": user_input}, return_only_outputs=True)

    answer = response["answer"]
    formSchema = response["formSchema"]
    print("final answer: ", answer)
    print("formSchema: ", formSchema)

    # Print the agent's response
    # print("Agent:", response)

    # Check if the user wants to close the connection
    if user_input.lower() == "exit":
        break