from langchain_experimental.agents.agent_toolkits import create_spark_dataframe_agent
from langchain_openai import ChatOpenAI
from pyspark.sql import SparkSession
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain.tools import tool
import streamlit as st

_progress = None
spark = SparkSession.getActiveSession()

@tool
def sparkify(text):
    """Run spark tool"""
    try:
        global _progress
        global spark
        if not spark:
            spark = st.session_state.spark
        _progress.progress(60, "Working on it...")
        _df = spark.read.csv('temp.csv', header=True, inferSchema=True)
        spark_tool = create_spark_dataframe_agent(llm=ChatOpenAI(temperature=0, model="gpt-4-turbo"), df=_df, verbose=False)
        instruct_prompt = f"""
You are Sparkify, a PySpark expert and executor. You can use the spark dataframe 'df' to answer questions about the data. You must save the dataframe to a temp file 'scratch.csv' after the operation.
Follow all the rules below, you cannot deviate from them ever.

Rules:
1. Any question that can be answered by the dataframe should be answered by the dataframe.
2. You must provide an response to the question with the relevant answer.
3. All operations must be chained. Save df only if human asks you to. Save MUST be chained with other operations. Save will not work if its not chained with other operations or if in another action. Save must include header.
4. You must provide output from df in the response if required by the question.
5. If the question requires a visualization, start response exactly with 'bar_chart::', 'line_chart::', or 'area_chart::'.

Dont's:
Respond "The analysis has been saved in a file named 'scratch.csv'." if question requires the output.
The human cannot see any data you display using df.show(). So, do not answer with respect to that.
Never respond with any data. Data must be saved in 'scratch.csv'. Respond with the operation done.

Do's:
Always format the output of df.show() as per the question in your response. Preferably in a table.
Use df.write.csv("scratch.csv", header=True, mode="overwrite") to save the dataframe.
Any operation done on the dataframe MUST be saved in 'scratch.csv'.

Text: {text}
"""
        return spark_tool.invoke(instruct_prompt)
    except Exception as e:
        return "Oops something went wrong."

class LLMAgent():
    def __init__(self, df, file_path) -> None:
        self.df = df
        self.file_path = file_path
        self.llm = ChatOpenAI(model="gpt-4-turbo")
        # Create an agent executor by passing in the agent and tools
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    self.get_prompt(self.df, self.file_path),
                ),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ]
        )
        self.agent = create_tool_calling_agent(self.llm, [sparkify], prompt)
        self.agent_executor = AgentExecutor(agent=self.agent, tools=[sparkify], verbose=True)
        self.ephemeral_chat_history_for_chain = ChatMessageHistory()
        self.conversational_agent_executor = RunnableWithMessageHistory(
            self.agent_executor,
            lambda session_id: self.ephemeral_chat_history_for_chain,
            input_messages_key="input",
            output_messages_key="output",
            history_messages_key="chat_history",
        )

    def get_prompt(self, df, path):
        columns = df.columns
        first_two_rows = df.head(2)
        first_two_rows_str = "\n".join([str(row) for row in first_two_rows])

        systemn_prompt = f"""
You are a Sparkify, helpful data analytics assistant. You have a 'sparkify' tool that runs spark operations on the dataframe.

Dataframe has the following columns: 
{columns}

First two rows of the dataframe are: 
{first_two_rows_str}

You may choose not to use the tool if you dont require a spark operation for the question. For example: Sometimes you may find the information
needed to answer a question in message history, or sometimes the question may not be about the data {path}.

When instructing sparkify tool, you must use the following rules:
1. Be direct about the operation you want to perform on the dataframe.
2. Give required information to perform the operation. You may use message history for this if needed.
3. If sparkify doesnt provide the required information, you may ask the user for more information.
4. If sparkify doesnt give data in the response and the human's question would be better answered by it, you may ask sparkify again.
5. Clearly specify sparkify to also visualize the result if needed. Sparkify must mention chart_type. Use the chart_type:: as the beginning of your response. Only allowed chart types are bar_chart::, line_chart::, and area_chart::.
6. Do not omit any information from human's question when instructing sparkify.
7. Do not ask ANY excess information from human without making sure it cannot be answered by the dataframe.
8. Sometimes human might not explain the question properly, you may ask for clarification if needed.
9. DO NOT MENTION 'scratch.csv'. Refer to scratch.csv as 'Scratch' in your responses.
"""
        return systemn_prompt
    
    def get_llm_response(self, user_input, progress):
        global _progress
        global spark
        _progress = progress
        if not spark:
            spark = st.session_state.spark
            if not spark:
                spark = SparkSession.builder.getOrCreate()
                st.session_state.spark = spark
        try:
            res = self.conversational_agent_executor.invoke(
                {
                    "input": user_input,
                },
                {"configurable": {"session_id": "streamlit-llm-session"}},
            )['output']
            progress.progress(80, "Putting things together...")
            # Read the temp dataframe and save it in session state after Sparkify operation
            st.session_state.scratch_df = spark.read.csv("scratch.csv", header=True, inferSchema=True)
            progress.progress(100, "Done!")
            return res
        except Exception:
            return "Oops, something went wrong."