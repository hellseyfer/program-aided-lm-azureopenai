from __future__ import annotations

from typing import Any, Dict, List, Optional

from langchain.callbacks.manager import (
    AsyncCallbackManagerForChainRun,
    CallbackManagerForChainRun,
)
from langchain.chains.base import Chain
from langchain.prompts.base import BasePromptTemplate
from langchain.schema.language_model import BaseLanguageModel
from pydantic import Extra
import requests
import json
from models.createCloudSourceSchema import CloudSourceSchema
from models.createPreviewLiveEventSchema import PreviewLiveEventSchema
from models.createLiveEventSchema import CreateLiveEventSchema
from langchain.pydantic_v1 import ValidationError

class CustomRequestChain(Chain):
    """
    An example of a custom chain.
    """

    prompt: BasePromptTemplate
    """Prompt object to use."""
    
    #input_key: str = "body"
    output_key: str = "text" #: :meta private:

    class Config:
        """Configuration for this pydantic object."""

        extra = Extra.forbid
        arbitrary_types_allowed = True

    @property
    def input_keys(self) -> List[str]:
        """Will be whatever keys the prompt expects.

        :meta private:
        """
        return self.prompt.input_variables

    @property
    def output_keys(self) -> List[str]:
        """Will always return text key.

        :meta private:
        """
        return [self.output_key]


    def _call(
        self,
        inputs: Dict[str, Any],
        run_manager: Optional[CallbackManagerForChainRun] = None,
    ) -> Dict[str, str]:
        url = "http://127.0.0.1:8000/live/v1/cloudsources"
        object_instance = None
        try:
            prompt_value = self.prompt.format_prompt(**inputs)
            parsed_dict = json.loads(prompt_value.text)
            object_instance = CloudSourceSchema(**parsed_dict)
            print("Validation successful")
        except ValidationError as e:
            print("Validation failed!")
            print("Error details:", e.json())
        except json.JSONDecodeError:
            return {self.output_key: prompt_value.text}

        # Make the POST request
        response = requests.post(url, json=object_instance.json(), timeout=3000)

        # Check the response
        if response.status_code == 200:
            print("POST request <create cloudsource> successful")
            response = createLiveEventRequest(response.json())
            return {self.output_key: 'event successfully created' }
        else:
            print("POST request <create cloudsource> failed")

        return {self.output_key: "the task could not be processed, please try again"}



    async def _acall(
        self,
        inputs: Dict[str, Any],
        run_manager: Optional[AsyncCallbackManagerForChainRun] = None,
    ) -> Dict[str, str]:
        # Your custom chain logic goes here
        # This is just an example that mimics LLMChain
        prompt_value = self.prompt.format_prompt(**inputs)

        # Whenever you call a language model, or another chain, you should pass
        # a callback manager to it. This allows the inner run to be tracked by
        # any callbacks that are registered on the outer run.
        # You can always obtain a callback manager for this by calling
        # `run_manager.get_child()` as shown below.
        response = await self.llm.agenerate_prompt(
            [prompt_value], callbacks=run_manager.get_child() if run_manager else None
        )

        # If you want to log something about this run, you can do so by calling
        # methods on the `run_manager`, as shown below. This will trigger any
        # callbacks that are registered for that event.
        if run_manager:
            await run_manager.on_text("Log something about this run")

        return {self.output_key: response.generations[0][0].text}

    @property
    def _chain_type(self) -> str:
        return "my_custom_chain"


def createLiveEventRequest(data):
    url = 'http://127.0.0.1:8000/live/v1/events'

    response = requests.post(url, json=data, timeout=3)
    return response
