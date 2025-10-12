from pydantic import BaseModel

class Connection(BaseModel):
    host: str
    port: int
    username: str|None = None
    password: str|None = None

