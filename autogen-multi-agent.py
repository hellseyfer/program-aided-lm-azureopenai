# Autogen, a cutting-edge framework for crafting multi-agent chat systems
# To accomplish tasks, Autogen provides different types of Agents, such as,
# Assistant Agent: This agent is responsible for accomplishing tasks such as coding, reviewing, etc.
# User Proxy Agent: As the name suggests, these agents act on behalf of end-users. This is responsible for bringing humans into the agent loop to guide conversations.
# Teachable Agent: This agent is configured to be highly teachable. We can feed the agent with explicit information that is absent in LLMs.
from autogen import AssistantAgent, UserProxyAgent, config_list_from_json

# Load LLM inference endpoints from an env variable or a file
# See https://microsoft.github.io/autogen/docs/FAQ#set-your-api-endpoints
# and OAI_CONFIG_LIST_sample.json
config_list = config_list_from_json(env_or_file="OAI_CONFIG_LIST")
assistant = AssistantAgent("assistant", llm_config={
                           "config_list": config_list})
user_proxy = UserProxyAgent(
    "user_proxy", code_execution_config={"work_dir": "coding"})
# prompt = Plot a chart of NVDA and TESLA stock price change YTD.
user_proxy.initiate_chat(assistant, message="")
# This initiates an automated chat between the two agents to solve the task
