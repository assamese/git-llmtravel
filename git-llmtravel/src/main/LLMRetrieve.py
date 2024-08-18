import openai
import os
from openai import OpenAI
import psycopg2
import json

#openai.my_api_key = os.environ["OPENAI_API_KEY"]

script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

def load_dbconfig(file_path):
    with open(file_path, 'r') as config_file:
        config = json.load(config_file)
    return config

dbconfig = load_dbconfig("../../config/db.json")

def load_llmconfig(file_path):
    with open(file_path, 'r') as config_file:
        config = json.load(config_file)
    return config

llmconfig = load_llmconfig("../../config/llm.json")

openai.my_api_key = llmconfig["api_keys"]["openai"]

client = OpenAI()

def ask_gpt(prompt):
    messages.append({"role" : "user", "content" : prompt})
    response = client.chat.completions.create(
        model = "gpt-3.5-turbo",
        messages = messages
        )
    reply = response.choices[0].message.content
    messages.append({"role" : "assistant", "content" : reply})
    return reply

messages = []

conn = psycopg2.connect(
    database = dbconfig["database"]["name"],
    user = dbconfig["database"]["user"],
    password = dbconfig["database"]["password"],
    host = dbconfig["database"]["host"],
    port = dbconfig["database"]["port"]
    )

uid = 2345
cur = conn.cursor()
sql = (f"""SELECT * FROM tripdetails
    WHERE uid = {uid};""")
cur.execute(sql, uid)
result = cur.fetchone()

#Prompt to generate initial itinerary

itinerary_prompt = "Please list day-to-day itinerary from travel agents for a vacation to" + result[2] + "from date" + str(result[3]) + "to" + str(result[4]) + "for" + str(result[5]) + "people .I will be leaving from" + result[1] + ". The budget for this vacation is " + str(result[6]) + ".Suggest how I can include these activities in the itinerary during the vacation :" + result[7] + ". List additional information regarding " + result[8] + " for this trip."

itinerary_response = ask_gpt(itinerary_prompt)
print(itinerary_response)

# Modifying itinerary to and fro based on further user preferences

while True:
    print("Are you satisfied with the itinerary presented? \n Type Y for yes, else type for further additional preferences: ")      
    itinerary_modify = input("You : ")
    if itinerary_modify == "Y":
        print("Your itinerary is ready!")
        break
    response = ask_gpt(itinerary_modify)
    print("ChatGPT : ", response)

# Getting itinerary in JSON format, schema provided

JSON_itinerary_prompt = """Here is a JSON schema. Please show this itinerary that follows this schema.
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "London Vacation Itinerary",
  "type": "object",
  "properties": {
    "trip": {
      "type": "object",
      "properties": {
        "from": { "type": "string" },
        "to": { "type": "string" },
        "start_date": { "type": "string", "format": "date" },
        "end_date": { "type": "string", "format": "date" },
        "people": { "type": "integer" },
        "budget_in_inr": { "type": "integer" },
        "itinerary": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "day": { "type": "integer" },
              "date": { "type": "string", "format": "date" },
              "activities": {
                "type": "array",
                "items": { "type": "string" }
              }
            },
            "required": ["day", "date", "activities"]
          }
        },
        "hotels": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "name": { "type": "string" },
              "type": { "type": "string" },
              "location": { "type": "string" },
              "price_per_night_inr": { "type": "integer" }
            },
            "required": ["name", "type", "location", "price_per_night_inr"]
          }
        },
        "airlines": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "name": { "type": "string" },
              "note": { "type": "string" }
            },
            "required": ["name", "note"]
          }
        },
        "budget_breakdown_inr": {
          "type": "object",
          "properties": {
            "flights": { "type": "integer" },
            "accommodation": { "type": "integer" },
            "daily_expenses": { "type": "integer" },
            "shopping_and_miscellaneous": { "type": "integer" },
            "total_estimated_cost": { "type": "integer" },
            "buffer": { "type": "integer" }
          },
          "required": [
            "flights",
            "accommodation",
            "daily_expenses",
            "shopping_and_miscellaneous",
            "total_estimated_cost",
            "buffer"
          ]
        }
      },
      "required": [
        "from",
        "to",
        "start_date",
        "end_date",
        "people",
        "budget_in_inr",
        "itinerary",
        "hotels",
        "airlines",
        "budget_breakdown_inr"
      ]
    }
  },
  "required": ["trip"]
}
"""
JSON_itinerary_response = ask_gpt(JSON_itinerary_prompt)
print(JSON_itinerary_response)

#Store the itinerary in table in JSON format

update_sql = """UPDATE tripDetails SET itinerary = %s WHERE uid = %s;"""
cur.execute(update_sql, [json.dumps(JSON_itinerary_response), uid])

# Finding prospective travel agencies

agent_list_prompt = """Here is a JSON schema. Can you list travel agencies located in " + origin + " or " + destination + " who can help me with this itinerary. Provide the email addresses of these agents. Show in JSON format that follows the provided schema.
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Travel Agencies",
  "type": "object",
  "properties": {
    "travel_agencies": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "name": {
            "type": "string"
          },
          "location": {
            "type": "string"
          },
          "address": {
            "type": "string"
          },
          "website": {
            "type": "string",
            "format": "uri"
          },
          "phone": {
            "type": "string"
          },
          "email": {
            "type": "string",
            "format": "email"
          }
        },
        "required": ["name", "location", "address", "website", "phone", "email"]
      }
    }
  },
  "required": ["travel_agencies"]
}

"""
agent_list_response = ask_gpt(agent_list_prompt)
print(agent_list_response)

#Extract travel agent email addresses into a list
travel_agent_data = json.loads(agent_list_response)
email_addresses = [agency['email'] for agency in travel_agent_data['travel_agencies']]
print(email_addresses)

#Prompt LLM to draft an email
email_prompt = """Generate an email subject and body to send to a travel agent enquiring whether they can help me visit these places and assist with the activities. Do not use any variables. The sender's name is """ + str(uid) + """. The draft should be 100 words. Here is the schema to follow :
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Email",
  "type": "object",
  "properties": {
    "subject": {
      "type": "string"
    },
    "body": {
      "type": "string"
    }
  },
  "required": ["subject", "body"]
}
"""
gen_email = ask_gpt(email_prompt)
print(gen_email)

#Extract subject and body into variables
email_data = json.loads(gen_email)
email_subject = email_data['subject']
email_body = email_data['body']

conn.commit()
cur.close()
conn.close()
