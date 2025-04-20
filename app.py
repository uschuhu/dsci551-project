import streamlit as st
import json
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
        print(obj)

        if "error" in obj:
            return {"error": obj["error"]}
        
        if "operation" not in obj:
            return {"error": "Missing 'operation' field in response: " + str(obj)}
                
        if obj["operation"] == "explore":
            try:
                collections = db.list_collection_names()
                return {"collections": collections}
            except Exception as e:
                return {"error": str(e)}

        collection = db[obj["collection"]]

        if obj["operation"] == "find":
            try:
                results = list(collection.find(obj["filter"], obj.get("projection", {})))
                return results
            except Exception as e:
                return {"error": str(e)}
            
        elif obj["operation"] == "aggregate":
            try:
                results = list(collection.aggregate(obj["pipeline"]))
                return results
            except Exception as e:
                return {"error": str(e)}

        elif obj["operation"] == "insert":
            try:
                if isinstance(obj["document"], list):
                    insert_result = collection.insert_many(obj["document"])
                    return {"inserted_ids": [str(i) for i in insert_result.inserted_ids]}
                else:
                    insert_result = collection.insert_one(obj["document"])
                    return {"inserted_id": str(insert_result.inserted_id)}
            except Exception as e:
                return {"error": str(e)}
            
        elif obj["operation"] == "update":
            try:
                if obj.get("many", False):
                    update_result = collection.update_many(obj["filter"], obj["update"])
                else:
                    update_result = collection.update_one(obj["filter"], obj["update"])
                return {
                    "matched_count": update_result.matched_count,
                    "modified_count": update_result.modified_count
                }
            except Exception as e:
                return {"error": str(e)}

        elif obj["operation"] == "delete":
            try:
                if obj.get("many", False):
                    delete_result = collection.delete_many(obj["filter"])
                else:
                    delete_result = collection.delete_one(obj["filter"])
                return {"deleted_count": delete_result.deleted_count}
            except Exception as e:
                return {"error": str(e)}
        else:
            return {"error": f"Unsupported operation: {obj['operation']}"}
            
    except Exception as e:
        return {"error": str(e)}

# ==========================================================
# Streamlit UI
st.set_page_config(page_title="ChatDB", layout="wide")
st.title("ChatDB: Natural Language Interface")

user_question = st.text_input("Ask a question:")

if user_question:
    st.subheader("MongoDB Query")
    query_str = generate_mongo_query(user_question, sample_docs)
    st.code(query_str, language="json")

    st.subheader("Query Results")
    results = execute_query(query_str)
    st.json(results)

    st.subheader("Natural Language Summary")
    summary = summarize_results(user_question, results)
    st.success(summary)