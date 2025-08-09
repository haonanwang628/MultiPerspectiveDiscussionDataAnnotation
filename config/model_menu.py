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
