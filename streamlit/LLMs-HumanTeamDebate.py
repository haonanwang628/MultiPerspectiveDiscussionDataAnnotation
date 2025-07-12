import streamlit as st
import os
import sys
import time
import json
import os
import copy

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.append(project_root)

from utils import Agent
from utils.Function import *


class MultiAgentsDebate:
    def __init__(self, model_names):
        self.user_avatar = "🧑‍💻"
        self.title = "LLM-Human Team Debate"
        self.models_name = model_names
        self.init_session()

    def init_session(self):
        if "chat_history" not in st.session_state:
            # introduce (F1)
            prologue = debate_config["Facilitator"]["task1"]
            st.session_state.chat_history = [{
                "role": "Introduce-Prologue",
                "name": "Facilitator(Introduce)",
                "avatar": "📃",
                "content": prologue
            }]
        if "roles_identity" not in st.session_state:
            st.session_state.roles_identity = []
            st.session_state.roles_positionality = ["#########"] * 3
        if "debate_models" not in st.session_state:
            st.session_state.debate_models = {
                "Role1": self.models_name["Role1"],
                "Role2": self.models_name["Role2"],
                "Human": self.models_name["Human"],
                "Facilitator": self.models_name["Facilitator"]
            }
            st.session_state.debate_responses = []
        if "agree_list" not in st.session_state:
            st.session_state.agree_list = []
        if "disagreed_list" not in st.session_state:
            st.session_state.disagreed_list = []
            st.session_state.disagreed_list_select = []
        if "Facilitator" not in st.session_state:
            st.session_state.Facilitator = None
        if "roles" not in st.session_state:
            st.session_state.roles = None

    def render_model_selectors(self):
        with st.sidebar:
            st.subheader("⚖️ LLM-Human Team")
            st.session_state.roles_identity.clear()
            for i, role in enumerate(["Role1", "Role2"]):
                self.render_divider()
                role_selected = st.selectbox(f"{role}", roles_name, index=i, key=f"{role}_name")
                disciplinary_selected = st.selectbox("Disciplinary Background", Disciplinary_Background, index=i,
                                                     key=f"{role}_Disciplinary_Background")
                corevalue_selected = st.selectbox("Core Value", Core_Values, index=i, key=f"{role}_Core_Value")
                st.markdown("Positionality Statement")
                st.markdown(st.session_state.roles_positionality[i])
                st.session_state.roles_identity.append({"role": role_selected,
                                                        "disciplinary_background": disciplinary_selected,
                                                        "core_value": corevalue_selected})
            self.render_divider()
            st.markdown("Human")
            input_container1 = st.empty()
            input_container2 = st.empty()
            input_container3 = st.empty()

            def white_background_div(content):
                return f"""
                <div style="
                    background-color: white;
                    padding: 8px;
                    border-radius: 8px;
                    margin-bottom: 10px;
                ">
                    {content}
                </div>
                """

            with input_container1:
                text1 = st.text_input("Your role information")
            with input_container2:
                text2 = st.text_input("Your Disciplinary Background information")
            with input_container3:
                text3 = st.text_input("Your Core Value information")
            if text1 and text2 and text3:
                st.session_state.roles_identity.append({"role": text1,
                                                        "disciplinary_background": text2,
                                                        "core_value": text3})
                input_container1.empty()
                input_container2.empty()
                input_container3.empty()

                st.markdown(white_background_div(text1), unsafe_allow_html=True)

                st.markdown("Disciplinary Background", unsafe_allow_html=True)
                st.markdown(white_background_div(text2), unsafe_allow_html=True)

                st.markdown("Core Value", unsafe_allow_html=True)
                st.markdown(white_background_div(text3), unsafe_allow_html=True)
            st.markdown("Positionality Statement")
            st.markdown(st.session_state.roles_positionality[2])

    def render_sidebar_results(self):
        with st.sidebar:
            st.markdown("""
                <style>
                div.stButton > button:first-child {
                    color: red;              /* 文字颜色 */
                    padding: 10px;          /* 内边距 */
                    border-radius: 10px;       /* 圆角 */
                    font-size: 10px;         /* 字体大小 */
                    transition: 1s;        /* 平滑过渡 */
                }
                div.stButton > button:first-child:hover {
                    background-color: #45a049; /* 悬停时颜色 */
                    transform: scale(1.1);   /* 悬停放大 */
                }
                </style>
            """, unsafe_allow_html=True)
            self.render_divider()
            if st.button("Generate Positionality"):
                self.roles_stage(pos=True)
                st.markdown("Generate Finish")
            self.render_divider()

            # target_text show
            st.markdown("### Target Text")
            if st.session_state.get("target_text"):
                st.markdown(f"{st.session_state.target_text}")
            else:
                st.markdown("#########")
            self.render_divider()

            if st.button("Update Items/Positionality"):
                pass
            self.render_divider()

            st.markdown("### ✅ Agreed Items")
            for _, item in enumerate(st.session_state.agree_list):
                st.markdown(f"- {item['code']}")

            st.markdown("---")
            st.markdown("### ⚠️ Disagreed Items")
            for idx, item in enumerate(st.session_state.disagreed_list):
                if st.button(f"🔍 {item['code']}", key=f"discuss_{idx}"):
                    st.session_state.selected_disagree = item
                    st.session_state.chat_history = [chat for chat in st.session_state.chat_history if
                                                     chat.get("role") != "Debate Agent" or chat.get(
                                                         "role") != "debate divider"]

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
                <b>{name}</b>
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

    def render_divider(self, text=""):
        st.markdown(
            f"""
            <style>
            .custom-divider {{
                color: gray;
                text-align: center;
                border-top: 1px solid #aaa;
                padding: 10px;
                font-family: sans-serif;
            }}
            </style>
            <div class='custom-divider'>{text}</div>
            """,
            unsafe_allow_html=True
        )

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
            elif msg["role"] in {"divider", "debate divider"}:
                self.render_divider(msg["content"])
            else:
                self.render_agent_message(msg["name"], msg["avatar"], msg["content"])

    def handle_input(self):
        user_input = st.chat_input("Input your text here...")
        if user_input:
            st.session_state.target_text = user_input
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            self.render_user_message(user_input)

            st.session_state.role_reply = None
            st.session_state.agree_reply = None

            # Role_Inference_Stage
            st.session_state.chat_history.append({
                "role": "divider",
                "content": "Roles Init Codebook"
            })
            self.roles_stage(st.session_state.target_text, pos=False, code_gen=True)
            st.session_state.chat_history.append({
                "role": "Roles Generation agent",
                "name": "Role_Inference_Stage",
                "avatar": "🔁",
                "content": st.session_state.roles_annotate
            })
            self.render_agent_message("Role_Inference_Stage", "🔁", st.session_state.roles_annotate, True)
            st.session_state.role_reply = st.session_state.roles_annotate

            # Agree_Disagree_stage (F2)
            st.session_state.chat_history.append({
                "role": "divider",
                "content": "Agree/Disagree Codebook"
            })
            self.render_divider("Agree/Disagree Codebook")
            agree_disagree_reply = self.agree_disagree(st.session_state.target_text)
            st.session_state.chat_history.append({
                "role": "Agree-Disagree",
                "name": "Facilitator(Agree vs Disagree)",
                "avatar": "📃",
                "content": agree_disagree_reply
            })
            self.render_agent_message("Facilitator(Agree vs Disagree)", "📃", agree_disagree_reply, True)
            st.session_state.agree_disagree_reply = agree_disagree_reply

            if st.session_state.role_reply and st.session_state.agree_disagree_reply:
                st.session_state.agree_list = st.session_state.agree_disagree_reply.get("Agreed", [])
                st.session_state.disagreed_list = st.session_state.agree_disagree_reply.get("Disagreed", [])
                if not st.session_state.disagreed_list:
                    save_codebook_excel("codebook.xlsx", st.session_state.target_text, st.session_state.agree_list)

            # Debate Ready (F3)
            st.session_state.chat_history.append({
                "role": "divider",
                "content": "Start Debate"
            })
            self.render_divider("Start Debate")
            st.session_state.Facilitator.event(debate_config["Facilitator"]["task3"]
                                               .replace("[Target Text]", st.session_state.target_text)
                                               .replace("[ROLE_CODEBOOKS]", str(st.session_state.roles_annotate))
                                               .replace("[Disagreed]", str(st.session_state.disagreed_list)))
            debate_ready_reply = st.session_state.Facilitator.ask()
            st.session_state.Facilitator.memory(debate_ready_reply, False)
            st.session_state.chat_history.append({
                "role": "Agree-Disagree",
                "name": "Facilitator(Why Disagree)",
                "avatar": "📃",
                "content": debate_ready_reply
            })
            self.render_agent_message("Facilitator(Why Disagree)", "📃", debate_ready_reply, True)

    def roles_stage(self, target_text="", pos=False, code_gen=False):
        # llm team (each role define)
        role1_model = st.session_state.debate_models["Role1"]
        role2_model = st.session_state.debate_models["Role2"]
        human_model = st.session_state.debate_models["Human"]
        role1, role2, human = [
            Agent.Agent(
                model_name=mdl,
                name=role,
                api_key=api_key[mdl],
                base_url=base_url[mdl]
            )
            for mdl, role in
            zip([role1_model, role2_model, human_model], ["Role1", "Role2", "Human"])
        ]

        # roles system
        if not role1.memory_lst:
            for role, meta in zip([role1, role2, human], st.session_state.roles_identity):
                role_prompt = debate_config["role_prompt"]["system"] \
                    .replace("[role]", meta["role"]) \
                    .replace("[Disciplinary Background]", meta["disciplinary_background"]) \
                    .replace("[Core Value]", meta["core_value"])
                role.set_meta_prompt(role_prompt)
            st.session_state.roles = [role1, role2, human]

        # positionality statement
        if pos:
            positionality = []
            for role in st.session_state.roles:
                role.event(debate_config["role_prompt"]["positionality"])
                role_response = role.ask()
                positionality.append(role_response)
                role.memory(role_response)
            st.session_state.roles_positionality = positionality

        # roles codebook generate
        if code_gen:
            roles_annotate = []
            for role in st.session_state.roles:
                role.event(debate_config["role_prompt"]["task"].replace("[Target Text]", target_text))
                role_response = role.ask()
                role.memory(role_response)
                roles_annotate.append(
                    json.loads(role_response.replace('```', "").replace('json', '').strip()))
            st.session_state.roles_annotate = roles_annotate  # Roles Annotate list

    def agree_disagree(self, target_text):
        fac_model = st.session_state.debate_models["Facilitator"]
        Facilitator = Agent.Agent(
            model_name=fac_model,
            name="Agree_Disagree",
            api_key=api_key[fac_model],
            base_url=base_url[fac_model]
        )
        agree_agent_infer = debate_config["Facilitator"]["system"]
        Facilitator.set_meta_prompt(agree_agent_infer)
        Facilitator.event(debate_config["Facilitator"]["task2"]
                          .replace("[codes and justifications]", str(st.session_state.roles_annotate))
                          .replace("[Target Text]", target_text))

        view = Facilitator.ask()
        Facilitator.memory(view, False)
        st.session_state.Facilitator = Facilitator
        return json.loads(eval(view.replace('```', "'''").replace('json', '').replace('\n', '')))

    def debate_single(self, target_text, code, evidence):
        # Central Issue
        st.session_state.chat_history.append({
            "role": "divider",
            "content": "Central Issue"
        })
        self.render_divider("Central Issue")
        issue = debate_config["Facilitator"]["Central Issue"]
        st.session_state.chat_history.append({
            "role": "Agree-Disagree",
            "name": "Facilitator",
            "avatar": "📃",
            "content": issue
        })
        self.render_agent_message("Facilitator(Issue)", "📃", issue, True)

        # role system setting
        meta_prompt = debate_config["role_debater"]["system"].replace("[Target Text]", target_text).replace(
            "[code and justification]", str([{"code": code, "evidence": evidence}]))
        for role, meta in zip(st.session_state.roles, st.session_state.roles_identity):
            role.memory_lst.clear()
            role_prompt = debate_config["role_prompt"]["system"] \
                .replace("[role]", meta["role"]) \
                .replace("[Disciplinary Background]", meta["disciplinary_background"]) \
                .replace("[Core Value]", meta["core_value"])
            role.set_meta_prompt(role_prompt)
            role.set_meta_prompt(meta_prompt)

        # role setting
        roles = [
            {"name": f"Role1({st.session_state.roles_identity[0]['role']})", "color": "🟢",
             "obj": st.session_state.roles[0]},
            {"name": f"Role2({st.session_state.roles_identity[1]['role']})", "color": "🔴",
             "obj": st.session_state.roles[1]},
            {"name": f"Human({st.session_state.roles_identity[2]['role']})", "color": "🧑‍💻",
             "obj": st.session_state.roles[2]}
        ]

        # Debating
        debate_responses = []
        for i, debate in enumerate(debate_config["role_debater"]["debate_round"].items()):
            st.session_state.chat_history.append({
                "role": "debate divider",
                "content": round_theme[i]
            })
            self.render_divider(round_theme[i])
            roles_responses = []
            for role_info in roles:
                role = role_info["obj"]
                if i > 0:
                    role.event(
                        f"Round {i + 1}:\n{debate}".replace("[response]", str(debate_responses[-1])))
                else:
                    role.event(f"Round {i + 1}:\n{debate}")
                response = role.ask()
                response = response if f"Round {i + 1}" in response else f"Round {i + 1}\n{response}"
                roles_responses.append(f"{role_info['name']}: {response}")
                role.memory(response)
                self.display_debate_dialogue(role_info["name"], role_info["color"],
                                             response.replace(f"Round {i + 1}", ""))
            # include roles_responses of every round
            debate_responses.append(f"Round {i + 1}: {roles_responses}")
        st.session_state.debate_responses.append(debate_responses)

        # Closing (F4)
        close_prompt = debate_config["Facilitator"]["task4"].replace("[debate_responses]",
                                                                     str(debate_responses))
        st.session_state.Facilitator.event(close_prompt)
        close = st.session_state.Facilitator.ask()
        st.session_state.Facilitator.memory(close, False)
        close_response = json.loads(close.replace('```', '').replace('json', '').strip())
        self.display_debate_dialogue("Facilitator(Final conclusion)", "⚖️",
                                     json.dumps(close_response, ensure_ascii=False, indent=2))

        # debate finish
        st.session_state.close_resolution = close_response["Resolution"]
        if close_response["Resolution"].strip().lower() != "drop":
            st.session_state.final_code = close_response["final_code"]
            st.session_state.final_justification = close_response["evidence"]

    def run(self):
        st.set_page_config(page_title=self.title, layout="wide")
        st.title(self.title)

        self.render_chat()
        self.render_model_selectors()
        self.handle_input()
        self.render_sidebar_results()

        if st.session_state.get("selected_disagree") in st.session_state.disagreed_list:
            # Single Disagreed Debate
            item = st.session_state.selected_disagree
            st.session_state.disagreed_list_select.append(item["code"])
            self.debate_single(st.session_state.target_text, item["code"], item["evidence"])
            st.session_state.disagreed_list = [i for i in st.session_state.disagreed_list if
                                               i.get("code") != item["code"]]
            resolution = st.session_state.close_resolution
            if isinstance(resolution, str) and resolution.strip().lower() != "drop":
                st.session_state.agree_list.append({"code": st.session_state.final_code,
                                                    "evidence": st.session_state.final_justification})

            if not st.session_state.disagreed_list:
                # Save Debate Process
                save_debate_excel("debate.xlsx", st.session_state.target_text, st.session_state.disagreed_list_select,
                                  st.session_state.debate_responses)
                st.session_state.debate_responses.clear()
                # Save Final Codebook
                save_codebook_excel("codebook.xlsx", st.session_state.target_text, st.session_state.agree_list)


if __name__ == "__main__":
    debate_config = import_json("config/debate_config.json")
    models_name = {
        "Role1": "deepseek-chat",
        "Role2": "deepseek-chat",
        "Human": "deepseek-chat",
        "Facilitator": "deepseek-chat",
    }
    app = MultiAgentsDebate(models_name)
    app.run()
