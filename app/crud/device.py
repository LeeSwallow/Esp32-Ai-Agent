from typing import Optional, List

from sqlalchemy.orm import Session

from app.model.device import Device


def get_by_name(db: Session, device_id: str) -> Optional[Device]:
    return db.query(Device).filter(Device.device_id == device_id).first()


def create(db: Session, device_id: str) -> Device:
    device = Device(device_id=device_id)
    db.add(device)
    db.commit()
    db.refresh(device)
    return device


def list_all(db: Session) -> List[Device]:
    return db.query(Device).order_by(Device.id.desc()).all()