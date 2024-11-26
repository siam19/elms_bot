from contextlib import asynccontextmanager
from fastapi import FastAPI
from typing import Union
from motor.motor_asyncio import AsyncIOMotorClient
import os


import redis

from extract import createDriver, authenticate_and_get_course_page

from dal import testDAL


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Before server starts serving requests
    db_client = AsyncIOMotorClient(f"mongodb://{os.environ.get('MONGO_INITDB_ROOT_USERNAME')}:{os.environ.get('MONGO_INITDB_ROOT_PASSWORD')}@mongodb:27017")
    
    database = db_client.get_database('test_db')
    
    # Ensure the database is available:
    pong = await database.command("ping")
    if int(pong["ok"]) != 1:
        raise Exception("Cluster connection is not okay!")

    
    # Get Collections from mongo
    test_collection = database.get_collection('test_collection')
    app.test_dal = testDAL(test_collection)
    # Connect to redis
    redis_client = redis.Redis(host='redis', port=6379, decode_responses=True)

    # attach redis client to app instance
    app.redis = redis_client

    app.webdriver = createDriver()

    yield # Server is serving requests

    # Shutdown


app = FastAPI(lifespan=lifespan)

@app.get("/mongo_test")
async def get_test():
    tests = await app.test_dal.get_test()
    return {"tests": tests}

@app.post("/add_test")
async def add_test(test: dict):
    await app.test_dal.test_collection.insert_one(test)
    return {"message": "Test added successfully"}

@app.get("/get-course")
def get_course_page(course_url: str):
    course_data = authenticate_and_get_course_page(app.webdriver, course_url)
    return {"course_data": course_data}

@app.get("/redis")
def test_redis(command: str, key: str, value: Union[str, int]):
    if command == "set":
        app.redis.set(key, value)
        return {"res": f"Set {key} to {value}"}
    elif command == "get":
        return {"res": app.redis.get(key)}

@app.post("/publish-message")
def send_message(message: str):
    # Publish message to redis channel
    app.redis.publish('message_queue', message)
    return {"message": f"Message published: {message}"}