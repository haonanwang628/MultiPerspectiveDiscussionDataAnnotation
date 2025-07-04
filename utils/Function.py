import tiktoken
import os
import json
import argparse
import pandas as pd
from openpyxl import load_workbook, Workbook
from openpyxl.styles import Alignment
import os

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


# string tokens
def num_tokens_from_string(string: str, model_name: str) -> int:
    encoding_name = MODEL_TOKENIZER_MAP.get(model_name, "cl100k_base")
    encoding = tiktoken.get_encoding(encoding_name)
    return len(encoding.encode(string))

# open json file
def import_json(file: str):
    with open(file, "r", encoding="utf-8") as f:
        return json.load(f)

# save codebook to excel
def save_excel(file_path, target_text, codebook):
    if os.path.exists(file_path):
        wb = load_workbook(file_path)
        ws = wb.active
        last_row = ws.max_row
    else:
        wb = Workbook()
        ws = wb.active
        ws.append(["target_text", "code", "evidence"])
        last_row = 1

    start_row = last_row + 1
    end_row = start_row + len(codebook) - 1
    merge_range = f"A{start_row}:A{end_row}"

    # load target text
    ws.merge_cells(merge_range)
    ws[f"A{start_row}"] = target_text
    ws[f"A{start_row}"].alignment = Alignment(vertical="center", horizontal="center", wrap_text=True)

    # load code and justification
    for idx, item in enumerate(codebook, start=start_row):
        ws.cell(row=idx, column=2, value=item["code"])  # B列：code
        ws.cell(row=idx, column=3, value=item["evidence"])  # C列：justification

    # adjust column wide
    ws.column_dimensions['A'].width = 50
    ws.column_dimensions['B'].width = 25
    ws.column_dimensions['C'].width = 80

    # save file
    wb.save(file_path)
    print(f"Current Final Codebook has been saved {file_path}")


# parser control
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
