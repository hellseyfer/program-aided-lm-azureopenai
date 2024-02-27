from uuid import UUID
from langchain.callbacks.base import AsyncCallbackHandler, BaseCallbackHandler
import asyncio
from typing import Any, Dict, List
from langchain_core.messages import BaseMessage
from langchain_core.outputs.llm_result import LLMResult
from langchain.schema.messages import AIMessage, HumanMessage
class MyCustomAsyncHandler(AsyncCallbackHandler):
    """Async callback handler that can be used to handle callbacks from langchain."""
    def __init__(self, arg1):
        self.arg1 = arg1

    async def on_chat_model_start(self, serialized: Dict[str, Any], messages: List[List[BaseMessage]], *, run_id: UUID, parent_run_id: UUID | None = None, tags: List[str] | None = None, metadata: Dict[str, Any] | None = None, **kwargs: Any) -> Any:
        return await super().on_chat_model_start(serialized, messages, run_id=run_id, parent_run_id=parent_run_id, tags=tags, metadata=metadata, **kwargs)
    async def on_llm_start(
        self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any
    ) -> None:
        """Run when chain starts running."""
        print("zzzz....")
        await asyncio.sleep(0.3)
        class_name = serialized["name"]
        print("Hi! I just woke up. Your llm is starting")

    async def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        """Run when chain ends running."""
        # Access the custom argument (e.g., 'my_arg') from kwargs
        await asyncio.sleep(5)
        print(f"Tool is starting with custom argument: {self.arg1}")
        self.arg1.extend(
        [
            AIMessage(content="Hi! I just woke up. Your llm is ending"),
        ]
    )

