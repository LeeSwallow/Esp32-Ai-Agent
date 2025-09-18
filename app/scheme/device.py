from datetime import datetime
from pydantic import BaseModel


class DeviceCreate(BaseModel):
    device_id: str

class DeviceResponse(BaseModel):
    id: int
    device_id: str
    created_at: datetime
    class Config:
        from_attributes = True

class SpeakRequest(BaseModel):
    text: str


