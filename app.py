import streamlit as st
import json
from openai_client import chat
from prompt_engineer import generate_mongo_query, summarize_results
from mongodb_connection import get_mongo_connection
from utils import get_sample_documents

# MongoDB Setup
db = get_mongo_connection()
collection_names = db.list_collection_names()
collections = {name: db[name] for name in collection_names}

# Load sample docs for schema reference
sample_docs = get_sample_documents(collections)

# Execute GPT-generated MongoDB query
def execute_query(response_json):
    try:
        obj = json.loads(response_json)

        if "error" in obj:
            return {"error": obj["error"]}
        
        if "operation" not in obj:
            return {"error": "Missing 'operation' field in response: " + str(obj)}
        
        collection = db[obj["collection"]]

        if obj["operation"] == "explore":
            pass
        elif obj["operation"] == "find":
            results = list(collection.find(obj["filter"], obj.get("projection", {})))
        elif obj["operation"] == "aggregate":
            results = list(collection.aggregate(obj["pipeline"]))
        elif obj["operation"] == "insert":
            pass
        elif obj["operation"] == "update":
            pass
        elif obj["operation"] == "delete":
            pass
        else:
            return {"error": f"Unsupported operation: {obj['operation']}"}
        
        return results
    except Exception as e:
        return {"error": str(e)}

# ==========================================================
# Streamlit UI
st.set_page_config(page_title="ChatDB", layout="wide")
st.title("ChatDB: Natural Language Interface")

user_question = st.text_input("Ask a question about your data:")

if user_question:
    st.subheader("MongoDB Query")
    query_str = generate_mongo_query(user_question, sample_docs)
    st.code(query_str, language="json")

    # # DEBUG
    # st.subheader("Raw GPT output")
    # st.code(query_str)

    st.subheader("Query Results")
    results = execute_query(query_str)
    st.json(results)

    st.subheader("Natural Language Summary")
    summary = summarize_results(user_question, results)
    st.success(summary)