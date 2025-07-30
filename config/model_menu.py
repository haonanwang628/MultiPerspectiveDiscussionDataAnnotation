# model menu
MODEL_TOKENIZER_MAP = {
    "deepseek-chat": "cl100k_base",
    "deepseek-reasoner": "cl100k_base",
}

llm_MaxToken = {
    "deepseek-chat": 8000,
    "deepseek-reasoner": 8000,
    "gpt-4o-mini-2024-07-18": 10000
}

available_models = ["deepseek-chat", "GPT-3.5", "gpt-4o-mini-2024-07-18", "Claude"]

api_key = {
    "GPT-3.5": "sk-xxx",
    "gpt-4o-mini-2024-07-18": "",
    "deepseek-chat": "sk-9bc06d1289704b05b7b52db5285dba67",
    "Claude": "sk-xxx"
}

base_url = {
    "GPT-3.5": "",
    "gpt-4o-mini-2024-07-18": "",
    "deepseek-chat": "https://api.deepseek.com/v1",
    "Claude": "https://api.anthropic.com"
}
