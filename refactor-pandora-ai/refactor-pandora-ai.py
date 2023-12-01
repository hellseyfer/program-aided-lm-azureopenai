from typing import Literal
from langchain.utils.openai_functions import convert_pydantic_to_openai_function
from langchain.prompts import PromptTemplate
from operator import itemgetter
from langchain.schema.output_parser import StrOutputParser
from langchain.schema.runnable import RunnableBranch
from langchain.pydantic_v1 import BaseModel, Field
from langchain.schema.runnable import RunnableBranch
from langchain.schema.runnable import RunnablePassthrough
from langchain.output_parsers.openai_functions import PydanticAttrOutputFunctionsParser
from langchain.chat_models import AzureChatOpenAI
from dotenv import load_dotenv
load_dotenv()

class CloudSourceInput(BaseModel):
    """Function to create a cloud source. A Cloud Source is an endpoint in the cloud taking stored video and content from outside sources. Once the cloud source is created, you can get the ingestion URL endpoint.
    In the meantime, you can get a Source Preview URL to verify that your ingested source is properly running on the cloud."""
    name: str = Field(description="Cloud Source Name")
    protocol: Literal["RTMP", "SRT"]
    "Ingest protocol"
    maxOutputConnections: int = Field(description="number of output connections", default=1)
    redundancyMode: Literal["NONE", "ACTIVE-ACTIVE", "ACTIVE-STANDBY"]
    "Redundancy mode"
    streamCount: int = Field(description="Number of streams", lt=20, gt=0, default=1)

general_prompt = PromptTemplate.from_template(
    "You are a helpful assistant. Answer the question as accurately as you can.\n\n{input}"
)
prompt_branch = RunnableBranch(
    (lambda x: x["topic"] == "CreateCloudSource", CloudSourceInput),
    #(lambda x: x["topic"] == "PreviewLiveEvent", physics_prompt),
    general_prompt,
)

class TopicClassifier(BaseModel):
    "Classify the topic of the user question"

    topic: Literal["CreateCloudSource",
                   "CreateLiveEvent", 
                   "PreviewLiveEvent", 
                   "GoLiveWithLiveEvent", 
                   "ListLiveEvents" ]
    """The topic of the user question. One of 
    'CreateCloudSource', 'CreateLiveEvent', 'GoLiveWithLiveEvent', 'PreviewLiveEvent' or 'ListLiveEvents'."""


classifier_function = convert_pydantic_to_openai_function(TopicClassifier)

llm = AzureChatOpenAI(
    deployment_name="gpt35-16k",
    model_name="gpt-35-turbo-16k",
    temperature=0
).bind(
    functions=[classifier_function], function_call={"name": "TopicClassifier"}
)

parser = PydanticAttrOutputFunctionsParser(
    pydantic_schema=TopicClassifier, attr_name="topic"
)

classifier_chain = llm | parser

llm = AzureChatOpenAI(
    deployment_name="gpt-4",
    model_name="gpt-4",
    temperature=0
)

final_chain = (
    RunnablePassthrough.assign(topic=itemgetter("input") | classifier_chain)
    | prompt_branch
    | llm
    | StrOutputParser()
)

output = final_chain.invoke(
    {
        "input": "I want to create a cloud source with name Example1 and stream count 8"
    }
)

print(output)