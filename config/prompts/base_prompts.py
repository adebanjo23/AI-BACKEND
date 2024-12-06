from dataclasses import dataclass
from typing import Dict


@dataclass
class PromptTemplate:
    system_prompt: str
    user_prompt_template: str

    def format_user_prompt(self, **kwargs) -> str:
        return self.user_prompt_template.format(**kwargs)


class BasePrompts:
    DEFAULT_SYSTEM_PROMPT = """You are a real-time voice assistant. 
    Respond directly to what the user just said without referencing your inability 
    to remember past conversations. Keep responses natural and relevant to the current input only."""

    DEFAULT_USER_PROMPT = "{user_input}"

    def __init__(self):
        self.current_template = PromptTemplate(
            system_prompt=self.DEFAULT_SYSTEM_PROMPT,
            user_prompt_template=self.DEFAULT_USER_PROMPT
        )

    def update_prompts(self, system_prompt: str = None, user_prompt_template: str = None):
        if system_prompt:
            self.current_template.system_prompt = system_prompt
        if user_prompt_template:
            self.current_template.user_prompt_template = user_prompt_template

    def get_formatted_prompts(self, **kwargs) -> Dict[str, str]:
        return {
            "system_prompt": self.current_template.system_prompt,
            "user_prompt": self.current_template.format_user_prompt(**kwargs)
        }