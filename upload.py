import streamlit as st
from pyspark.sql import SparkSession
import shutil
import os

spark = SparkSession.getActiveSession()
if not spark:
    spark = SparkSession.builder.getOrCreate()
    st.session_state.spark = spark

def get_upload():
    file = st.file_uploader("Upload a CSV file to get started", type=["csv"])
    if file:
        try:
            # remove previous files
            shutil.rmtree('temp.csv')
            shutil.rmtree('scratch.csv')
            shutil.rmtree('sparkify')
        except:
            pass
        # create a directory
        os.makedirs('sparkify', exist_ok=True)
        file_name = 'sparkify/'+file.name
        # Save file from streamlit file object to disk
        with open(file_name, "wb") as f:
            f.write(file.getbuffer())
        try:
            with st.spinner("Loading file..."):
                # Read CSV file with Spark
                df = spark.read.csv(file_name, header=True, inferSchema=True)
            st.session_state.file_path = file_name
            st.success("File loaded and converted to Spark DataFrame successfully!")
            st.write("Data Preview (Upto First 10 Rows)")
            st.dataframe(df.limit(1000), width=600, height=350, use_container_width=True)
            api_key = st.text_input("Enter OpenAI API Key to Start Chat")
            st.write("Don't have an API Key? Get one [here](https://platform.openai.com/signup). We do not store your API Key.")
            st.markdown("<br />", unsafe_allow_html=True)
            if api_key and st.session_state.df is None:
                os.environ["OPENAI_API_KEY"] = api_key
                st.session_state.df = df
                st.session_state.scratch_df = df
                # scratch is displayed on the right side of the screen, sparkify saved data to scratch
                df.write.csv("scratch.csv", header=True, mode="overwrite")
                # temp is used to store the current state of the dataframe, temp is fed into sparkify
                df.write.csv("temp.csv", header=True, mode="overwrite")
                return True
        except Exception as e:
            st.error("Error loading file. Please check the file path and try again.")