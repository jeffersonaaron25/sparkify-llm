import re
import streamlit as st
import shutil

def app(llm):
    start_message = "Hello! I am Sparkify, your data assistant. Ask me any question on your data. You can also ask me to perform spark operations on your data. Keep in mind, complex operations can take time. I'm improving myself constantly, so please be patient with me. Let's get started!"
    if st.button("New Chat"):
        # Reset session state
        st.session_state.chat_history = []
        st.session_state.chart_history = {}
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

    for idx in range(len(st.session_state.chat_history)):
        role, avatar, message, chart = st.session_state.chat_history[idx]
        # Display the chat messages from the chat history
        st.chat_message(role, avatar=avatar).write(message)
        if chart:
            chart_data = st.session_state.chart_history[idx]
            chart_data = {key.replace('(', ' ('): value for key, value in chart_data.items()}


        if chart in ['bar_chart']:
            st.chat_message(role, avatar=avatar).bar_chart(data=chart_data, x=list(chart_data.keys())[0], y=list(chart_data.keys())[1:])
        if chart in ['line_chart']:
            st.chat_message(role, avatar=avatar).line_chart(data=chart_data,  x=list(chart_data.keys())[0], y=list(chart_data.keys())[1:])
        if chart in ['area_chart']:
            st.chat_message(role, avatar=avatar).area_chart(data=chart_data,  x=list(chart_data.keys())[0], y=list(chart_data.keys())[1:])

    if 'turn' not in st.session_state:
        st.session_state.turn = 0

    if st.session_state.turn == 0:
        # Display the start message when turn is 0
        st.session_state.chat_history.append(("assistant", "💥", start_message, None))
        st.session_state.turn += 1
        role, avatar, message, chart = st.session_state.chat_history[-1]
        st.chat_message(role, avatar=avatar).write(message)
    
    user_input = None
    user_input = st.chat_input("Enter your message")

    if user_input:
        st.session_state.chat_history.append(("human", "🙋🏽‍♂️", user_input, None))
        # Display the user input
        role, avatar, message, chart = st.session_state.chat_history[-1]
        st.chat_message(role, avatar=avatar).write(message)

        with st.spinner("Sparkify in action..."):
            progress = st.progress(20, "Gathering my thoughts...")
            llm_response = llm.get_llm_response(user_input, progress)
            progress.empty()
        
        chart = None

        chart_types = ['bar_chart::', 'line_chart::', 'area_chart::']
        pattern = '|'.join(chart_types)

        match = re.search(pattern, llm_response)
        if match:
            chart = match.group().replace('::', '')
            llm_response = llm_response[match.end():]
            chart_data = st.session_state.scratch_df.toPandas().to_dict(orient='list')
            chart_data = {key.replace('(', ' ('): value for key, value in chart_data.items()}
            st.session_state.chart_history[len(st.session_state.chat_history)] = chart_data
            
        st.session_state.chat_history.append(("assistant", "💥", llm_response, chart))
        # Refresh app to get latest scratch dataframe
        st.rerun()
