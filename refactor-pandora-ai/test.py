from langchain.chains import SimpleSequentialChain, ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain.schema import StrOutputParser
from langchain.schema.runnable import RunnablePassthrough
from langchain.chat_models import AzureChatOpenAI
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
load_dotenv()

llm = AzureChatOpenAI(
    deployment_name="gpt-4",
    model_name="gpt-4",
    temperature=0
)

conversation = ConversationChain(
    llm=llm, memory=ConversationBufferMemory(), verbose=True)

synopsis_prompt = PromptTemplate.from_template(
    """ Generate a synopsis given the title: {title}"""
)
synopsis_chain = synopsis_prompt | llm | StrOutputParser()

review_prompt = PromptTemplate.from_template(
    """ Generate a review given the synopsis: {synopsis}"""
)
review_chain = review_prompt | llm | StrOutputParser()

classifier_prompt = PromptTemplate.from_template(
    """The user wants me to generate a {input}"""
)
classifier = classifier_prompt | llm | StrOutputParser()

combined_chain = (
    {"title": conversation}
    | RunnablePassthrough.assign(synopsis=synopsis_chain)
    | RunnablePassthrough.assign(review=review_chain)
)

output = combined_chain.invoke(
    {"input": "I want to generate a synopsis of saw x movie"})
print(output)
