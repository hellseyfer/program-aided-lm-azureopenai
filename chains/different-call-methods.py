from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

from langchain.chat_models import AzureChatOpenAI
from dotenv import load_dotenv
load_dotenv()

llm = AzureChatOpenAI(
    deployment_name="gpt35-16k",
    model_name="gpt-35-turbo-16k",
    temperature=0
)

prompt_template = "Tell me a {adjective} joke"
llm_chain = LLMChain(llm=llm, prompt=PromptTemplate.from_template(prompt_template))

# By default, __call__ returns both the input and output key values
#output = llm_chain(inputs={"adjective": "corny"})
#print(output)


# You can configure it to only return output key values by setting return_only_outputs to True.
#output = llm_chain("corny", return_only_outputs=True)
#print(output)

# If the Chain only outputs one output key (i.e. only has one element in its output_keys), you can use run method.
# Note that run outputs a string instead of a dictionary.
#llm_chain.output_keys   #  ['text']

output = llm_chain.run({"adjective": "corny"})
print(output)

# These two are equivalent
#llm_chain.run({"adjective": "corny"})
#llm_chain.run("corny")

# These two are also equivalent
#llm_chain("corny")
#llm_chain({"adjective": "corny"})