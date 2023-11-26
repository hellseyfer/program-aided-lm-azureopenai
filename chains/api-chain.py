# let's search through https://techdocs.akamai.com/iam-api/reference/apifrom dotenv import load_dotenv
from langchain.chat_models import AzureChatOpenAI
from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain, APIChain
from langchain.callbacks.manager import get_openai_callback

load_dotenv()

llm = AzureChatOpenAI(
    deployment_name="gpt-4",
    model_name="gpt-4",
    temperature=0
)


prompt = PromptTemplate(
    input_variables=["api_url"],
    template="""Act as a technical writer. Write detailed documentation for the API that exists at {api_url}. Only detail the request, do not describe the response. Do not include any parameters not in the sample endpoint."""
)

chain = LLMChain(
    llm=llm,
    verbose=True,
    prompt=prompt
)

implicit_docs = """
Pitchfork has an API with a sample endpoint at https://pitchfork.com/api/v2/search/?genre=experimental&genre=global&genre=jazz&genre=metal&genre=pop&genre=rap&genre=rock&types=reviews&sort=publishdate%20desc%2Cposition%20asc&size=5&start=0&rating_from=0.0
"""

implicit_chain = APIChain.from_llm_and_api_docs(llm, implicit_docs, verbose=True, limit_to_domains=["https://pitchfork.com"],)

#implicit_chain.run("What was the first rap album reviewed by pitchfork?")
#implicit_chain.run("What was the last rnb album reviewed by pitchfork?")

with get_openai_callback() as cb:
    response = implicit_chain.run("What was the last jazz album reviewed by pitchfork?")
    print(f"Response: {response}")
    print(f"Total Tokens: {cb.total_tokens}")
    print(f"Prompt Tokens: {cb.prompt_tokens}")
    print(f"Completion Tokens: {cb.completion_tokens}")
    print(f"Total Cost (USD): ${cb.total_cost}")