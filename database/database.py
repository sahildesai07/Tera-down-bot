import motor.motor_asyncio
from config import DB_URI, DB_NAME

# MongoDB setup
dbclient = motor.motor_asyncio.AsyncIOMotorClient(DB_URI)
database = dbclient[DB_NAME]
user_data = database['users']

# Default verify status
default_verify = {
    'is_verified': False,
    'verified_time': 0,
    'verify_token': "",
    'link': ""
}

# Function to create a new user document template
def new_user(id):
    return {
        '_id': id,
        'verify_status': default_verify.copy()  # Use a copy to avoid modifying default_verify
    }

# Check if a user is present in the database
async def present_user(user_id: int):
    found = await user_data.find_one({'_id': user_id})
    return bool(found)

# Add a new user to the database
async def add_user(user_id: int):
    user = new_user(user_id)
    await user_data.insert_one(user)

# Retrieve verify status for a user
async def db_verify_status(user_id):
    user = await user_data.find_one({'_id': user_id})
    if user:
        return user.get('verify_status', default_verify)
    return default_verify

# Update verify status for a user
async def db_update_verify_status(user_id, verify):
    await user_data.update_one({'_id': user_id}, {'$set': {'verify_status': verify}})

# Retrieve a list of all user IDs in the database
async def full_userbase():
    user_docs = user_data.find()
    user_ids = [doc['_id'] async for doc in user_docs]
    return user_ids

# Delete a user from the database
async def del_user(user_id: int):
    await user_data.delete_one({'_id': user_id})
