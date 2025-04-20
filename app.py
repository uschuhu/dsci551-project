import streamlit as st
import json
from prompt_engineer import generate_mongo_query, generate_sql_query, if_join_required, summarize_results, mongodb_or_sql
from mongodb_connection import get_mongo_connection
from mysql_connection import get_mysql_connection
from utils import get_sample_documents
import pandas as pd
from sqlalchemy import create_engine, text

# MongoDB Setup
db = get_mongo_connection()
collection_names = db.list_collection_names()
collections = {name: db[name] for name in collection_names}

# Load sample docs for schema reference
sample_docs = get_sample_documents(collections)

# SQL setup
sql_db = get_mysql_connection()
conn = sql_db.connect()
conn.execute(text("USE SocMed;"))

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
    
def execute_sql_query(response_sql, sql_db):
    if response_sql[0:11] == "DESCRIPTIVE":
        return {"success":"Operation successful."}
    try:
        df = pd.read_sql(text(response_sql), sql_db)
        results = sql_db.execute(text(response_sql)).all()
        print(results)
        sql_db.execute(text("commit;"))
        data = [row._mapping for row in results]
        print(data)
        return [row._mapping for row in results]
    except Exception as e:
        e_string = str(e)
        if "does not return rows" in e_string:
            sql_db.execute(text("commit;"))
            return {"success":"Operation successful."}
        else:
            return {"error":"An error occurred. Please try again."}


# ==========================================================
# Streamlit UI
st.set_page_config(page_title="ChatDB", layout="wide")
st.title("ChatDB: Natural Language Interface")

user_question = st.text_input("Ask a question:")

if user_question:
    st.subheader("mongodb or sql?")
    join_response = mongodb_or_sql(user_question, sample_docs)
    st.success(join_response)

    if "MySQL" in join_response:
        st.subheader("sql Query")
        query_str = generate_sql_query(user_question)
        st.code(query_str)

        st.subheader("Query Results")
        results = execute_sql_query(query_str, conn)
        try:
            st.dataframe(pd.DataFrame(results))
        except:
            st.json(results)

    elif "MongoDB" in join_response:
        query_str = generate_mongo_query(user_question, sample_docs)
        st.code(query_str, language="json")

        st.subheader("Query Results")
        results = execute_query(query_str)
        st.json(results)

    try:
        st.subheader("Natural Language Summary")
        summary = summarize_results(user_question, results)
        st.success(summary)
    except:
        st.subheader("Error occurred. Please try again.")