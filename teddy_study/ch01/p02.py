from dotenv import load_dotenv

load_dotenv()

import os

print(f"[API KEY]\n{os.environ.get('OPEN_AI_API_KEY')}")