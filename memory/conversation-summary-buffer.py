# ConversationSummaryBufferMemory combines the two ideas. It keeps a buffer of recent interactions in memory, 
# but rather than just completely flushing old interactions it compiles them into a summary and uses both. 
# It uses token length rather than number of interactions to determine when to flush interactions.

from langchain.chains import ConversationChain
from langchain.memory import ConversationSummaryBufferMemory
from langchain.chat_models import AzureChatOpenAI
from dotenv import load_dotenv
load_dotenv()

llm = AzureChatOpenAI(
    deployment_name="gpt-4",
    model_name="gpt-4",
    temperature=0
)

conversation_with_summary = ConversationChain(
    llm=llm,
    # We set a very low max_token_limit for the purposes of testing.
    memory=ConversationSummaryBufferMemory(llm=llm, max_token_limit=40),
    verbose=True,
)
print(conversation_with_summary.predict(input="Hi, what's up?"))


print(conversation_with_summary.predict(input="Just working on writing some documentation!"))

# We can see here that there is a summary of the conversation and then some previous interactions
print(conversation_with_summary.predict(input="For LangChain! Have you heard of it?"))

# We can see here that the buffer is updated
print(conversation_with_summary.predict(
    input="It is a decentralized language-learning platform that connects native speakers and learners in real time."
))

print(conversation_with_summary.predict(
    input="can we use langchain to improve blockchain features?"
))