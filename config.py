import os
from dotenv import load_dotenv

load_dotenv() #read from .env 

RESUME_KEYWORDS=["python","django","flask","sql","rest api"
                 ,"git","docker","javascript"]
TARGET_TITLES=["associate engineer","python developer",
               "backend developer","software engineer"]
EMAIL_ADDRESS=os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD=os.getenv("EMAIL_PASSWORD")
RECIPIENT_EMAIL=os.getenv("RECIPIENT_EMAIL")
