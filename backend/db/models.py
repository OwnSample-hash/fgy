from . import mariadb as db
from pydantic import BaseModel


class User(db.Base):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, index=True, autoincrement=True)
    username = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, index=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, email={self.email})>"


class UserSchema(BaseModel):
    id: int
    username: str
    email: str

    class Config:
        from_attributes = True


class Files(db.Base):
    __tablename__ = "files"

    id = db.Column(db.Integer, primary_key=True, index=True)
    filename = db.Column(db.String(255), nullable=False)
    filepath = db.Column(db.String(255), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    shared_with = db.Column(db.String(255), nullable=True)  # Comma-separated user IDs

    def __repr__(self):
        return (
            f"<File(id={self.id}, filename={self.filename}, owner_id={self.owner_id})>"
        )


class FileSchema(BaseModel):
    id: int
    filename: str
    filepath: str
    owner_id: int
    shared_with: str | None = None

    class Config:
        from_attributes = True


class Logs(db.Base):
    __tablename__ = "logs"

    id = db.Column(db.Integer, primary_key=True, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    file_id = db.Column(db.Integer, db.ForeignKey("files.id"), nullable=True)
    action = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)

    def __repr__(self):
        return f"<Log(id={self.id}, user_id={self.user_id}, action={self.action}, timestamp={self.timestamp})>"


class LogSchema(BaseModel):
    id: int
    user_id: int | None = None
    file_id: int | None = None
    action: str
    timestamp: str

    class Config:
        from_attributes = True
