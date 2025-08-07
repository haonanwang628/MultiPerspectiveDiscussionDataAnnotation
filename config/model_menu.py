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

api_key = {
    "GPT-3.5": "sk-xxx",
    "gpt-4o-mini":"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",
    "deepseek-chat": "sk-9bc06d1289704b05b7b52db5285dba67",
    "Claude": "sk-xxx"
}

base_url = {
    "GPT-3.5": "",
    "gpt-4o-mini": "",
    "deepseek-chat": "https://api.deepseek.com/v1",
    "Claude": "https://api.anthropic.com"
}
