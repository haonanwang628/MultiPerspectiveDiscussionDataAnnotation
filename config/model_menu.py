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
    "gpt-4o-mini-2024-07-18": "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",
    "deepseek-chat": "sk-9bc06d1289704b05b7b52db5285dba67",
    "Claude": "sk-xxx"
}

base_url = {
    "GPT-3.5": "",
    "gpt-4o-mini-2024-07-18": "",
    "deepseek-chat": "https://api.deepseek.com/v1",
    "Claude": "https://api.anthropic.com"
}
