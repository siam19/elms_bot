from contextlib import asynccontextmanager
from fastapi import FastAPI
from typing import Union
import redis


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Before server starts serving requests

    # Connect to redis
    redis_client = redis.Redis(host='redis', port=6379, decode_responses=True)
    
    # attach redis client to app instance
    app.redis = redis_client

    yield # Server is serving requests

    # Shutdown


app = FastAPI(lifespan=lifespan)



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