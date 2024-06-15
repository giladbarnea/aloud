from pathlib import Path

from langchain_core.prompts import ChatPromptTemplate

from aloud.scheme import ChatPrompt

PROMPTS_MODULE_PATH = Path(__file__).parent


def get(prompt_name: str) -> ChatPromptTemplate:
    prompt = ChatPrompt(PROMPTS_MODULE_PATH / f'{prompt_name}.yaml')
    return ChatPromptTemplate.from_messages([(msg.role, msg.content) for msg in prompt.messages])
