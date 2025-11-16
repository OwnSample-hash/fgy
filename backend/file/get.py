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
            return {"error": "User not found"}, 404
        files = session.query(Files).filter_by(owner_id=current_user.id).all()
        file_list = [{"id": f.id, "filename": f.filename, "original": f.original,
                      "owner_username": session.query(User).get(f.original).username if f.original != cuser.id else current_user.username,
                      } for f in files]
    return file_list

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

@file_router.get("/file/{file_id}/download")
async def download_file(file_id: int, current_user: Annotated[auth.UserSchema, Depends(auth.get_current_user)]):
    with db.transaction() as session:
        cuser = session.query(User).get(current_user.id)
        if not cuser:
            return {"error": "User not found"}
        file = session.query(Files).filter_by(id=file_id, owner_id=current_user.id).first()
        if not file:
            return {"error": "File not found"}, 404
    try:
        s3.head_object(Bucket="mshare", Key=file.original+"/"+file.filename)
    except s3.exceptions.NoSuchKey:
        return {"error": "File not found in storage"}, 404
    presigned_url = s3.generate_presigned_url('get_object',
                                              Params={'Bucket': 'mshare',
                                                      'Key': file.original+"/"+file.filename},
                                              ExpiresIn=3600)
    return {"download_url": presigned_url, "error": None, "filename": file.filename}

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
        refs = session.query(Files).filter_by(original=current_user.id, filename=file.filename).all()
        for ref in refs:
            session.delete(ref)
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
        shared_file = Files(filename=file.filename, owner_id=target_user.id, size=file.size, original=cuser.id)
        session.add(shared_file)
    return {"status": "File shared", "shared_with": target_username}

