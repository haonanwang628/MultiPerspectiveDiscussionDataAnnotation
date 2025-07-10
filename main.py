# 待定
import json
import os
import argparse
from utils import Agent_debate
from utils.Function import *


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
    parser.add_argument("-m", "--model-name", type=str, default="deepseek-chat", help="Model name")
    parser.add_argument("-t", "--temperature", type=float, default=0, help="Sampling temperature")

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    texts = import_json(args.input_file)
    debate_config = import_json(os.path.join(args.config_dir, "debate_config.json"))

    codebook_dir = os.path.join(args.output_dir, "Scrum-interviews-Codebook")
