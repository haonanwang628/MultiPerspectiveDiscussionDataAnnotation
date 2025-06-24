import streamlit as st
import os
import sys
import json
import time

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.append(project_root)
from utils.Agent import Agent


class SingleAgents:

    def __init__(self, model_registry, default_models, bot_names, bot_avatars, user_avatar="🧑‍💻"):
        """
        model_registry: Dict[str, Callable]，如 {'GPT-4': func1, 'Claude': func2, ...}
        default_models: List[str]，每个Bot的默认模型名
        bot_names / bot_avatars: 每个Bot的昵称和头像
        """
        self.model_registry = model_registry
        self.default_models = default_models
        self.bot_names = bot_names
        self.bot_avatars = bot_avatars
        self.user_avatar = user_avatar
        self.title = "🤖 Single Agents"
        self.init_session()

    def init_session(self):
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []  # {"role", "name", "avatar", "content"}
        if "bot_models" not in st.session_state:
            st.session_state.bot_models = self.default_models.copy()

    def render_chat(self):
        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                self.render_user_message(msg["content"])
            else:
                self.render_bot_message(msg["name"], msg["avatar"], msg["content"])

    def render_user_message(self, text):
        st.markdown(
            f"""
            <div style='display: flex; justify-content: flex-end; align-items: center; margin: 6px 0;'>
                <div style='background-color: #DCF8C6; padding: 10px 14px; border-radius: 10px; max-width: 70%; text-align: right;'>
                    {text}
                </div>
                <div style='font-size: 24px; margin-left: 8px;'>{self.user_avatar}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    def render_bot_message(self, name, avatar, text):
        st.markdown(
            f"""
            <div style='display: flex; justify-content: flex-start; align-items: center; margin: 6px 0;'>
                <div style='font-size: 24px; margin-right: 8px;'>{avatar}</div>
                <div style='background-color: #F1F0F0; padding: 10px 14px; border-radius: 10px; max-width: 70%; text-align: left;'>
                    <b>{name}:</b> {text}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    def render_model_selectors(self, active_bots):
        with st.sidebar:
            st.subheader("🤖 Bot Model Settings")
            for i in range(active_bots):
                selected_model = st.selectbox(
                    label=f"Select model for {self.bot_names[i]}",
                    options=list(self.model_registry.keys()),
                    index=list(self.model_registry.keys()).index(self.default_models[i]),
                    key=f"model_select_{i}"
                )
                st.session_state.bot_models[i] = selected_model

    def handle_input(self, active_bots, user_input):
        if user_input:
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            for i in range(active_bots):
                model_name = st.session_state.bot_models[i]
                bot_func = self.model_registry[model_name]
                bot_name = f"{self.bot_names[i]} ({model_name})"
                bot_avatar = self.bot_avatars[i]

                reply = bot_func(user_input)
                st.session_state.chat_history.append({
                    "role": f"bot{i + 1}",
                    "name": f"{self.bot_names[i]} ({model_name})",
                    "avatar": self.bot_avatars[i],
                    "content": reply
                })

    def run(self):
        st.set_page_config(page_title=self.title, layout="centered")
        st.title(self.title)
        user_input = st.chat_input("Input your text here...")
        num_bots = st.sidebar.selectbox("🧠 How many Agents?", [1, 2, 3, 4], index=1)
        self.render_model_selectors(num_bots)
        self.handle_input(num_bots, user_input)
        self.render_chat()


# Add API(TBD)
def gpt3_5(text): return f"{text[::-1]}"


def gpt4(text): return f"{text[:len(text) // 2]}..."


def claude(text): return f"I see you're thinking: {text.upper()} 🤔"


def deepseek(text):
    agent = Agent(
        model_name="deepseek-chat",
        name="deepseek",
        api_key="sk-9bc06d1289704b05b7b52db5285dba67",
        base_url="https://api.deepseek.com/v1"
    )
    agent.event(text)
    response = agent.ask()

    return response


if __name__ == "__main__":
    api_key = {"deepseek-chat": "sk-9bc06d1289704b05b7b52db5285dba67", "GPT-3.5": "", "GPT-4": "", "Claude": ""}
    base_url = {"deepseek-chat": "https://api.deepseek.com/v1", "GPT-3.5": "", "GPT-4": "", "Claude": ""}
    app = SingleAgents(
        model_registry={
            "GPT-3.5": gpt3_5,
            "GPT-4": gpt4,
            "Claude": claude,
            "deepseek-chat": deepseek
        },
        default_models=["GPT-3.5", "GPT-4", "Claude", "deepseek-chat"],
        bot_names=["Agent1", "Agent2", "Agent3", "Agent4"],
        bot_avatars=["🌀", "📘", "🧠", "🌀"]
    )
    app.run()
