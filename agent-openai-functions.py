from langchain.agents import AgentType, Tool, initialize_agent
from langchain.chains import LLMMathChain
from langchain.chat_models import ChatOpenAI
from langchain.utilities import google_serper
from langchain.sql_database import SQLDatabase
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from dotenv import load_dotenv
from langchain.chat_models import AzureChatOpenAI
from langchain_experimental.sql import SQLDatabaseChain

load_dotenv()

llm = AzureChatOpenAI(
    deployment_name="gpt-4",
    model_name="gpt-4",
    temperature=0
)

search = google_serper.GoogleSerperAPIWrapper()
llm_math_chain = LLMMathChain.from_llm(llm=llm, verbose=True)
db_path = "Chinook.db"

db = SQLDatabase.from_uri(f"sqlite:///{db_path}")
#toolkit = SQLDatabaseToolkit(db=db, llm=llm)
db_chain = SQLDatabaseChain.from_llm(llm, db, verbose=True)

tools = [
    Tool(
        name="Search",
        func=search.run,
        description="useful for when you need to answer questions about current events. You should ask targeted questions",
    ),
    Tool(
        name="Calculator",
        func=llm_math_chain.run,
        description="useful for when you need to answer questions about math",
    ),
    Tool(
        name="ChinookDB",
        func=db_chain.run,
        description="useful for when you need to answer questions about Chinook.db. Input should be in the form of a question containing full context",
    ),
]

agent_executor = initialize_agent(
    tools, llm, agent=AgentType.OPENAI_FUNCTIONS, verbose=True
)

agent_executor.invoke(
    {
        "input": "Who is Leo DiCaprio's girlfriend? What is her current age raised to the 0.43 power? Can you check what tables the db has?, Can you provide me at least 10 Artists names?"
    }
)