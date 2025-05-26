import json
import os
import argparse
from utils.Agent import Agent
from utils.Function import *

class SingleDabate:
    def __init__(self,
                 model_name='deepseek-chat',
                 temperature=0,
                 config=None,  # path
                 output=None,  # path
                 api_key=None,
                 sleep_time=0,
                 base_url='https://api.deepseek.com'
                 ):
        """Create a SingleDabate

          Args:
              model_name (str): openai model name
              temperature (float): higher values make the output more random, while lower values make it more focused and deterministic
              num_players (int): num of players
              api_key (str): As the parameter name suggests
              sleep_time (float): sleep because of rate limits
              base_url (str): base URL for non-OpenAI models
        """
        self.model_name = model_name
        self.temperature = temperature
        self.api_key = api_key
        self.sleep_time = sleep_time
        self.base_url = base_url
        self.output = output

        self.config = config

        # 1、init: Role Inference Stage
        # list: [{"role": "" , "disciplinary_background":"", "perspective":""} ...]
        self.Annotators_meta = self.single_agents_init()

        # 2、Agents/llms generate codebook
        # list: [{"role": "" , "disciplinary_background":"", "codebook":[{"code":"", "justification":""}]}]
        self.Annotators_str, self.Annotators = self.single_agents_codebook(self.Annotators_meta)

        ###TRASH
        # response maker
        # self.makers = self.single_agents_maker(self.Annotators_str)

    def single_agents_init(self):
        role = Agent(
            model_name=self.model_name,
            name="Role Inference Stage",
            temperature=self.temperature,
            api_key=self.api_key,
            sleep_time=self.sleep_time,
            base_url=self.base_url
        )
        role_infer_sys = self.config["role_infer"][0]["system"].replace("[Insert Domain Name]", self.config["Domain"])
        role.set_meta_prompt(role_infer_sys)
        role.event(self.config["role_infer"][1]["user"])
        Annotators = role.ask()
        role.memory(Annotators, False)

        return get_json(Annotators)  # "role": "" , "disciplinary_background":"", "perspective":""

    def single_agents_codebook(self, Annotators_meta):
        Annotators_str = ""
        Annotators = []
        for i in range(len(Annotators_meta)):

            role_prompt = self.config["role_prompt"] \
                .replace("^^^role^^^", Annotators_meta[i]["role"+str(i+1)]) \
                .replace("^^^Disciplinary Background^^^", Annotators_meta[i]["disciplinary_background"]) \
                .replace("^^^Perspective^^^", Annotators_meta[i]["perspective"])

            role = Agent(
                model_name=self.model_name,
                name=Annotators_meta[i]["role"+str(i+1)],
                temperature=self.temperature,
                api_key=self.api_key,
                sleep_time=self.sleep_time,
                base_url=self.base_url
            )

            role.set_meta_prompt(role_prompt)
            role.event(self.config["meta_prompt"].replace("[Target Text]", self.config["target_text"]))
            role_response = role.ask()
            role.memory(role_response, False)
            Annotators_str += "/n" + role_response
            Annotators.append(get_json(role_response))

        # [{"role": "" , "disciplinary_background":"", "codebook":[{"code":"", "justification":""}]}]
        return Annotators_str, Annotators

    def single_agents_maker(self, Annotators):
        makers = {}
        m1, m2 = Agent(
            model_name=self.model_name,
            name="decision maker",
            temperature=self.temperature,
            api_key=self.api_key,
            sleep_time=self.sleep_time,
            base_url=self.base_url
        ), \
            Agent(
                model_name=self.model_name,
                name="evaluate maker",
                temperature=self.temperature,
                api_key=self.api_key,
                sleep_time=self.sleep_time,
                base_url=self.base_url
            )
        decision_prompt = self.config["decision maker"].replace("[codebook]", Annotators).replace("[target_text]", self.config["target_text"])
        evaluate_prompt = self.config["evaluate maker"].replace("[codebook]", Annotators)
        m1.event(decision_prompt)
        decision_response = m1.ask()
        m1.memory(decision_response, False)
        m2.event(evaluate_prompt)
        evaluate_response = m2.ask()
        m2.memory(evaluate_response, False)
        makers["decision maker"] = get_json(decision_response)
        makers["evaluate maker"] = get_json(evaluate_response)

        return makers

    def load_json(self, id):
        save_json_path = os.path.join(self.output, f"{id}.json")
        # result = {"target_text": self.config["target_text"], "Annotators": self.Annotators, "Makers": self.makers}
        result = {"target_text": self.config["target_text"], "Annotators": self.Annotators}
        json_code = json.dumps(result, indent=4, ensure_ascii=False)
        with open(save_json_path, "w") as file:
            file.write(json_code)


def parse_args():
    parser = argparse.ArgumentParser("", formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument("-i", "--input-file", type=str,
                        default=r"F:\Work\Debate\MultiAgentDabateDataAnnotation\Data\processed\raw_text.txt",
                        help="raw_text Input file path")
    parser.add_argument("-o", "--output-dir", type=str,
                        default=r"F:\Work\Debate\MultiAgentDabateDataAnnotation\Data\single_agents_codebook\output",
                        help="Output file dir")
    parser.add_argument("-k", "--api-key", type=str, default="sk-9bc06d1289704b05b7b52db5285dba67",
                        help="OpenAI api key")
    parser.add_argument("-b", "--base-url", type=str, default="https://api.deepseek.com/v1",
                        help="base URL for non-OpenAI models")
    parser.add_argument("-m", "--model-name", type=str, default="deepseek-chat", help="Model name")
    parser.add_argument("-t", "--temperature", type=float, default=0, help="Sampling temperature")

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    # root_path = os.path.dirname(os.path.abspath(__file__))
    # raw_text_path = os.path.join(root_path, "Data", "processed", "raw_text.txt")
    # code_config_path = os.path.join(root_path, "Data", "single_agents_codebook", "code_config.json")
    # meta_prompt_config_path = os.path.join(root_path, "Data", "single_agents_codebook", "meta_prompt_config.json")
    with open(os.path.join(args.output_dir, "..", "config_1.json"), "r", encoding="utf-8") as f:
        config = json.load(f)
    with open(args.input_file, "r") as f:
        texts = f.readlines()

    for i, text in enumerate(texts):
        config["Domain"], config["target_text"] = text.split(",")[0], text.split(",")[1]

        debate = SingleDabate(model_name=args.model_name,
                              temperature=args.temperature,
                              config=config,
                              output=args.output_dir,
                              api_key=args.api_key,
                              sleep_time=0,
                              base_url=args.base_url)

        debate.load_json(i)
