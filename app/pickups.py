from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date

from app.database import SessionLocal
from app.models import Pickup, Client

router = APIRouter()

# DB dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ✅ Add Pickup
@router.post("/pickups")
def add_pickup(
    client_id: int,
    pickup_date: date,
    pickup_count: int,
    db: Session = Depends(get_db)
):

    # Check client exists
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    # Validate pickup count
    if pickup_count < 0:
        raise HTTPException(status_code=400, detail="Pickup count must be positive")

    new_pickup = Pickup(
        client_id=client_id,
        pickup_date=pickup_date,
        pickup_count=pickup_count
    )

    db.add(new_pickup)
    db.commit()
    db.refresh(new_pickup)

    return {"message": "Pickup added successfully"}

# ✅ Get Pickups (with filters)
@router.get("/pickups")
def get_pickups(
    pickup_date: date | None = None,
    client: str | None = None,
    db: Session = Depends(get_db)
):

    query = db.query(Pickup).join(Client)

    # Filter by date
    if pickup_date:
        query = query.filter(Pickup.pickup_date == pickup_date)

    # Filter by client name OR client_id string
    if client:
        query = query.filter(
            (Client.name.ilike(f"%{client}%")) |
            (Client.client_id.ilike(f"%{client}%"))
        )

    pickups = query.all()

    return [
        {
            "id": p.id,
            "date": p.pickup_date,
            "client_id": p.client.client_id,
            "client_name": p.client.name,
            "pickup_count": p.pickup_count
        }
        for p in pickups
    ]

# DELETE PICKUP
@router.delete("/pickups/{pickup_id}")
def delete_pickup(pickup_id: int, db: Session = Depends(get_db)):

    pickup = db.query(Pickup).filter(Pickup.id == pickup_id).first()

    if not pickup:
        raise HTTPException(status_code=404, detail="Pickup not found")

    db.delete(pickup)
    db.commit()

    return {"message": "Pickup deleted"}

# UPDATE PICKUP
@router.put("/pickups/{pickup_id}")
def update_pickup(
    pickup_id: int,
    pickup_date: date,
    pickup_count: int,
    db: Session = Depends(get_db)
):

    pickup = db.query(Pickup).filter(Pickup.id == pickup_id).first()

    if not pickup:
        raise HTTPException(status_code=404, detail="Pickup not found")

    pickup.pickup_date = pickup_date
    pickup.pickup_count = pickup_count

    db.commit()

    return {"message": "Pickup updated"}
