import json
import os
import argparse
from utils.Agent_debate import DebateModel
from utils.Function import import_json, roles_identity_generate


def parse_args():
    parser = argparse.ArgumentParser("", formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument("-i", "--input-file", type=str,
                        default=r"F:\Work\Debate\MultiAgentDabateDataAnnotation\Data\Scrum-interviews\processed\First "
                                r"Cycle - RQ1.json",
                        help="raw_text Input file path")
    parser.add_argument("-o", "--output-dir", type=str,
                        default=r"F:\Work\Debate\MultiAgentDabateDataAnnotation\Data\Scrum-interviews\output",
                        help="Codebook and debate output file dir")
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
    models_name = {
        "Role1": "deepseek-chat",
        "Role2": "deepseek-chat",
        "Role3": "deepseek-chat",
        "Facilitator": "deepseek-chat",
    }
    roles_identity = roles_identity_generate(len(models_name) - 1)
    codebook = []
    for i, text in enumerate(texts):
        # if i == 2:
        #     break
        print(f"------------Current Target Text {i+1}------------")
        debate_config["target_text"] = text["data_chunk"]
        debate = DebateModel(debate_config, models_name)
        roles, Facilitator = debate.agents_init()
        roles_positionality, roles_annotate = debate.role_stage(roles, roles_identity)
        for j, positionality in enumerate(roles_positionality):
            roles_identity[j]["positionality"] = positionality
        agree_disagree, disagree_explain = debate.agree_disagree(Facilitator, roles_annotate)
        debate_process, disagree_to_agree = [], []
        for disagree in agree_disagree["Disagreed"]:
            print(f"Disagree [{disagree['code']}] Debating")
            debate_responses, close_response = debate.single_disagree_debate(roles, roles_identity, Facilitator,
                                                                             disagree)
            debate_process.append({
                "Disagreed": disagree["code"],
                "Process": debate_responses,
                "Closing": close_response
            })
            if close_response["Resolution"].strip().lower() == "retain":
                disagree_to_agree.append({
                    "*code": close_response["final_code"],
                    "*evidence": close_response["evidence"]
                })
        print(f"Debate Finish !")
        result = {
            "target_text": debate_config["target_text"],
            "Codebook": agree_disagree["Agreed"] + disagree_to_agree,
            "Role_Team": roles_identity,
            "Consolidating_results": agree_disagree,
            "disagree_explain": disagree_explain,
            "Debate": debate_process,
        }
        codebook.append({"target_text": debate_config["target_text"],
                         "Codebook": agree_disagree["Agreed"]})
        # save every target debate process
        with open(f"{args.output_dir}\debate_process\json\debate_{i}.json", "w", encoding="utf-8") as f:
            json.dump(result, f, indent=4)

    # save data codebook
    with open(f"{args.output_dir}\codebook.json", "w", encoding="utf-8") as f:
        json.dump(codebook, f, indent=4)
