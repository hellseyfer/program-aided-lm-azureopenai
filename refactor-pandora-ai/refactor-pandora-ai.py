# in this scenario there's a classifier chain and a branch of chains
# https://python.langchain.com/docs/expression_language/how_to/routing
from typing import Literal
from langchain.utils.openai_functions import convert_pydantic_to_openai_function
from langchain.prompts import PromptTemplate
from operator import itemgetter
from langchain.schema.output_parser import StrOutputParser
from langchain.pydantic_v1 import BaseModel, Field
from langchain.schema.runnable import RunnableBranch, RunnablePassthrough, RunnableSequence
from langchain.output_parsers.openai_functions import PydanticAttrOutputFunctionsParser
from langchain.output_parsers import PydanticOutputParser
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain.agents import AgentType, Tool, initialize_agent
from langchain.chat_models import AzureChatOpenAI
from dotenv import load_dotenv
load_dotenv()
#import langchain
#langchain.debug= True

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
    template="""Answer the user query.\n{format_instructions}\n{input}\n .
    
        Context: {context}
        
         Answer the question as accurately as you can. Don't make assumptions, ask the user for more info if needed.
         If you need to gather more info from the user, ignore the format instructions and ask the question until you get the information.""",
    input_variables=["input", "context"],
    partial_variables={
        "format_instructions": cloudsource_parser.get_format_instructions()},
)

previewliveevent_parser = PydanticOutputParser(
    pydantic_object=PreviewLiveEventSchema)

previewliveevent_prompt = PromptTemplate(
    template="""Answer the user query.\n{format_instructions}\n{input}\n .
    
        Context: {context}
        
        Answer the question as accurately as you can. Don't make assumptions, ask the user for more info if needed.
        If you need to gather more info from the user, ignore the format instructions and ask the question until you get the information.""",
    input_variables=["input", "context"],
    partial_variables={
        "format_instructions": previewliveevent_parser.get_format_instructions()},
)

general_prompt = PromptTemplate.from_template(
    "You are a helpful assistant. Answer the question as accurately as you can.\n\n{input}"
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

llm_with_binding = AzureChatOpenAI(
    deployment_name="gpt-4",
    model_name="gpt-4",
    temperature=0
).bind(
    functions=[classifier_function], function_call={"name": "TopicClassifier"}
)

parser = PydanticAttrOutputFunctionsParser(
    pydantic_schema=TopicClassifier, attr_name="topic"
)

classifier_chain = llm_with_binding | parser
memory = ConversationBufferMemory()
chatbot = ConversationChain(llm=llm_with_binding, memory=memory)

llm = AzureChatOpenAI(
    deployment_name="gpt-4",
    model_name="gpt-4",
    temperature=0
)

cloudsource_chain = cloudsource_prompt
previewliveevent_chain = previewliveevent_prompt

prompt_branch = RunnableBranch(
    (lambda x: x["topic"] == "CreateCloudSource", cloudsource_chain),
    (lambda x: x["topic"] == "PreviewLiveEvent", previewliveevent_chain),
    general_prompt,
)

final_chain = (
    RunnablePassthrough.assign(context=itemgetter("input") | chatbot)
    | RunnablePassthrough.assign(topic=itemgetter("input") | classifier_chain)
    | prompt_branch
    | llm
    | StrOutputParser()
)


# """I want to create a cloud source with name Example1 and stream count 8 and put it in the meme category. please use the max connection possible"""
# """ """
# output = final_chain.invoke(
#    {
#        "input": """ I want to see a preview of the meme event"""
#    }
# )
# print(output)


# Start the conversation loop
while True:
    human_input = input("Human: ")
    
    # Get AI response 
    ai_response = final_chain.invoke({ "input": human_input})
    print("AI: ", ai_response)

    # Save context 
    memory.save_context({"input": human_input}, {"output": ai_response})

    # Can view full context at any point
    #full_context = memory.load_memory_variables({})
    #print(full_context)
     # Check if the user wants to close the connection
    if human_input.lower() == "exit":
        break