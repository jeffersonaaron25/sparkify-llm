import streamlit as st
from pyspark.sql import SparkSession
import shutil
import os

spark = SparkSession.getActiveSession()
if not spark:
    spark = SparkSession.builder.getOrCreate()

def get_upload():
    # file_path = st.text_input("Enter the path to your CSV file")
    file = st.file_uploader("Upload a CSV file", type=["csv"])
    if file:
        try:
            shutil.rmtree('scratch.csv')
            shutil.rmtree('temp.csv')
            shutil.rmtree('sparkify')
        except:
            pass
        # create a directory
        os.makedirs('sparkify', exist_ok=True)
        file_name = 'sparkify/'+file.name
        with open(file_name, "wb") as f:
            f.write(file.getbuffer())
        # Read CSV file with Spark
        try:
            with st.spinner("Loading file..."):
                df = spark.read.csv(file_name, header=True, inferSchema=True)
            st.session_state.file_path = file_name
            st.success("File loaded and converted to Spark DataFrame successfully!")
            st.dataframe(df, width=600, height=350)
            api_key = st.text_input("Enter OpenAI API Key to Start Chat")
            st.write("Don't have an API Key? Get one [here](https://platform.openai.com/signup). We do not store your API Key.")
            st.markdown("<br />", unsafe_allow_html=True)
            # if st.button("Start Chat") and st.session_state.df is None:
            if api_key and st.session_state.df is None:
                os.environ["OPENAI_API_KEY"] = api_key
                st.session_state.df = df
                st.session_state.temp_df = df
                df.write.csv("scratch.csv", header=True, mode="overwrite")
                df.write.csv("temp.csv", header=True, mode="overwrite")
                return True
        except Exception as e:
            print(e)
            st.error("Error loading file. Please check the file path and try again.")