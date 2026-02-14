from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Client

router = APIRouter()

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ✅ Add Client
@router.post("/clients")
def add_client(client_id: str, name: str, db: Session = Depends(get_db)):

    # Required validation
    if not client_id or not name:
        raise HTTPException(status_code=400, detail="All fields required")

    # Unique validation
    existing = db.query(Client).filter(Client.client_id == client_id).first()
    if existing:
        raise HTTPException(status_code=409, detail="Client ID already exists")

    new_client = Client(client_id=client_id, name=name)
    db.add(new_client)
    db.commit()
    db.refresh(new_client)

    return {"message": "Client added successfully"}

# ✅ Get All Clients
@router.get("/clients")
def get_clients(db: Session = Depends(get_db)):
    clients = db.query(Client).all()

    return [
        {
            "id": c.id,
            "client_id": c.client_id,
            "name": c.name
        }
        for c in clients
    ]

# ✅ Delete Client
# ✅ Delete Client
@router.delete("/clients/{id}")
def delete_client(id: int, db: Session = Depends(get_db)):

    client = db.query(Client).filter(Client.id == id).first()

    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    db.delete(client)
    db.commit()

    return {"message": "Client deleted successfully"}
