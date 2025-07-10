from utils.Agent import Agent
from utils.Function import *


class DebateModel:
    def __init__(self, debate_config, llms_name):
        """Create a Debate Model
        Args:
            debate_config: debate prompt and debate progress design
            llms_name (str): multi llm(roles and moderator) name, e.g., ['gpt-4', 'deepseek-chat'],

        """
        self.config = debate_config
        self.llm_names = llms_name

        self.target_text = self.config["target_text"]

    def agents_init(self):
        """
            return: roles and Moderator Agent.
        """
        Role1, Role2, Role3, Moderator = [
            Agent(
                model_name=mdl,
                name=role,
                api_key=api_key[mdl],
                base_url=base_url[mdl]
            )
            for mdl, role in
            zip(self.llm_names, ["Role1", "Role2", "Role3"])
        ]
        roles = [Role1, Role2, Role3]
        return roles, Moderator

    def role_stage(self, roles, roles_identity):
        """
        Args:
            roles: list of all role Agent.
            roles_identity: Set up the identity for each role. [{"role":, "disciplinary_background":, "core_value":}].
        return: roles annotate----Codebook of target text.
        """
        roles_annotate, roles_positionality = [], []
        for role, meta in zip(roles, roles_identity):
            role_prompt = self.config["role_prompt"]["system"] \
                .replace("[role]", meta["role"]) \
                .replace("[Disciplinary Background]", meta["disciplinary_background"]) \
                .replace("[Core Value]", meta["core_value"])

            # roles system
            role.set_meta_prompt(role_prompt)

            # roles positionality statement
            role.event(self.config["role_prompt"]["positionality"])
            role_response = role.ask()
            roles_positionality.append(role_response)
            role.memory(role_response, if_print=False)

            # roles codebook generate
            role.event(self.config["role_prompt"]["task"].replace("[Target Text]", self.target_text))
            role_response = role.ask()
            role.memory(role_response, if_print=False)
            roles_annotate.append(
                json.loads(role_response.replace('```', "").replace('json', '').strip()))
        return roles_positionality, roles_annotate

    def agree_disagree(self, Moderator, roles_annotate):
        """
        Args:
            Moderator: Moderator Agent.
            roles_annotate: roles annotate----Codebook of target text.
        return: Agreed and Disagreed Codebook.
        """
        agree_agent_infer = self.config["Moderator"]["system"]
        Moderator.set_meta_prompt(agree_agent_infer)
        Moderator.event(self.config["Moderator"]["task2"]
                        .replace("[codes and justifications]", str(roles_annotate))
                        .replace("[Target Text]", self.target_text))
        view = Moderator.ask()
        Moderator.memory(view, if_print=False)
        return json.loads(eval(view.replace('```', "'''").replace('json', '').replace('\n', '')))

    def single_disagree_debate(self, roles, roles_identity, Moderator, disagree):
        """
        Args:
            Moderator: Moderator Agent.
            roles: list of all role Agent.
            roles_identity: Set up the identity for each role. [{"role":, "disciplinary_background":, "core_value":}].
            disagree: disagree codebook.
        return:
        """
        meta_prompt = self.config["role_debater"]["system"].replace("[Target Text]", self.target_text).replace(
            "[code and justification]", str([{"code": disagree["code"], "justification": disagree["justification"]}]))
        for role, meta in zip(roles, roles_identity):
            role.memory_lst.clear()
            role_prompt = self.config["role_prompt"]["system"] \
                .replace("[role]", meta["role"]) \
                .replace("[Disciplinary Background]", meta["disciplinary_background"]) \
                .replace("[Core Value]", meta["core_value"])
            role.set_meta_prompt(role_prompt)
            role.set_meta_prompt(meta_prompt)

        roles_update = [
            {"name": f"Role1({roles_identity[0]['role']})", "obj": roles[0]},
            {"name": f"Role2({roles_identity[1]['role']})", "obj": roles[1]},
            {"name": f"Role3({roles_identity[2]['role']})", "obj": roles[2]}
        ]

        # Debating
        debate_responses = []
        for i, debate in enumerate(self.config["role_debater"]["debate_round"].items()):
            roles_responses = []
            for role_info in roles_update:
                role = role_info["obj"]
                if i > 0:
                    role.event(f"Round {i + 1}:\n{debate}".replace("[response]", str(debate_responses[-1])))
                else:
                    role.event(f"Round {i + 1}:\n{debate}")
                response = role.ask()
                response = response if f"Round {i + 1}" in response else f"Round {i + 1}\n{response}"
                roles_responses.append(f"{role_info['name']}: {response}")
                role.memory(response, if_print=False)
            # include roles_responses of every round
            debate_responses.append(f"Round {i + 1}: {roles_responses}")

        # Closing (F4)
        close_prompt = self.config["Moderator"]["task4"] \
            .replace("[debate_responses]",str(debate_responses))
        Moderator.event(close_prompt)
        close = Moderator.ask()
        Moderator.memory(close, False, False)
        close_response = json.loads(close.replace('```', '').replace('json', '').strip())

        return debate_responses, close_response

    def save_json(self):
        ...
