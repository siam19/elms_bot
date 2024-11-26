#DATA ACCESS LAYER

from motor.motor_asyncio import AsyncIOMotorCollection
from pydantic import BaseModel, Field
from bson import ObjectId
from typing import List

class testDAL:
    def __init__(self, test_collection: AsyncIOMotorCollection):
        self.test_collection = test_collection

    async def get_test(self):
        tests = []
        async for test in self.test_collection.find():
            test['_id'] = str(test['_id'])
            tests.append(test)
        return tests
    
    async def add_test(self, test: dict):
        await self.test_collection.insert_one(test)
        return {"message": f"{str(test)} added successfully"}
    

    