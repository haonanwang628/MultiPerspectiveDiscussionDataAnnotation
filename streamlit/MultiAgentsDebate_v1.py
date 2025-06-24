import streamlit as st
import os
import sys
import time
import json

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.append(project_root)

import Agents
from utils.Function import import_json

available_models = ["GPT-3.5", "GPT-4", "deepseek-chat", "Claude"]

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
    def __init__(self, model_registry, bot_names, bot_avatars, user_avatar="🧑‍💻"):
        self.model_registry = model_registry
        self.bot_names = bot_names
        self.bot_avatars = bot_avatars
        self.user_avatar = user_avatar
        self.title = "🤖 Multi Agents Debate"
        self.init_session()

    def init_session(self):
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []
        if "bot_models" not in st.session_state:
            st.session_state.bot_models = ["GPT-3.5"] * len(self.bot_names)
        if "debate_models" not in st.session_state:
            st.session_state.debate_models = {
                "Affirmative": "GPT-3.5",
                "Negative": "GPT-3.5",
                "Judge": "GPT-3.5"
            }

    def render_user_message(self, text):
        st.markdown(f"""
        <div style='display: flex; justify-content: flex-end; align-items: center; margin: 6px 0;'>
            <div style='background-color: #DCF8C6; padding: 10px 14px; border-radius: 10px; max-width: 70%; text-align: right;'>
                {text}
            </div>
            <div style='font-size: 24px; margin-left: 8px;'>{self.user_avatar}</div>
        </div>
        """, unsafe_allow_html=True)

    def render_bot_message(self, name, avatar, content):
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
                time.sleep(0.01)

        st.markdown("</div></div>", unsafe_allow_html=True)

    def display_debate_dialogue(self, speaker_name, avatar, message, delay=0.02):
        st.session_state.chat_history.append({
            "role": "bot",
            "name": speaker_name,
            "avatar": avatar,
            "content": message
        })
        self.render_bot_message(speaker_name, avatar, message)
        time.sleep(delay)

    def render_chat(self):
        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                self.render_user_message(msg["content"])
            else:
                self.render_bot_message(msg["name"], msg["avatar"], msg["content"])

    def render_model_selectors(self):
        with st.sidebar:
            st.subheader("🤖 Assign LLM to Each Agent")
            for i in range(len(self.bot_names)):
                selected_model = st.selectbox(
                    label=f"{self.bot_names[i]} Model",
                    options=available_models,
                    index=0,
                    key=f"model_select_{i}"
                )
                st.session_state.bot_models[i] = selected_model

            st.subheader("⚖️ Debate Agent Models")
            for role in ["Affirmative", "Negative", "Judge"]:
                selected = st.selectbox(
                    f"{role} uses",
                    available_models,
                    index=0,
                    key=f"debate_model_{role}"
                )
                st.session_state.debate_models[role] = selected

    def handle_input(self, user_input):
        if user_input:
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            self.render_user_message(user_input)

            st.session_state.role_reply = None
            st.session_state.agree_reply = None

            for i in range(len(self.bot_names)):
                agent_name = self.bot_names[i]
                model_name = st.session_state.bot_models[i]
                bot_func = self.model_registry[agent_name]
                reply = bot_func(user_input, model_name)

                st.session_state.chat_history.append({
                    "role": f"bot{i + 1}",
                    "name": f"{agent_name} ({model_name})",
                    "avatar": self.bot_avatars[i],
                    "content": reply
                })
                self.render_bot_message(f"{agent_name} ({model_name})", self.bot_avatars[i], reply)

                if agent_name == "Role_Agent":
                    st.session_state.role_reply = reply
                elif agent_name == "Agree_Agent":
                    st.session_state.agree_reply = reply

            if st.session_state.role_reply and st.session_state.agree_reply:
                debate_config["target_text"] = user_input
                debate_config["Disagreed"] = st.session_state.agree_reply.get("Disagreed", [])
                codebook = [*st.session_state.agree_reply.get("Agreed", []), *self.debate()]
                self.display_debate_dialogue("Judge Final Codebook", "⚖️", json.dumps(codebook, ensure_ascii=False, indent=2))

    def debate(self):
        aff_model = st.session_state.debate_models["Affirmative"]
        neg_model = st.session_state.debate_models["Negative"]
        judge_model = st.session_state.debate_models["Judge"]
        CODEBOOK = []
        aff, neg, judge = [
            Agents.Agent(
                model_name=mdl,
                name=role,
                temperature=0,
                api_key=api_key[mdl],
                sleep_time=0,
                base_url=base_url[mdl]
            )
            for mdl, role in zip([aff_model, neg_model, judge_model], ["Affirmative Debater", "Negative Debater", "Judge"])
        ]

        meta_prompt = debate_config["meta_prompt"].replace("[Target Text]", debate_config["target_text"]).replace(
            "[code and justification]", str(debate_config["Disagreed"]))
        aff.set_meta_prompt(meta_prompt)
        neg.set_meta_prompt(meta_prompt)
        judge.set_meta_prompt(meta_prompt)

        for _, codebook in enumerate(debate_config["Disagreed"]):
            code, justification = codebook["code"], codebook["justification"]

            aff.event(debate_config["Affirmative Debater"]["round 1"].replace("[code]", code).replace("[justification]", justification))
            aff_r1 = aff.ask()
            aff.memory(aff_r1, True)
            self.display_debate_dialogue("Affirmative R1", "🟢", aff_r1)

            neg.event(debate_config["Negative Debater"]["round 1"].replace("[code]", code).replace("[justification]", justification).replace("opponent_round1", aff_r1))
            neg_r1 = neg.ask()
            neg.memory(neg_r1, True)
            self.display_debate_dialogue("Negative R1", "🔴", neg_r1)

            aff.event(debate_config["Affirmative Debater"]["round 2"].replace("opponent_round1", neg_r1))
            aff_r2 = aff.ask()
            aff.memory(aff_r2, True)
            self.display_debate_dialogue("Affirmative R2", "🟢", aff_r2)

            neg.event(debate_config["Negative Debater"]["round 2"].replace("opponent_round2", aff_r2))
            neg_r2 = neg.ask()
            neg.memory(neg_r2, True)
            self.display_debate_dialogue("Negative R2", "🔴", neg_r2)

            aff.event(debate_config["Affirmative Debater"]["closing"])
            aff_close = aff.ask()
            aff.memory(aff_close, True)
            self.display_debate_dialogue("Affirmative Close", "🟢", to_json(aff_close))

            neg.event(debate_config["Negative Debater"]["closing"])
            neg_close = neg.ask()
            neg.memory(neg_close, True)
            self.display_debate_dialogue("Negative Close", "🔴", to_json(neg_close))

            judge_prompt = debate_config["Judge"].replace("AFF_R1", aff_r1).replace("AFF_R2", aff_r2).replace("NEG_R1", neg_r1).replace("NEG_R2", neg_r2).replace("AFF_CLOSE", aff_close).replace("NEG_CLOSE", neg_close)
            judge.event(judge_prompt)
            jud = judge.ask()
            judge.memory(jud, False)
            judge_response = to_json(jud)
            self.display_debate_dialogue("Judge", "⚖️", json.dumps(judge_response, ensure_ascii=False, indent=2))

            if isinstance(judge_response, dict) and judge_response.get("Resolution") != "Drop":
                CODEBOOK.append({
                    "code": judge_response.get("final_code", ""),
                    "justification": judge_response.get("briefly explain", "")
                })
            del aff.memory_lst[1:]
            del neg.memory_lst[1:]

        return CODEBOOK

    def run(self):
        st.set_page_config(page_title=self.title, layout="centered")
        st.title(self.title)
        user_input = st.chat_input("Input your text here...")
        self.render_model_selectors()
        self.handle_input(user_input)
        # self.render_chat()


def Role(text, model_name):
    role_config["target_text"] = text
    roles = Agents.RoleAgent(
        model_name=model_name,
        config=role_config,
        api_key=api_key[model_name],
        base_url=base_url[model_name]
    )
    meta = roles.single_agents_init()
    _, Annotators = roles.single_agents_codebook(meta)
    return Annotators


def Agree(text, model_name):
    agree_config["target_text"] = text
    agree = Agents.AgreeAgent(
        model_name=model_name,
        config=agree_config,
        api_key=api_key[model_name],
        base_url=base_url[model_name]
    )
    view = agree.agree_agent_codebook()
    return view


if __name__ == "__main__":
    role_config = import_json("config/role_config.json")
    agree_config = import_json("config/agree_config.json")
    debate_config = import_json("config/debate_config.json")

    app = MultiAgents(
        model_registry={
            "Role_Agent": Role,
            "Agree_Agent": Agree
        },
        bot_names=["Role_Agent", "Agree_Agent"],
        bot_avatars=["🔁", "📃"]
    )
    app.run()
