import os
import streamlit as st
import re
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.exc import ProgrammingError
from langchain.chains import create_sql_query_chain
from langchain_community.utilities import SQLDatabase
from langchain_groq import ChatGroq

# Load environment variables
load_dotenv()

# --- Database Configuration ---
db_user = "root"
db_password = "*******"
db_host = "localhost"
db_name = "retail_sales_db"

# --- SQLAlchemy Engine ---
engine = create_engine(f"mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}")

# --- LangChain SQL Database Utility ---
db = SQLDatabase(engine, sample_rows_in_table_info=3)

# --- LLM Initialization ---
llm = ChatGroq(
    temperature=0,
    model_name="llama3-70b-8192",
    api_key="gsk_6z5zIMw*******5kO5sj6h18yN71qUyhVmhvC"
)

# --- SQL Query Chain ---
chain = create_sql_query_chain(llm, db)

# --- Function to Execute Question as SQL Query ---
def execute_query(question):
    try:
        # Get SQL query from LLM
        response = chain.invoke({"question": question})

        # Extract SQL from response using regex
        match = re.search(r"SELECT .*", response, re.IGNORECASE | re.DOTALL)
        cleaned_query = match.group(0).strip() if match else None

        if cleaned_query:
            # Run the SQL query
            result = db.run(cleaned_query)
            return cleaned_query, result
        else:
            st.warning("No valid SQL query was generated.")
            return None, None

    except ProgrammingError as e:
        st.error(f"SQL Error: {e}")
        return None, None

# --- Streamlit App Interface ---
st.title("🧠 Natural Language to SQL App")
st.markdown("Ask a question in plain English and get answers from your MySQL database.")

# User input
question = st.text_input("Enter your question:")

# Execute button
if st.button("Execute"):
    if question:
        query, result = execute_query(question)
        
        if query and result is not None:
            st.subheader("🔍 Generated SQL Query")
            st.code(query, language="sql")
            
            st.subheader("📊 Query Result")
            st.write(result)
        else:
            st.info("No results found or there was an error.")
    else:
        st.warning("Please enter a question to proceed.")
