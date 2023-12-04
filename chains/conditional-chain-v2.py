# in this scenario there's a classifier chain and a branch of prompts
from typing import Literal
from langchain.utils.openai_functions import convert_pydantic_to_openai_function
from langchain.prompts import PromptTemplate
from operator import itemgetter
from langchain.schema.output_parser import StrOutputParser
from langchain.schema.runnable import RunnableBranch
from langchain.pydantic_v1 import BaseModel, Field, Required
from langchain.schema.runnable import RunnableBranch
from langchain.schema.runnable import RunnablePassthrough
from langchain.output_parsers.openai_functions import PydanticAttrOutputFunctionsParser
from langchain.output_parsers import PydanticOutputParser
from langchain.chat_models import AzureChatOpenAI
from dotenv import load_dotenv
load_dotenv()


class CloudSourceSchema(BaseModel):
    """Function to create a cloud source. A Cloud Source is an endpoint in the cloud taking stored video and content from outside sources. Once the cloud source is created, you can get the ingestion URL endpoint.
    In the meantime, you can get a Source Preview URL to verify that your ingested source is properly running on the cloud."""
    name: str = Field(description="Cloud Source Name")
    protocol: Literal["SRT", "RTMP"]
    "Ingest protocol. The default value is 'SRT'"
    maxOutputConnections: int = Field(
        description="number of output connections", lt=1000, default=1)
    redundancyMode: Literal["NONE", "ACTIVE-ACTIVE", "ACTIVE-STANDBY"]
    "Redundancy mode. The default value is 'NONE'"
    streamCount: int = Field(
        description="Number of streams", lt=20, gt=0, default=1)


class PreviewLiveEventSchema(BaseModel):
    """This step activates the transcoding resources for your live event and lets you preview and verify the ingested source with the provided playback URLs through the user interface."""
    name: str = Field(description="PreviewLiveEvent")
    id: str = Field(description="Live event id")


cloudsource_parser = PydanticOutputParser(pydantic_object=CloudSourceSchema)

cloudsource_prompt = PromptTemplate(
    template="Answer the user query.\n{format_instructions}\n{input}\n",
    input_variables=["input"],
    partial_variables={
        "format_instructions": cloudsource_parser.get_format_instructions()},
)

previewliveevent_parser = PydanticOutputParser(
    pydantic_object=PreviewLiveEventSchema)

previewliveevent_prompt = PromptTemplate(
    template="Answer the user query.\n{format_instructions}\n{input}\n",
    input_variables=["input"],
    partial_variables={
        "format_instructions": previewliveevent_parser.get_format_instructions()},
)

general_prompt = PromptTemplate.from_template(
    "You are a helpful assistant. Answer the question as accurately as you can.\n\n{input}"
)

prompt_branch = RunnableBranch(
    (lambda x: x["topic"] == "CreateCloudSource", cloudsource_prompt),
    (lambda x: x["topic"] == "PreviewLiveEvent", previewliveevent_prompt),
    general_prompt,
)


class TopicClassifier(BaseModel):
    "Classify the topic of the user question"

    topic: Literal["CreateCloudSource",
                   "CreateLiveEvent",
                   "PreviewLiveEvent",
                   "GoLiveWithLiveEvent",
                   "ListLiveEvents"]
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

# """I want to create a cloud source with name Example1 and stream count 8 and put it in the meme category. please use the max connection possible"""
# """ """
output = final_chain.invoke(
    {
        "input": """ I want to see a preview of the meme event"""
    }
)

print(output)
