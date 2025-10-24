#!/usr/bin/env python3
import os
from dotenv import load_dotenv


if os.getenv("ENV") == "PROD":
    load_dotenv("data/.env")
else:
    load_dotenv()


from fastapi import FastAPI
from db import db
from auth import router as auth_router
from sys import argv
import uvicorn


app = FastAPI()
app.include_router(auth_router, tags=["auth"], prefix="/api")


@app.get("/")
async def read_root():
    return {"Hello": "World"}


if __name__ == "__main__":
    if "--do-db" in argv:
        try:
            db.drop_tables()
            db.create_tables()
            print("Database setup completed.")
        except Exception as e:
            print(f"Error setting up database: {e}")


    if "--reload" in argv:
        uvicorn.run("main:app", host="127.0.0.1", port=int(os.getenv("PORT", 8000)), reload=True)
    else:
        uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
