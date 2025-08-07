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
