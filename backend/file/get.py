from typing import Annotated
from fastapi import APIRouter, Depends
import auth
from db import db, User, Files
import boto3

file_router = APIRouter()

s3 = boto3.client('s3')


@file_router.get("/list_files")
async def lists_files(current_user: Annotated[auth.UserSchema, Depends(auth.get_current_user)]):
    with db.transaction() as session:
        cuser = session.query(User).get(current_user.id)
        if not cuser:
            return {"error": "User not found"}
        files = session.query(Files).filter_by(owner_id=current_user.id).all()
        file_list = [{"id": f.id, "filename": f.filename} for f in files]
    return {"files": file_list}

@file_router.get("/file/{file_id}")
async def get_file(file_id: int, current_user: Annotated[auth.UserSchema, Depends(auth.get_current_user)]):
    with db.transaction() as session:
        cuser = session.query(User).get(current_user.id)
        if not cuser:
            return {"error": "User not found"}
        file = session.query(Files).filter_by(id=file_id, owner_id=current_user.id).first()
        if not file:
            return {"error": "File not found"}, 404
    return {"id": file.id, "filename": file.filename, "size": file.size}

@file_router.delete("/file/{file_id}")
async def delete_file(file_id: int, current_user: Annotated[auth.UserSchema, Depends(auth.get_current_user)], do_s3:bool=False):
    with db.transaction() as session:
        cuser = session.query(User).get(current_user.id)
        if not cuser:
            return {"error": "User not found"}
        file = session.query(Files).filter_by(id=file_id, owner_id=current_user.id).first()
        if not file:
            return {"error": "File not found"}, 404
        cuser.used -= file.size
        session.delete(file)
    if do_s3:
        s3.delete_object(Bucket="mshare", Key=cuser.id+"/"+file.filename)
    return {"status": "File deleted"}

@file_router.put("/file/{file_id}/rename")
async def rename_file(file_id: int, new_name: str, current_user: Annotated[auth.UserSchema, Depends(auth.get_current_user)]):
    with db.transaction() as session:
        cuser = session.query(User).get(current_user.id)
        if not cuser:
            return {"error": "User not found"}
        file = session.query(Files).filter_by(id=file_id, owner_id=current_user.id).first()
        if not file:
            return {"error": "File not found"}, 404
        file = session.query(Files).filter_by(id=file_id, owner_id=current_user.id).update({"filename": new_name})
        session.add(file)
    return {"status": "File renamed", "new_name": new_name}

@file_router.get("/quota")
async def get_quota(current_user: Annotated[auth.UserSchema, Depends(auth.get_current_user)]):
    with db.transaction() as session:
        cuser = session.query(User).get(current_user.id)
        if not cuser:
            return {"error": "User not found"}
    return {"quota": cuser.quota, "used": cuser.used}

@file_router.post("/share/{file_id}")
async def share_file(file_id: int, target_username: str, current_user: Annotated[auth.UserSchema, Depends(auth.get_current_user)]):
    with db.transaction() as session:
        cuser = session.query(User).get(current_user.id)
        if not cuser:
            return {"error": "User not found"}
        file = session.query(Files).filter_by(id=file_id, owner_id=current_user.id).first()
        if not file:
            return {"error": "File not found"}, 404
        target_user = session.query(User).filter_by(username=target_username).first()
        if not target_user:
            return {"error": "Target user not found"}, 404
        shared_file = Files(filename=file.filename, owner_id=target_user.id, size=file.size)
        session.add(shared_file)
    return {"status": "File shared", "shared_with": target_username}

