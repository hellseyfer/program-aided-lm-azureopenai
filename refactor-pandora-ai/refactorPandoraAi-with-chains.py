# in this scenario there's a classifier chain and a branch of chains
# https://python.langchain.com/docs/expression_language/how_to/routing
from typing import Literal
from langchain.utils.openai_functions import convert_pydantic_to_openai_function
from langchain.prompts import PromptTemplate
from operator import itemgetter
from langchain.schema.output_parser import StrOutputParser
from langchain.schema.runnable import RunnableBranch, RunnablePassthrough,  RunnableLambda
from langchain.output_parsers.openai_functions import PydanticAttrOutputFunctionsParser
from langchain.output_parsers import PydanticOutputParser
from langchain.chains import ConversationChain
from langchain.memory import ConversationSummaryMemory, ConversationBufferMemory
from uuid import uuid4
from models.createCloudSourceSchema import CloudSourceSchema
from models.createPreviewLiveEventSchema import PreviewLiveEventSchema
from models.topicClassifierSchema import TopicClassifier
from customRequestChain import CustomRequestChain
from langchain.chat_models import AzureChatOpenAI
from dotenv import load_dotenv
load_dotenv()
# import langchain
# langchain.debug= True

cloudsource_parser = PydanticOutputParser(pydantic_object=CloudSourceSchema)

cloudsource_prompt = PromptTemplate(
    template="""Answer the user query.\n{format_instructions}\n{input}\n .

         Answer the question as accurately as you can.
         If you need to gather more info from the user, ignore the format instructions and ask questions until you get the information.""",
    input_variables=["input"],
    partial_variables={
        "format_instructions": cloudsource_parser.get_format_instructions()},
)

previewliveevent_parser = PydanticOutputParser(
    pydantic_object=PreviewLiveEventSchema)

previewliveevent_prompt = PromptTemplate(
    template="""Answer the user query.\n{format_instructions}\n{input}\n .
        
        Answer the question as accurately as you can.
        If you need to gather more info from the user, ignore the format instructions and ask questions until you get the information needed.""",
    input_variables=["input"],
    partial_variables={
        "format_instructions": previewliveevent_parser.get_format_instructions()},
)

general_prompt = PromptTemplate.from_template(
    # "You are a helpful assistant. Answer the question as accurately as you can.\n\n{input}"
    """You are a helpful assistant. Kindly ask the user to try again since we couldn't recognize his intent or topic.
    If needed, feel free to help the user with the following topics: 'CreateCloudSource', 'CreateLiveEvent', 'GoLiveWithLiveEvent', 'PreviewLiveEvent' or 'ListLiveEvents'"""
)


classifier_function = convert_pydantic_to_openai_function(TopicClassifier)

llm_with_binding = AzureChatOpenAI(
    deployment_name="gpt-4",
    model_name="gpt-4",
    temperature=0.3,
).bind(
    functions=[classifier_function], function_call={"name": "TopicClassifier"}
)

llm = AzureChatOpenAI(
    deployment_name="gpt-4",
    model_name="gpt-4",
    temperature=0.3
)

parser = PydanticAttrOutputFunctionsParser(
    pydantic_schema=TopicClassifier, attr_name="topic"
)

classifier_chain = llm_with_binding | parser

# memory = ConversationSummaryMemory(llm=llm, return_messages=True)
memory = ConversationBufferMemory(return_messages=True)

chatbot = ConversationChain(
    llm=llm_with_binding,
    memory=memory,
    verbose=True)

chain_request = CustomRequestChain(
    prompt=PromptTemplate.from_template("{body}")
)

cloudsource_chain = cloudsource_prompt
previewliveevent_chain = previewliveevent_prompt

def text_parser(text: str):
    """Returns the output text with no changes."""
    return text.get('text') or text.get('body')

parsedText = RunnableLambda(text_parser)

prompt_branch = RunnableBranch(
    (lambda x: x["topic"] == "CreateCloudSource",
     cloudsource_chain | llm | StrOutputParser() | chain_request | parsedText),
    (lambda x: x["topic"] == "PreviewLiveEvent", previewliveevent_chain | llm | StrOutputParser()),
    general_prompt,
)

final_chain = (
    RunnablePassthrough.assign(topic=itemgetter("input") | classifier_chain)
    | prompt_branch
)


# """I want to create a cloud source with name Example1 and stream count 8 and put it in the meme category. max connections of 800 and the rest of the values as default"""
# """ I want to see a preview of the meme event"""


# Start the conversation loop
while True:
    human_input = input("Human: ")

    if human_input.lower() == "exit":
        break

    # Get AI response
    chatbot.predict(input=human_input)
    output = chatbot.memory.buffer
    print("output chat: ", output)
    ai_response = final_chain.invoke({"input": output})
    print("AI: ", ai_response)

    # Save context
    # memory.save_context({"input": human_input}, {"output": ai_response})

    # Can view full context at any point
    # full_context = memory.load_memory_variables({})
    # print(full_context)
    # Check if the user wants to close the connection
