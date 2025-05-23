import json
from openai_client import chat

def generate_mongo_query(user_question, sample_docs, max_post_id):
    system_prompt = f"""
    You are a MongoDB expert. Your job is to convert a user's natural language question into a valid MongoDB operation in JSON format.

    Always return a JSON object with the following fields:
    - "operation": One of ["explore", "find", "aggregate", "insertOne", "insertMany", "updateOne", "updateMany", "deleteOne", "deleteMany]
    - "collection": the name of the main collection to query
    - "filter": (only for 'find' or 'delete') the query conditions
    - "projection": (only for 'find') the fields to include or exclude (always exclude '_id')
    - "pipeline": (only for 'aggregate') a valid aggregation pipeline including any $match, $group, $sort, $project, $limit, $lookup, etc.
    - "document": (only for 'insert') the document to be inserted
    - "update": (only for 'update') the update to apply (use $set, etc.)

    Always include the "operation" field.
    Only use "explore" when none of the other operations apply.
    Infer the correct collection(s) based on the question and data structure. Use $lookup for joining collections when needed.
    When inserting new posts, make the new "post_id" = {max_post_id} + 1

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
        {"role": "system", "content": f"Answer the user question concisely, in natural language, using the following MongoDB or SQL result:\n\n{result}. If the result is empty, answer 'Empty Result'"},
        {"role": "user", "content": question}
    ]
    return chat(prompt, max_tokens=400)

def generate_sql_query(user_question):

    system_prompt = f"""
    You are an SQL expert. Your job is to convert a user's natural language question into a valid MySQL query for AWS RDS. If you are asked to describe the overall structure of the tables,
    respond in natural language, and start responses with the word "DESCRIPTIVE: ". Otherwise, output only the raw text of the SQL query.

    Read the database schema from the following SQL table creation statement:
    CREATE TABLE `Users` (
    `USER_ID` INT,
    `HANDLE` VARCHAR(32) NOT NULL,
    `PASSWORD` VARCHAR(255) NOT NULL,
    `EMAIL` VARCHAR(255) NOT NULL,
    PRIMARY KEY (`USER_ID`)
    );

    CREATE TABLE `Posts` (
    `POST_ID` VARCHAR(50),
    `USER_ID` INT,
    PRIMARY KEY (`POST_ID`),
    FOREIGN KEY (`USER_ID`) REFERENCES `Users`(`USER_ID`) ON UPDATE CASCADE ON DELETE CASCADE
    );

    CREATE TABLE `Follows` (
    `FOLLOWER` VARCHAR(32),
    `FOLLOWING` VARCHAR(32),
    PRIMARY KEY (`FOLLOWER`, `FOLLOWING`),
    FOREIGN KEY (`FOLLOWER`) REFERENCES `Users`(`USER_ID`) ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (`FOLLOWING`) REFERENCES `Users`(`USER_ID`) ON UPDATE CASCADE ON DELETE CASCADE
    );
    """

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_question}
    ]
    try: return chat(messages)
    except Exception as e:
        return str(e)
    
def if_join_required(user_question, sample_docs):
    system_prompt = f"""
    You are a MongoDB and MySQL expert. You will read a prompt in natural language and decide if a CROSS-DATABASE JOIN between the MongoDB database and MySQL database is required to complete a query.
    Do not require a CROSS-DATABASE JOIN if the tables are in the same database, i.e. if the JOIN is between two MongoDB documents or two MySQL tables.
    The MongoDB database only has three collections: likes, posts, and comments. 
    The MongoDB database does not have a Users collection.
    The MySQL database only has three tables: Users, Posts, and Follows. 
    
    Read the database schema from the following SQL table creation statement:
    CREATE TABLE `Users` (
    `USER_ID` INT,
    `HANDLE` VARCHAR(32) NOT NULL,
    `PASSWORD` VARCHAR(255) NOT NULL,
    `EMAIL` VARCHAR(255) NOT NULL,
    PRIMARY KEY (`USER_ID`)
    );

    CREATE TABLE `Posts` (
    `POST_ID` VARCHAR(50),
    `USER_ID` INT,
    PRIMARY KEY (`POST_ID`),
    FOREIGN KEY (`USER_ID`) REFERENCES `Users`(`USER_ID`) ON UPDATE CASCADE ON DELETE CASCADE
    );

    CREATE TABLE `Follows` (
    `FOLLOWER` VARCHAR(32),
    `FOLLOWING` VARCHAR(32),
    PRIMARY KEY (`FOLLOWER`, `FOLLOWING`),
    FOREIGN KEY (`FOLLOWER`) REFERENCES `Users`(`USER_ID`) ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (`FOLLOWING`) REFERENCES `Users`(`USER_ID`) ON UPDATE CASCADE ON DELETE CASCADE
    );

    Read the key names from the sample documents for MongoDB: {sample_docs}

    Given the above instructions and MySQL and MongoDB structures, is a join between MySQL and MongoDB required? 
    Should the answer be returned in a tabular MySQL format or a MongoDB JSON document? 

    """

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_question}
    ]
    try:
        return chat(messages)
    except Exception as e:
        return json.dumps({"error": str(e)})
    
def mongodb_or_sql(user_question, sample_docs):
    system_prompt = f"""
    You are a MongoDB and MySQL expert. You will read a prompt in natural language and decide whether to query MongoDB or MySQL for the answer.
    The MongoDB database only has three collections: likes, posts, and comments. 
    The MongoDB database does not have a Users collection.
    The MySQL database only has three tables: Users, Posts, and Follows. 
    
    Read the database schema from the following SQL table creation statement:
    CREATE TABLE `Users` (
    `USER_ID` INT,
    `HANDLE` VARCHAR(32) NOT NULL,
    `PASSWORD` VARCHAR(255) NOT NULL,
    `EMAIL` VARCHAR(255) NOT NULL,
    PRIMARY KEY (`USER_ID`)
    );

    CREATE TABLE `Posts` (
    `POST_ID` VARCHAR(50),
    `USER_ID` INT,
    PRIMARY KEY (`POST_ID`),
    FOREIGN KEY (`USER_ID`) REFERENCES `Users`(`USER_ID`) ON UPDATE CASCADE ON DELETE CASCADE
    );

    CREATE TABLE `Follows` (
    `FOLLOWER` VARCHAR(32),
    `FOLLOWING` VARCHAR(32),
    PRIMARY KEY (`FOLLOWER`, `FOLLOWING`),
    FOREIGN KEY (`FOLLOWER`) REFERENCES `Users`(`USER_ID`) ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (`FOLLOWING`) REFERENCES `Users`(`USER_ID`) ON UPDATE CASCADE ON DELETE CASCADE
    );

    Read the key names from the sample documents for MongoDB: {sample_docs}

    Given the above MySQL and MongoDB structures, should you query the MySQL database or MongoDB database for the answer?
    Answer "MySQL" or "MongoDB".

    """

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_question}
    ]
    try:
        return chat(messages)
    except Exception as e:
        return json.dumps({"error": str(e)})