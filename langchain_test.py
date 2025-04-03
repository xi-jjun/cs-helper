import os
from dotenv import load_dotenv

load_dotenv() # load .env file

API_KEY = os.environ['OPEN_AI_API_KEY']
print(API_KEY)
