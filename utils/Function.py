import tiktoken
import os
import json
import argparse

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


def import_json(file: str):
    with open(file, "r", encoding="utf-8") as f:
        return json.load(f)


def to_json(string: str):
    return json.loads(eval(string.replace('```', "'''").replace('json', '').replace('\n', '')))


def parse_args():
    parser = argparse.ArgumentParser("", formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument("-i", "--input-file", type=str,
                        default=r"F:\Work\Debate\MultiAgentDabateDataAnnotation\Data\processed\Scrum-interviews\First "
                                r"Cycle - RQ1.json",
                        help="raw_text Input file path")
    parser.add_argument("-o", "--output-dir", type=str,
                        default=r"F:\Work\Debate\MultiAgentDabateDataAnnotation\Data\output",
                        help="Output file dir")
    parser.add_argument("-c", "--config-dir", type=str,
                        default=r"F:\Work\Debate\MultiAgentDabateDataAnnotation\config",
                        help="config file dir")
    parser.add_argument("-k", "--api-key", type=str, default="sk-9bc06d1289704b05b7b52db5285dba67",
                        help="OpenAI api key")
    parser.add_argument("-b", "--base-url", type=str, default="https://api.deepseek.com/v1",
                        help="base URL for non-OpenAI models")
    parser.add_argument("-m", "--model-name", type=str, default="deepseek-chat", help="Model name")
    parser.add_argument("-t", "--temperature", type=float, default=0, help="Sampling temperature")

    return parser.parse_args()
