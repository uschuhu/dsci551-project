import mysql.connector
import pandas as pd
from sqlalchemy import create_engine, text
from utils import load_config

def get_mysql_connection():
    config = load_config()
    user = config["MYSQL_U"]
    pw = config["MYSQL_P"]
    host = config["MYSQL_HOST"]
    port = config["MYSQL_PORT"]

    engine = create_engine(f"mysql+mysqlconnector://{user}:{pw}@{host}:{port}")
    return engine

def close_mysql_connection(conn, engine):
    conn.close()
    engine.dispose()
