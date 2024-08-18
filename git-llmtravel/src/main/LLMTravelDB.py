import psycopg2
import json
import os



def load_dbconfig(file_path):
    with open(file_path, 'r') as config_file:
        config = json.load(config_file)
    return config

def get_input_and_save_to_db():
    dbconfig = load_dbconfig("config/db.json")

    from sqlalchemy.engine import URL
    from sqlalchemy import create_engine

    url = URL.create(
    'postgresql',
    username='LLMTravel-db1_owner',
    password='g9xZuEak7IGQ',
    host='ep-ancient-pond-a5jpapqu.us-east-2.aws.neon.tech',
    database='LLMTravel-db1'
    )
    engine = create_engine(url, connect_args={'sslmode': 'require'})

    create_query = "CREATE TABLE IF NOT EXISTS tripDetails3(\
        user_id VARCHAR(100) PRIMARY KEY,\
        origin VARCHAR(50),\
        destination VARCHAR(50),\
        start_date DATE,\
        end_date DATE,\
        noofppl INT,\
        budget FLOAT,\
        pref VARCHAR(100),\
        helpp VARCHAR(100),\
        itinerary JSONB)\
        "

    insert_query = " \
        INSERT INTO tripDetails3 (user_id, origin, destination, start_date, end_date, noofppl, budget, pref, helpp)\
        VALUES ('123', 'New York', 'Los Angeles', '2024-11-11', '2024-11-20', 4, 5000, 'luxury', 'flight')\
        "
    print (insert_query)

    with engine.connect() as conn:
        result = conn.execute(create_query)
        result = conn.execute(insert_query)


if __name__ == "__main__":
  get_input_and_save_to_db()
