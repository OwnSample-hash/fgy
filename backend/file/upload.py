from typing import Annotated
from fastapi import APIRouter, UploadFile, Depends
import auth
from db import db, User, Files
import boto3

router = APIRouter()

s3 = boto3.client('s3')

@router.post("/upload")
async def upload_file(file: UploadFile, current_user: Annotated[auth.UserSchema, Depends(auth.get_current_user)]):
    with db.transaction() as session:
        cuser = session.query(User).get(current_user.id)
        if not cuser:
            return {"error": "User not found"}
        # Save file metadata to database
        if cuser.quota <= session.query(Files).filter_by(owner_id=current_user.id).count():
            return {"error": "Quota exceeded"}, 403
        if file.size:
           cuser.used += file.size / (1024 * 1024)  # Convert bytes to MiB
        else:
            file.file.seek(0, 2)  # Move to end of file
            size = file.file.tell()
            cuser.used += size / (1024 * 1024)
            file.file.seek(0)  # Reset to start of file
        session.add(Files(filename=file.filename, owner_id=current_user.id))
    s3.upload_fileobj(file.file, "your-bucket-name", file.filename)
    return {"filename": file.filename}
