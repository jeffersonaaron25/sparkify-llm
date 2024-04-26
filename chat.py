import streamlit as st
import shutil

def app(llm):
    start_message = "Hello! I am Sparkify, your data assistant. Ask me any question on your data. You can also ask me to perform spark operations on your data. Keep in mind, complex operations can take time. I'm improving myself constantly, so please be patient with me. Let's get started!"
    if st.button("New Chat"):
        # Reset session state
        st.session_state.chat_history = []
        st.session_state.df = None
        st.session_state.scratch_df = None
        st.session_state.llm = None
        st.session_state.turn = 0
        try:
            # remove previous files
            shutil.rmtree('temp.csv')
            shutil.rmtree('scratch.csv')
            shutil.rmtree('sparkify')
        except:
            pass
        st.session_state.file_path = None
        st.rerun()
    
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

    for role, avatar, message in st.session_state.chat_history:
        # Display the chat messages from the chat history
        st.chat_message(role, avatar=avatar).write(message)

    if 'turn' not in st.session_state:
        st.session_state.turn = 0

    if st.session_state.turn == 0:
        # Display the start message when turn is 0
        st.session_state.chat_history.append(("assistant", "💥", start_message))
        st.session_state.turn += 1
        role, avatar, message = st.session_state.chat_history[-1]
        st.chat_message(role, avatar=avatar).write(message)
    
    user_input = None
    user_input = st.chat_input("Enter your message")

    if user_input:
        st.session_state.chat_history.append(("human", "🙋🏽‍♂️", user_input))
        # Display the user input
        role, avatar, message = st.session_state.chat_history[-1]
        st.chat_message(role, avatar=avatar).write(message)

        with st.spinner("Sparkify in action..."):
            progress = st.progress(20, "Gathering my thoughts...")
            llm_response = llm.get_llm_response(user_input, progress)
            progress.empty()
        
        st.session_state.chat_history.append(("assistant", "💥", llm_response))
        # Display the assistant response
        role, avatar, message = st.session_state.chat_history[-1]
        st.chat_message(role, avatar=avatar).write(message)
        # Refresh app to get latest scratch dataframe
        st.rerun()
