# using LCEL, Creating a sequence of calls (to LLMs or any other component/arbitrary function) is precisely what LangChain Expression Language was designed for.
# As a toy example, let's suppose we want to create a chain that first creates a play synopsis and then generates a play review based on the synopsis.
# import langchain
# langchain.debug = True
from langchain.chat_models import AzureChatOpenAI
from langchain.schema import StrOutputParser
from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
from langchain.schema.runnable import RunnablePassthrough

load_dotenv()

llm = AzureChatOpenAI(
    deployment_name="gpt-4",
    model_name="gpt-4",
    temperature=0
)

synopsis_prompt = PromptTemplate.from_template(
    """You are a playwright. Given the title of play, it is your job to write a synopsis for that title.

Title: {title}
Playwright: This is a synopsis for the above play:"""
)

review_prompt = PromptTemplate.from_template(
    """You are a play critic from the New York Times. Given the synopsis of play, it is your job to write a review for that play.

Play Synopsis:
{synopsis}
Review from a New York Times play critic of the above play:"""
)

summary_prompt = PromptTemplate.from_template(
    """You are a play summarizer for the lazy people. Given the review of play, it is you job to write a summary for that review,
    and to give stars (from 1 to 5) based on that review at the end of your response.
    
    Play Critic:
    {review}
    This is a summary of the above play:"""
)

synopsis_chain = synopsis_prompt | llm | StrOutputParser()
review_chain = review_prompt | llm | StrOutputParser()
summary_chain = summary_prompt | llm | StrOutputParser()
runnable_sequence = (
    {"synopsis": synopsis_chain}
    | RunnablePassthrough.assign(review=review_chain)
    | RunnablePassthrough.assign(summary=summary_chain)
)
output = runnable_sequence.invoke({"title": "Tragedy at sunset on the beach"})
print(output)
