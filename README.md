# SparkifyLLM

This project contains a Language Learning Model (LLM) implementation that uses the GPT-4 model from OpenAI and integrates with PySpark using LangChain for data processing tasks.

## Overview

SparkifyLLM is designed to interact with users and perform operations on a dataframe using LangChain's Spark toolkit. Here are some of the capabilities of the chatbot:

1. **Data Exploration**: The chatbot can answer questions about the data in the dataframe, such as the number of rows, columns, unique values, missing values, and basic statistical properties like mean, median, mode, etc.

2. **Data Manipulation**: The chatbot can perform various data manipulation tasks like filtering, sorting, grouping, and aggregating data based on user queries. It can also add or drop columns, rename columns, and change data types.

3. **Natural Language Processing**: The chatbot understands natural language queries and can translate them into PySpark operations using the langchain tool. This makes it easy for users without a technical background to interact with the data.

Remember, the capabilities of the chatbot are dependent on the capabilities of the underlying LLM. It's always a good idea to test the chatbot with different types of queries to understand its capabilities and limitations.

In addition, there is also a preview tab to view the changes in dataframe from the LLM-run operations.

## Screenshots
<img width="800" alt="Screenshot 2024-04-25 at 10 08 49 AM" src="https://github.com/jeffersonaaron25/sparkify-llm/assets/53298971/ac86a488-d67c-4bc2-a38f-0f56af89bfec">
<img width="800" alt="Screenshot 2024-04-25 at 10 29 36 AM" src="https://github.com/jeffersonaaron25/sparkify-llm/assets/53298971/467f8efd-e226-464f-9d85-9574622ebcd5">


## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License
MIT
