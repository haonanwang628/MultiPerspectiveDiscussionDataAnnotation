import tiktoken
import os
import json

# 自定义模型-tokenizer 映射表
MODEL_TOKENIZER_MAP = {
    "deepseek-chat": "cl100k_base",
    "deepseek-reasoner": "cl100k_base",
    # 可继续添加更多模型映射
}

llm_MaxToken = {
    "gpt-4": 7900,
    "gpt-4-0314": 7900,
    "gpt-3.5-turbo-0301": 3900,
    "gpt-3.5-turbo": 3900,
    "text-davinci-003": 4096,
    "text-davinci-002": 4096,
    "deepseek-chat": 8000,
}

def num_tokens_from_string(string: str, model_name: str) -> int:
    encoding_name = MODEL_TOKENIZER_MAP.get(model_name, "cl100k_base")
    encoding = tiktoken.get_encoding(encoding_name)
    return len(encoding.encode(string))

def get_json(string: str):
    return json.loads(eval(string.replace('```', "'''").replace('json', '').replace('\n', '')))
