import streamlit as st
import sys
import os
from LLMsTeamDebate import MultiAgentsDebate

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.append(project_root)
from config.debate_menu import *
from utils.Function import import_json


class MultiAgentsHumanDebate(MultiAgentsDebate):
    def __init__(self, debate_config, models_name):
        super().__init__(debate_config, models_name)
        self.title = "LLM-Human Team Debate"
        st.session_state.debate_models = models_name

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
            self.render_human_selectors()

    def render_human_selectors(self):
        self.render_divider()
        st.markdown("Human")
        input_container1 = st.empty()
        input_container2 = st.empty()
        input_container3 = st.empty()

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

            st.markdown(self.white_background_div(text1), unsafe_allow_html=True)

            st.markdown("Disciplinary Background", unsafe_allow_html=True)
            st.markdown(self.white_background_div(text2), unsafe_allow_html=True)

            st.markdown("Core Value", unsafe_allow_html=True)
            st.markdown(self.white_background_div(text3), unsafe_allow_html=True)
        st.markdown("Positionality Statement")
        st.markdown(st.session_state.roles_positionality[2])

    def white_background_div(self, content):
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


if __name__ == "__main__":
    debate_config = import_json("config/debate_config.json")
    models_name = {
        "Role1": "deepseek-chat",
        "Role2": "deepseek-chat",
        "Human": "deepseek-chat",
        "Facilitator": "deepseek-chat",
    }
    app = MultiAgentsHumanDebate(debate_config, models_name)
    app.run()
