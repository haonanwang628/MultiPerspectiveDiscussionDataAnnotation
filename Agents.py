from utils.Agent import Agent
from utils.Function import *
import streamlit as st


class RoleAgent:
    def __init__(self,
                 model_name='deepseek-chat',
                 temperature=0,
                 config=None,  # path
                 output=None,  # path
                 api_key=None,
                 sleep_time=0,
                 base_url='https://api.deepseek.com'
                 ):
        """
        Create a RoleAgent

        Args:
            model_name (str): openai model name
            temperature (float): higher values make the output more random, while lower values make it more focused and deterministic
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

    def single_agents_init(self):
        role = Agent(
            model_name=self.model_name,
            name="Role Agent",
            temperature=self.temperature,
            api_key=self.api_key,
            sleep_time=self.sleep_time,
            base_url=self.base_url
        )
        role_infer_sys = self.config["role_infer"]["system"].replace("[Insert Domain Name]", self.config["Domain"])
        role.set_meta_prompt(role_infer_sys)
        role.event(self.config["role_infer"]["user"])
        Annotators = role.ask()
        role.memory(Annotators, False)

        return to_json(Annotators)  # "role": "" , "disciplinary_background":"", "perspective":""

    def single_agents_codebook(self, Annotators_meta):
        Annotators_str = ""
        Annotators = []
        for i in range(len(Annotators_meta)):
            role_prompt = self.config["role_prompt"] \
                .replace("^^^role^^^", Annotators_meta[i]["role" + str(i + 1)]) \
                .replace("^^^Disciplinary Background^^^", Annotators_meta[i]["disciplinary_background"]) \
                .replace("^^^Perspective^^^", Annotators_meta[i]["perspective"])

            role = Agent(
                model_name=self.model_name,
                name=Annotators_meta[i]["role" + str(i + 1)],
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
            Annotators.append(to_json(role_response))

        # [{"role": "" , "disciplinary_background":"", "codebook":[{"code":"", "justification":""}]}]
        return Annotators_str, Annotators

    def load_json(self, id):
        output_dir = os.path.join(self.output, "role-agent")
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        save_json_path = os.path.join(output_dir, f"role_response{id}.json")
        # result = {"target_text": self.config["target_text"], "Annotators": self.Annotators, "Makers": self.makers}
        result = {"target_text": self.config["target_text"], "Annotators": self.Annotators}
        json_code = json.dumps(result, indent=4, ensure_ascii=False)
        with open(save_json_path, "w") as file:
            file.write(json_code)


class AgreeAgent:
    def __init__(self,
                 model_name='deepseek-chat',
                 temperature=0,
                 config=None,  # path
                 output=None,  # path
                 api_key=None,
                 sleep_time=0,
                 base_url='https://api.deepseek.com'
                 ):
        """
        Create a AgreeAgent

        Args:
            model_name (str): openai model name
            temperature (float): higher values make the output more random, while lower values make it more focused and deterministic
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

        # "agreement": [{"code:"", justification:""}] , disagreement":"",
        self.view = self.agree_agent_codebook()

    def agree_agent_codebook(self):
        agree = Agent(
            model_name=self.model_name,
            name="Agree Agent",
            temperature=self.temperature,
            api_key=self.api_key,
            sleep_time=self.sleep_time,
            base_url=self.base_url
        )
        agree_agent_infer = self.config["agree_infer"]["system"].replace("[code and justifications]",
                                                                         self.config["Annotators"])
        agree.set_meta_prompt(agree_agent_infer)
        agree.event(self.config["agree_infer"]["user"])
        view = agree.ask()
        agree.memory(view, False)

        return to_json(view)  # "agreement": [{"code:"", justification:""}] , disagreement":"",

    def load_json(self, id):
        output_dir = os.path.join(self.output, "agree-agent")
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        save_json_path = os.path.join(output_dir, f"agree_response{id}.json")
        result = {"target_text": self.config["target_text"], "codebook": self.view}
        json_code = json.dumps(result, indent=4, ensure_ascii=False)
        with open(save_json_path, "w") as file:
            file.write(json_code)


class DebateAgent:
    def __init__(self,
                 model_name='deepseek-chat',
                 temperature=0,
                 config=None,  # path
                 output=None,  # path
                 api_key=None,
                 sleep_time=0,
                 base_url='https://api.deepseek.com'
                 ):
        """
        Create a AgreeAgent

        Args:
            model_name (str): openai model name
            temperature (float): higher values make the output more random, while lower values make it more focused and deterministic
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

        # init debate
        self.affirmative, self.negative, self.judge = self.debate_agents_init()

        # final codebook
        self.codebook = self.debate()

    def debate_agents_init(self):
        aff = Agent(
            model_name=self.model_name,
            name="Affirmative Debater",
            temperature=self.temperature,
            api_key=self.api_key,
            sleep_time=self.sleep_time,
            base_url=self.base_url
        )
        neg = Agent(
            model_name=self.model_name,
            name="Negative Debater",
            temperature=self.temperature,
            api_key=self.api_key,
            sleep_time=self.sleep_time,
            base_url=self.base_url
        )
        judge = Agent(
            model_name=self.model_name,
            name="Judge",
            temperature=self.temperature,
            api_key=self.api_key,
            sleep_time=self.sleep_time,
            base_url=self.base_url
        )
        meta_prompt = self.config["meta_prompt"].replace("[Target Text]", self.config["target_text"]).replace(
            "[code and justification]", str(self.config["Disagreed"]))
        aff.set_meta_prompt(meta_prompt)
        neg.set_meta_prompt(meta_prompt)
        judge.set_meta_prompt(meta_prompt)
        return aff, neg, judge

    def debate(self):
        for _, codebook in enumerate(self.config["Disagreed"]):
            code, justification = codebook["code"], codebook["justification"]

            # round1
            self.affirmative.event(
                self.config["Affirmative Debater"]["round 1"].replace("[code]", code).replace("[justification]",
                                                                                              justification))
            aff_r1 = self.affirmative.ask()
            self.affirmative.memory(aff_r1, True)

            self.negative.event(
                self.config["Negative Debater"]["round 1"].replace("[code]", code)
                .replace("[justification]", justification).replace("opponent_round1", aff_r1))
            neg_r1 = self.negative.ask()
            self.negative.memory(neg_r1, True)

            # round2
            self.affirmative.event(self.config["Affirmative Debater"]["round 2"].replace("opponent_round1", neg_r1))
            aff_r2 = self.affirmative.ask()
            self.affirmative.memory(aff_r2, True)

            self.negative.event(self.config["Negative Debater"]["round 2"].replace("opponent_round2", aff_r2))
            neg_r2 = self.negative.ask()
            self.negative.memory(neg_r2, True)

            # closing
            self.affirmative.event(self.config["Affirmative Debater"]["closing"])
            aff_close = self.affirmative.ask()
            self.affirmative.memory(aff_close, True)

            self.negative.event(self.config["Negative Debater"]["closing"])
            neg_close = self.negative.ask()
            self.negative.memory(neg_close, True)

            # self.judge
            self.judge.event(
                self.config["Judge"].replace("AFF_R1", aff_r1).replace("AFF_R2", aff_r2).replace("NEG_R1", neg_r1)
                .replace("NEG_R2", neg_r2).replace("AFF_CLOSE", aff_close).replace("NEG_CLOSE", neg_close))
            jud = self.judge.ask()
            self.judge.memory(jud, True)

        return self.to_codebook(self.judge.memory_lst)


    @staticmethod
    def to_codebook(judge_response):
        codebook = []
        for _, response in enumerate(judge_response):
            if response["role"] == "assistant":
                content = json.loads(response["content"].replace('```', '').replace('json', '').replace('\n', ''))
                if content["Resolution"] != "Drop":
                    codebook.append({"code": content["final_code"],
                                     "justification": content["briefly explain"]
                                     })
        return codebook

    def load_json(self, id):
        output_dir = os.path.join(self.output, "debate-agent")
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        save_json_path = os.path.join(output_dir, f"debate_response{id}.json")
        result = {"target_text": self.config["target_text"], "Disagreed": self.config["Disagreed"],
                  "Affirmative Debater": self.affirmative.memory_lst,
                  "Negative Debater": self.negative.memory_lst,
                  "Judge": self.judge.memory_lst,
                  "Debate Result": self.codebook
                  }
        json_code = json.dumps(result, indent=4, ensure_ascii=False)
        with open(save_json_path, "w") as file:
            file.write(json_code)

