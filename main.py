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
    debate_config = import_json(os.path.join(args.config_dir, "debate_config.json"))

    codebook_dir = os.path.join(args.output_dir, "Scrum-interviews-Codebook")
    if not os.path.exists(codebook_dir):
        os.makedirs(codebook_dir)

    for i, text in enumerate(texts):

        if i == 1:
            break
        role_config["target_text"] = text["data_chunk"]
        agree_config["target_text"] = text["data_chunk"]
        debate_config["target_text"] = text["data_chunk"]
        roles = Agents.RoleAgent(model_name=args.model_name,
                                 temperature=args.temperature,
                                 config=role_config,
                                 output=args.output_dir,
                                 api_key=args.api_key,  # []
                                 sleep_time=0,
                                 base_url=args.base_url)
        Annotators_meta = roles.single_agents_init()
        Annotators_str, Annotators = roles.single_agents_codebook(Annotators_meta)
        agree_config["Annotators"] = Annotators_str
        roles.load_json(i, Annotators)

        agree = Agents.AgreeAgent(model_name=args.model_name,
                                  temperature=args.temperature,
                                  config=agree_config,
                                  output=args.output_dir,
                                  api_key=args.api_key,
                                  sleep_time=0,
                                  base_url=args.base_url)
        view = agree.agree_agent_codebook()
        agree.load_json(i, view)
        debate_config["Disagreed"] = view["Disagreed"]

        debate = Agents.DebateAgent(model_name=args.model_name,
                                    temperature=args.temperature,
                                    config=debate_config,
                                    output=args.output_dir,
                                    api_key=args.api_key,
                                    sleep_time=0,
                                    base_url=args.base_url)
        Affirmative, Negative, Judge = debate.debate()
        debate.load_json(i, Affirmative, Negative, Judge)

        codebook = [*view["Agreed"], *debate.to_codebook(Judge.memory_lst)]
        save_json_path = os.path.join(codebook_dir, f"{i}.json")
        result = {"target_text": text["data_chunk"],
                  "codebook": codebook
                  }
        json_code = json.dumps(result, indent=4, ensure_ascii=False)
        with open(save_json_path, "w") as file:
            file.write(json_code)
