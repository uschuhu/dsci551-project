import json
from openai_client import chat

def generate_mongo_query(user_question, sample_docs):
    # system_prompt = f"""
    # You are a MongoDB expert. Given the user's natural language input, choose the correct collection(s) and convert it into a valid MongoDB query.

    # Requirements:
    # - Always return a JSON query.
    # - Use filter and projection in all queries.
    # - Ignore _id in projection.
    # - Infer the right collection(s) based on user intent.
    
    # Reference this schema for the data structure and collection names:
    # {sample_docs}
    # """

    system_prompt = f"""
    You are a MongoDB expert. Your job is to convert a user's natural language question into a valid MongoDB operation in JSON format.

    Always return a JSON object with the following fields:
    - "operation": One of ["explore", "find", "aggregate", "insert", "update", "delete"]
    - "collection": the name of the main collection to query
    - "filter": (only for 'find' or 'delete') the query conditions
    - "projection": (only for 'find') the fields to include or exclude (always exclude '_id')
    - "pipeline": (only for 'aggregate') a valid aggregation pipeline including any $match, $group, $sort, $project, $limit, $lookup, etc.
    - "document": (only for 'insert') the document to be inserted
    - "update": (only for 'update') the update to apply (use $set, etc.)

    Always include the "operation" field.
    Only use "explore" when none of the other operations apply.
    Infer the correct collection(s) based on the question and data structure. Use $lookup for joining collections when needed.

    Use this example of the database schema for context:
    {sample_docs}
    """

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_question}
    ]
    try:
        return chat(messages)
    except Exception as e:
        return json.dumps({"error": str(e)})
    
def summarize_results(question, result):
    prompt = [
        {"role": "system", "content": f"Answer the user question concisely using the following MongoDB result:\n\n{result}"},
        {"role": "user", "content": question}
    ]
    return chat(prompt, max_tokens=100)