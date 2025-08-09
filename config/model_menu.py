# model menu
MODEL_TOKENIZER_MAP = {
    "deepseek-chat": "cl100k_base",
    "deepseek-reasoner": "cl100k_base",
}

llm_MaxToken = {
    "deepseek-chat": 8000,
    "deepseek-reasoner": 8000,
    "gpt-4o-mini": 10000
}

available_models = ["deepseek-chat", "GPT-3.5", "gpt-4o-mini", "Claude"]
import os

api_key = {
    "GPT-3.5": "sk-xxx",
    "gpt-4o-mini": os.getenv("OPENAI_API_KEY"),
    "deepseek-chat": os.getenv("DEEPSEEK_API_KEY"),
    "Claude": "sk-xxx"
}

base_url = {
    "GPT-3.5": "",
    "gpt-4o-mini": "",
    "deepseek-chat": "https://api.deepseek.com/v1",
    "Claude": "https://api.anthropic.com"
}

