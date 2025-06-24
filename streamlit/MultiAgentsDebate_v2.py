import streamlit as st
import os
import sys
import time
import json
from openpyxl import load_workbook, Workbook
from openpyxl.styles import Alignment
import os

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.append(project_root)

import Agents
from utils.Function import import_json, save_excel

available_models = ["deepseek-chat", "GPT-3.5", "GPT-4", "Claude"]

api_key = {
    "GPT-3.5": "sk-xxx",
    "GPT-4": "sk-xxx",
    "deepseek-chat": "sk-9bc06d1289704b05b7b52db5285dba67",
    "Claude": "sk-xxx"
}

base_url = {
    "GPT-3.5": "https://api.openai.com/v1",
    "GPT-4": "https://api.openai.com/v1",
    "deepseek-chat": "https://api.deepseek.com/v1",
    "Claude": "https://api.anthropic.com"
}


def to_json(response):
    try:
        return json.loads(response.replace('```', '').replace('json', '').strip())
    except:
        return {}


class MultiAgents:
    def __init__(self, model_registry, agent_names, agent_avatars, user_avatar="🧑‍💻"):
        self.model_registry = model_registry
        self.agent_names = agent_names
        self.agent_avatars = agent_avatars
        self.user_avatar = user_avatar
        self.title = "LLM Team Debate"

        self.init_session()
        self.role_agents = None

    def init_session(self):
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []
        if "agent_models" not in st.session_state:
            st.session_state.agent_models = ["deepseek-chat"] * len(self.agent_names)
        if "debate_models" not in st.session_state:
            st.session_state.debate_models = {
                "Role1": "deepseek-chat",
                "Role2": "deepseek-chat",
                "Role3": "deepseek-chat",
                "Judge": "deepseek-chat"
            }
        if "agree_list" not in st.session_state:
            st.session_state.agree_list = []
        if "disagreed_list" not in st.session_state:
            st.session_state.disagreed_list = []

    def render_model_selectors(self):
        with st.sidebar:
            st.subheader("🤖 Assign LLM to Each Agent")
            for i in range(len(self.agent_names)):
                selected_model = st.selectbox(
                    f"{self.agent_names[i]}",
                    available_models,
                    index=0,
                    key=f"model_select_{i}"
                )
                st.session_state.agent_models[i] = selected_model

            st.subheader("⚖️ LLM Team")
            for role in ["Role1", "Role2", "Role3", "Judge"]:
                selected = st.selectbox(
                    f"{role}",
                    available_models,
                    index=0,
                    key=f"debate_model_{role}"
                )
                st.session_state.debate_models[role] = selected

    def render_sidebar_results(self):
        with st.sidebar:
            if st.button("Update"):
                pass

            if st.session_state.get("target_text"):
                st.markdown(f"## **:rainbow[Text]** ")
                st.markdown(f"- :blue-background[***{st.session_state.target_text}***]")
            st.markdown("### ✅ Agreed Items")
            for _, item in enumerate(st.session_state.agree_list):
                st.markdown(f"- {item['code']}")

            st.markdown("---")
            st.markdown("### ⚠️ Disagreed Items")
            for idx, item in enumerate(st.session_state.disagreed_list):
                if st.button(f"🔍 Discuss: {item['code']}", key=f"discuss_{idx}"):
                    st.session_state.selected_disagree = item
                    st.session_state.chat_history = [chat for chat in st.session_state.chat_history if
                                                     chat.get("role") != "Debate Agent"]

    def render_user_message(self, text):
        st.markdown(f"""
        <div style='display: flex; justify-content: flex-end; align-items: center; margin: 6px 0;'>
            <div style='background-color: #DCF8C6; padding: 10px 14px; border-radius: 10px; max-width: 70%; text-align: left;'>
                {text}
            </div>
            <div style='font-size: 24px; margin-left: 8px;'>{self.user_avatar}</div>
        </div>
        """, unsafe_allow_html=True)

    def render_agent_message(self, name, avatar, content, delay=False):
        st.markdown(f"""
        <div style='display: flex; justify-content: flex-start; align-items: flex-start; margin: 6px 0;'>
            <div style='font-size: 24px; margin-right: 8px;'>{avatar}</div>
            <div style='background-color: #F1F0F0; padding: 10px 14px; border-radius: 10px; max-width: 75%; text-align: left;'>
                <b>{name}:</b>
            </div>
        """, unsafe_allow_html=True)

        try:
            parsed = json.loads(content) if isinstance(content, str) else content
            st.json(parsed)
        except Exception:
            placeholder = st.empty()
            full = ""
            for ch in str(content):
                full += ch
                placeholder.markdown(f"<div style='font-family: monospace;'>{full}</div>", unsafe_allow_html=True)
                if delay:
                    time.sleep(0.01)

        st.markdown("</div></div>", unsafe_allow_html=True)

    def display_debate_dialogue(self, speaker_name, avatar, message):
        st.session_state.chat_history.append({
            "role": "Debate Agent",
            "name": speaker_name,
            "avatar": avatar,
            "content": message
        })
        self.render_agent_message(speaker_name, avatar, message)

    def render_chat(self):
        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                self.render_user_message(msg["content"])
            else:
                self.render_agent_message(msg["name"], msg["avatar"], msg["content"])

    def handle_input(self, user_input):
        if user_input:
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            self.render_user_message(user_input)

            st.session_state.role_reply = None
            st.session_state.agree_reply = None

            for i in range(len(self.agent_names)):
                agent_name = self.agent_names[i]
                model_name = st.session_state.agent_models[i]
                agent_func = self.model_registry[agent_name]
                reply = agent_func(user_input, model_name)

                st.session_state.chat_history.append({
                    "role": self.agent_names[i],
                    "name": f"{agent_name} ({model_name})",
                    "avatar": self.agent_avatars[i],
                    "content": reply
                })
                self.render_agent_message(f"{agent_name} ({model_name})", self.agent_avatars[i], reply, True)

                if agent_name == "Role_Inference_Stage":
                    st.session_state.role_reply = reply
                elif agent_name == "Agree_Agent":
                    st.session_state.agree_reply = reply

            if st.session_state.role_reply and st.session_state.agree_reply:
                # st.session_state.agree_list = [item["code"] for item in st.session_state.agree_reply.get("Agreed", [])]
                st.session_state.agree_list = st.session_state.agree_reply.get("Agreed", [])
                st.session_state.disagreed_list = st.session_state.agree_reply.get("Disagreed", [])

    def Role(self, text, model_name):
        role_config["target_text"] = text
        roles = Agents.RoleAgent(
            model_name=model_name,
            config=role_config,
            api_key=api_key[model_name],
            base_url=base_url[model_name]
        )
        meta = roles.single_agents_init()
        st.session_state.roles_meta = meta
        _, Annotators = roles.single_agents_codebook(meta)
        return Annotators

    def Agree(self, text, model_name):
        agree_config["target_text"] = text
        agree = Agents.AgreeAgent(
            model_name=model_name,
            config=agree_config,
            api_key=api_key[model_name],
            base_url=base_url[model_name]
        )
        view = agree.agree_agent_codebook()
        return view

    def debate_single(self, target_text, code, justification):
        role1_model = st.session_state.debate_models["Role1"]
        role2_model = st.session_state.debate_models["Role2"]
        role3_model = st.session_state.debate_models["Role3"]
        judge_model = st.session_state.debate_models["Judge"]
        role1, role2, role3, judge = [
            Agents.Agent(
                model_name=mdl,
                name=role,
                api_key=api_key[mdl],
                base_url=base_url[mdl]
            )
            for mdl, role in
            zip([role1_model, role2_model, role3_model, judge_model], ["Role1", "Role2", "Role3", "Judge"])
        ]

        meta_prompt = debate_config["meta_prompt"].replace("[Target Text]", target_text).replace(
            "[code and justification]", str([{"code": code, "justification": justification}]))
        judge.set_meta_prompt(meta_prompt)

        meta_prompt = debate_config["role_prompt"].replace("[meta_prompt]", meta_prompt)
        for role_obj, meta_data in zip([role1, role2, role3], st.session_state.roles_meta):
            role_name = next(k for k in meta_data.keys() if k.startswith("role"))  # get "role1"/"role2"/"role3"
            customized_prompt = (
                meta_prompt.replace("[role]", meta_data[role_name])
                .replace("[Disciplinary Background]", meta_data["disciplinary_background"])
                .replace("[Perspective]", meta_data["perspective"])
            )
            role_obj.set_meta_prompt(customized_prompt)

        roles = [
            {"name": f"Role1({st.session_state.roles_meta[0]['role1']})", "color": "🟢", "obj": role1},
            {"name": f"Role2({st.session_state.roles_meta[1]['role2']})", "color": "🔴", "obj": role2},
            {"name": f"Role3({st.session_state.roles_meta[2]['role3']})", "color": "🔵", "obj": role3}
        ]

        role_res = [[]]*3
        for r in range(3):
            role_res[r] = []
            if r == 0:
                for role_info in roles:
                    role = role_info["obj"]
                    role.event(debate_config["role debater"]["point"].replace("[code]", code).replace("[justification]",
                                                                                                        justification))
                    response = role.ask()
                    role.memory(response, True)
                    role_res[r].append(f"[{role_info['name']}: {response}]")
                    self.display_debate_dialogue(role_info["name"], role_info["color"], response)
            else:
                for role_info in roles:
                    role = role_info["obj"]
                    role.event(debate_config["role debater"]["round 2~n"].replace("opponent", str(role_res[r-1])))
                    response = role.ask()
                    role.memory(response, True)
                    role_res[r].append(f"[{role_info['name']}: {response}]")
                    self.display_debate_dialogue(role_info["name"], role_info["color"], response)

        # # round 1
        # role_r1 = []
        # for role_info in roles:
        #     role = role_info["obj"]
        #     role.event(debate_config["role debater"]["round 1"].replace("[code]", code).replace("[justification]",
        #                                                                                         justification))
        #     response = role.ask()
        #     role.memory(response, True)
        #     role_r1.append(f"[{role_info['name']}: {response}]")
        #     self.display_debate_dialogue(role_info["name"], role_info["color"], response)
        #
        # # round 2
        # role_r2 = []
        # for role_info in roles:
        #     role = role_info["obj"]
        #     role.event(debate_config["role debater"]["round 2"].replace("opponent_round1", str(role_r1)))
        #     response = role.ask()
        #     role.memory(response, True)
        #     role_r2.append(f"[{role_info['name']}: {response}]")
        #     self.display_debate_dialogue(role_info["name"], role_info["color"], response)

        # closing
        role_close = []
        for role_info in roles:
            role = role_info["obj"]
            role.event(debate_config["role debater"]["closing"])
            response = role.ask()
            role.memory(response, True)
            role_close.append(f"[{role_info['name']}: {response}]")
            self.display_debate_dialogue(role_info["name"], role_info["color"], response)

        judge_prompt = debate_config["Judge"].replace("[ALL_ROLES_R1]", str(role_res[0])) \
            .replace("[ALL_ROLES_R2]", str(role_res[1])).replace("[ALL_ROLES_R3]", str(role_res[2]))\
            .replace("[ROLE_CLOSE]", str(role_close))
        judge.event(judge_prompt)
        jud = judge.ask()
        judge_response = to_json(jud)
        self.display_debate_dialogue("Judge", "⚖️", json.dumps(judge_response, ensure_ascii=False, indent=2))

        st.session_state.judge_resolution = judge_response["Resolution"]
        if judge_response["Resolution"].strip().lower() != "drop":
            st.session_state.judge_final_code = judge_response["final_code"]
            st.session_state.judge_final_justification = judge_response["briefly explain"]

    def run(self):
        st.set_page_config(page_title=self.title, layout="wide")
        st.title(self.title)

        user_input = st.chat_input("Input your text here...")
        if user_input != "" and user_input:
            st.session_state.target_text = user_input
        self.render_chat()
        self.render_model_selectors()
        self.handle_input(user_input)
        self.render_sidebar_results()

        if "selected_disagree" in st.session_state and st.session_state.selected_disagree in st.session_state.disagreed_list:
            target_text = st.session_state.target_text
            item = st.session_state.selected_disagree
            self.debate_single(target_text, item["code"], item["justification"])
            st.session_state.disagreed_list = [i for i in st.session_state.disagreed_list if
                                               i.get("code") != item["code"]]
            resolution = st.session_state.judge_resolution
            if isinstance(resolution, str) and resolution.strip().lower() != "drop":
                st.session_state.agree_list.append({"code": st.session_state.judge_final_code,
                                                    "justification": st.session_state.judge_final_justification})

            # save final codebook
            if not st.session_state.disagreed_list:
                save_excel("codebook.xlsx", target_text, st.session_state.agree_list)


if __name__ == "__main__":
    role_config = import_json("config/role_config.json")
    agree_config = import_json("config/agree_config.json")
    debate_config = import_json("config/debate_config.json")


    app = MultiAgents(
        model_registry={
            "Role_Inference_Stage": lambda text, model: app.Role(text, model),
            "Agree_Agent": lambda text, model: app.Agree(text, model)
        },
        agent_names=["Role_Inference_Stage", "Agree_Agent"],
        agent_avatars=["🔁", "📃"]
    )
    app.run()
