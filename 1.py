import streamlit as st

import json
import numpy as np
import random
import time
# with st.chat_message("assistant"):
#     st.write("Hello human")
#     st.bar_chart(np.random.randn(30, 3))

# message = st.chat_message("assistant")
# message.write("Hello human")
# message.bar_chart(np.random.randn(30, 3))

# prompt = st.chat_input("Say something")
# if prompt:
#     st.write(f"User has sent the following prompt: {prompt}")


# Streamed response emulator
# def response_generator():
#     response = random.choice(
#         [
#             "Hello there! How can I assist you today?",
#             "Hi, human! Is there anything I can help you with?",
#             "Do you need help?",
#         ]
#     )
#     for word in response.split():
#         yield word + " "
#         time.sleep(0.05)
#
# st.title("Echo Bot")
#
# # Initialize chat history
# if "messages" not in st.session_state:
#     st.session_state.messages = []
#
# # Display chat messages from history on app rerun
# for message in st.session_state.messages:
#     with st.chat_message(message["role"]):
#         st.markdown(message["content"])
#
# # React to user input
# if prompt := st.chat_input("What is up?"):
#     # Display user message in chat message container
#     with st.chat_message("user"):
#         st.markdown(prompt)
#     # Add user message to chat history
#     st.session_state.messages.append({"role": "user", "content": prompt})
#
#     # Display assistant response in chat message container
#     with st.chat_message("assistant"):
#         response = st.write_stream(response_generator())
#     # Add assistant response to chat history
#     st.session_state.messages.append({"role": "assistant", "content": response})
reply = {
    "role1": "Software Developer",
    "disciplinary_background": "Computer Science / Software Engineering",
    "perspective": "Focuses on technical details, coding practices, tools, and frameworks mentioned in the interviews. Will pay attention to challenges in implementation, debugging, and optimization."
  }

pretty_json = json.dumps(reply, indent=2, ensure_ascii=False)
st.code(pretty_json, language="json")