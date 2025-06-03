import json
import os
import argparse
from utils.Agent import Agent
from utils.Function import *
import Agents

if __name__ == "__main__":
    args = parse_args()

    texts = import_json(args.input_file)
    role_config = import_json(os.path.join(args.config_dir, "role_config.json"))
    agree_config = import_json(os.path.join(args.config_dir, "agree_config.json"))
    for i, text in enumerate(texts):
        if i == 1:
            break
        role_config["target_text"] = text["data_chunk"]
        agree_config["target_text"] = text["data_chunk"]
        roles = Agents.RoleAgent(model_name=args.model_name,
                                  temperature=args.temperature,
                                  config=role_config,
                                  output=args.output_dir,
                                  api_key=args.api_key,
                                  sleep_time=0,
                                  base_url=args.base_url)
        agree_config["Annotators"] = roles.Annotators_str
        agree = Agents.AgreeAgent(model_name=args.model_name,
                                  temperature=args.temperature,
                                  config=agree_config,
                                  output=args.output_dir,
                                  api_key=args.api_key,
                                  sleep_time=0,
                                  base_url=args.base_url)
        roles.load_json(i)
        agree.load_json(i)