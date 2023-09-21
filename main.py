from fastapi import FastAPI, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import uvicorn
from pydantic import BaseModel
app = FastAPI()


#DB CONNECTION
client = AsyncIOMotorClient("mongodb://localhost:27017")     
db = client["todo_db"]
collection = db["todos"]

if __name__ == "__main__":
   uvicorn.run("main:app", host="127.0.0.1", port=9003, reload=True)

#MODEL
class TodoModel(BaseModel):
    _id:ObjectId
    title: str
    description: str

@app.post("/todos/", response_model=TodoModel)
async def create_todo(todo: TodoModel):
    inserted = await collection.insert_one({"title": todo.title, "description": todo.description})
    created_todo = await collection.find_one({"_id": inserted.inserted_id})
    return created_todo

@app.get("/todos/{todo_id}", response_model=TodoModel)
async def read_todo(todo_id: str):
    todo = await collection.find_one({"_id": ObjectId(todo_id)})
    if todo:
        print(todo)
        return todo
    raise HTTPException(status_code=404, detail="Todo not found")

@app.put("/todos/{todo_id}", response_model=TodoModel)
async def update_todo(todo_id: str, todo: TodoModel):
    updated = await collection.update_one(
        {"_id": ObjectId(todo_id)},
        {"$set": {"title": todo.title, "description": todo.description}},
    )
    if updated.modified_count == 1:
        updated_todo = await collection.find_one({"_id": ObjectId(todo_id)})
        return updated_todo
    raise HTTPException(status_code=404, detail="Todo not found")

@app.delete("/todos/{todo_id}", response_model=dict)
async def delete_todo(todo_id: str):
    deleted = await collection.delete_one({"_id": ObjectId(todo_id)})
    if deleted.deleted_count == 1:
        return {"message": "Todo deleted"}
    raise HTTPException(status_code=404, detail="Todo not found")