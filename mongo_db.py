import motor.motor_asyncio
import pymongo
import asyncio


# mClient = motor.motor_asyncio.AsyncIOMotorClient(
#     "mongodb+srv://master:master@main.gmcbd.mongodb.net/main?retryWrites=true&w=majority")
# print(mClient.main.main)


async def connect_to_database(database: str):
    mClient = motor.motor_asyncio.AsyncIOMotorClient(
        f"mongodb+srv://master:/{database}?retryWrites=true&w=majority")
    database = mClient[database]
    return database


async def get_collection(database: motor.motor_asyncio.AsyncIOMotorDatabase, collection: str):
    return database[collection]


loop = asyncio.get_event_loop()
database = loop.run_until_complete(connect_to_database("DiscordStat"))
# mClient = pymongo.MongoClient("mongodb+srv://master:master@main.gmcbd.mongodb.net/main?retryWrites=true&w=majority")
# database = mClient.main
# main_coll = database['main']
