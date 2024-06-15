import os

#API_ID = 22505271  # api id
#API_HASH = "c89a94fcfda4bc06524d0903977fc81e"

#BOT_TOKEN = "7209486748:AAHYo-Co8ezY_7e2QD0FkPXw_WlZWihM6cg"


## REDIS
HOST = "redis-16448.c73.us-east-1-2.ec2.cloud.redislabs.com"  # redis host uri
PORT = 16448  # redis port
PASSWORD = "o5BMtARZTkrMHP7xvxkOEx6XrXS583NN"  # redis password

PRIVATE_CHAT_ID = -1002022900736
ADMINS = [6695586027]

#Database 
#Database [https://youtu.be/qFB0cFqiyOM?si=fVicsCcRSmpuja1A]
DB_URI = os.environ.get("DATABASE_URL", "mongodb+srv://ultroidxTeam:ultroidxTeam@cluster0.gabxs6m.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
DB_NAME = os.environ.get("DATABASE_NAME", "ultroidxTeam")

#Shortner (token system) 
# check my discription to help by using my refer link of shareus.io


SHORTLINK_URL = os.environ.get("SHORTLINK_URL", "instantearn.in")
SHORTLINK_API = os.environ.get("SHORTLINK_API", "47070a188ed5491b80f3b70adde6f9954a1e6ee7")
VERIFY_EXPIRE = int(os.environ.get('VERIFY_EXPIRE', 86400)) # Add time in seconds
IS_VERIFY = os.environ.get("IS_VERIFY", "True")
TUT_VID = os.environ.get("TUT_VID", "https://t.me/Ultroid_Official/18") # shareus ka tut_vid he 
