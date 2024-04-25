import streamlit as st
import upload, chat
from llm import LLMAgent

st.set_page_config(layout="centered", page_title="SparkifyLLM", page_icon="💥")

# remove padding from the top and bottom of the page - workaround for streamlit's default padding
st.markdown("""
    <style>
            .block-container {
                padding-top: 1rem;
                padding-bottom: 0rem;
                padding-left: 5rem;
                padding-right: 5rem;
            }
    </style>
    """, unsafe_allow_html=True)

# remove padding from the top and bottom of the sidebar - workaround for streamlit's default padding
st.markdown(
        """
        <style>
        .st-emotion-cache-16txtl3 {
            padding-top: 1rem;
            padding-bottom: 0rem;
            padding-left: 1rem;
            padding-right: 1rem;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

st.title("SparkifyLLM")

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'file_path' not in st.session_state:
    st.session_state.file_path = None
if 'turn' not in st.session_state:
    st.session_state.turn = 0
if 'df' not in st.session_state:
    st.session_state.df = None
if 'temp_df' not in st.session_state:
    st.session_state.temp_df = None

if "df" not in st.session_state or (
    "df" in st.session_state and st.session_state.df is None
    ):
    # Load the file if df is not in session state
    success = upload.get_upload()
    if success:
        # trigger streamlit rerun to display the chat interface
        st.rerun()

if "df" in st.session_state and st.session_state.df:
    # sidebar for data preview
    st.sidebar.header("Data Preview", divider='red')
    st.sidebar.markdown("<p style='font-size:14px; color: grey; margin-top: -10px;'>Click to toggle between source and scratch dataframes</p>", unsafe_allow_html=True)
    st.sidebar.markdown("<p style='font-size:14px; color: grey; margin-top: -15px;'>Source: Data loaded from the CSV file. Scratch: Data after operations.</p>", unsafe_allow_html=True)

    preview_scratch = st.sidebar.toggle('Scratch', True)
    if preview_scratch:
        st.sidebar.dataframe(st.session_state.temp_df)
        st.sidebar.markdown("<p style='text-align: center; color: grey; margin-top: -10px;'>Scratch</p>", unsafe_allow_html=True)
        st.sidebar.markdown("<p style='text-align: center; font-size: 10px; color: grey; margin-top: -15px;'>To keep changes for following queries, save the scratch dataframe.</p>", unsafe_allow_html=True)
        if st.sidebar.button("Save Scratch Dataframe", type='primary', use_container_width=True):
            st.session_state.temp_df.write.csv("scratch.csv", header=True, mode="overwrite")
            st.toast('Scratch saved!')
    else:
        st.sidebar.dataframe(st.session_state.df)
        st.sidebar.markdown("<p style='text-align: center; color: grey; margin-top: -10px;'>Source</p>", unsafe_allow_html=True)
    
    # initialize the LLM agent
    if 'llm' not in st.session_state or (
        'llm' in st.session_state and st.session_state.llm == None
    ):
        llm = LLMAgent(st.session_state.df, st.session_state.file_path)
        st.session_state.llm = llm
    chat.app(st.session_state.llm)
