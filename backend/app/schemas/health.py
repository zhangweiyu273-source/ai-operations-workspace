from pydantic import BaseModel


class LivenessResponse(BaseModel):
    status: str
    service: str
    version: str


class ReadinessResponse(BaseModel):
    status: str
    database: str


class SystemStatusResponse(BaseModel):
    name: str
    version: str
    environment: str
    database: str
