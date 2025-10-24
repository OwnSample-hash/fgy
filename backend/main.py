#!/usr/bin/env python3
import os
from fastapi import FastAPI
from db import db
from dotenv import load_dotenv
from auth import router as auth_router
from sys import argv
import uvicorn

load_dotenv()

app = FastAPI()
app.include_router(auth_router, tags=["auth"], prefix="/api")


@app.get("/")
async def read_root():
    return {"Hello": "World"}


if __name__ == "__main__":
    if "--do-db" in argv:
        db.drop_tables()
        db.create_tables()


    if "--reload" in argv:
        uvicorn.run("main:app", host="127.0.0.1", port=int(os.getenv("PORT", 8000)), reload=True)
    else:
        uvicorn.run(app, host="127.0.0.1", port=int(os.getenv("PORT", 8000)))
