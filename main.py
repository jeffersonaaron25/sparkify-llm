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

# Adjust page and sidebar width
st.markdown(
    """
    <style>
        section[data-testid="stSidebar"] {
            width: 50% !important;
            max-width: 50% !important; # Set the width to your desired value
        }
        button[data-testid="baseButton-header"] {
            display: none;
        }
    </style>
    """,
    unsafe_allow_html=True,
)
st.markdown("""
    <style>
        section.main > div {max-width:60rem}
    </style>
    """, unsafe_allow_html=True)

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
if 'scratch_df' not in st.session_state:
    st.session_state.scratch_df = None
if 'spark' not in st.session_state:
    st.session_state.spark = None

if "df" not in st.session_state or (
    "df" in st.session_state and st.session_state.df is None
    ):
    st.markdown("<p style='color: grey; margin-top: -10px;'>From Jefferson | <a href='https://github.com/jeffersonaaron25'>GitHub</a> | <a href='https://www.linkedin.com/in/jeffersonaaron/'>LinkedIn</a></p>", unsafe_allow_html=True)
    # Load the file if df is not in session state
    success = upload.get_upload()
    if success:
        # trigger streamlit rerun to display the chat interface
        st.rerun()

if "df" in st.session_state and st.session_state.df:
    # sidebar for data preview
    st.sidebar.header("Data Preview (Upto First 1000 Rows)", divider='red')
    st.sidebar.markdown("<p style='font-size:14px; color: grey; margin-top: -10px;'>Click to toggle between source and scratch dataframes</p>", unsafe_allow_html=True)
    st.sidebar.markdown("<p style='font-size:14px; color: grey; margin-top: -15px;'>Source: Data loaded from the CSV file. Scratch: Data after operations.</p>", unsafe_allow_html=True)

    preview_scratch = st.sidebar.toggle('Scratch', True)
    if preview_scratch:
        st.sidebar.dataframe(st.session_state.scratch_df.limit(1000), use_container_width=True)
        st.sidebar.markdown("<p style='text-align: center; color: grey; margin-top: -10px;'>Scratch</p>", unsafe_allow_html=True)
        st.sidebar.markdown("<p style='text-align: center; font-size: 10px; color: grey; margin-top: -15px;'>To keep changes for following queries, save the scratch dataframe.</p>", unsafe_allow_html=True)
        b1, b2, b3 = st.sidebar.columns(3)
        with b1:
            if st.button("Reset Scratch", type='secondary', use_container_width=True):
                st.session_state.scratch_df = st.session_state.spark.read.csv("temp.csv", header=True, inferSchema=True)
                st.rerun()
        with b2:
            if st.button("Reset Scratch from Source", type='secondary', use_container_width=True):
                st.session_state.scratch_df = st.session_state.df
                st.session_state.df.write.csv("scratch.csv", header=True, mode="overwrite")
                st.session_state.df.write.csv("temp.csv", header=True, mode="overwrite")
                st.rerun()
        with b3:
            if st.button("Save Scratch", type='primary', use_container_width=True):
                try:
                    st.session_state.scratch_df.write.csv("temp.csv", header=True, mode="overwrite")
                    st.toast('Scratch saved!')
                except:
                    st.error('Error saving scratch! If this persists, consider restarting session.')
        
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
