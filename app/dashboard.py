from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date

from app.database import SessionLocal
from app.models import Client, Pickup

router = APIRouter()


# DB dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ✅ Dashboard Data
@router.get("/dashboard")
def get_dashboard(db: Session = Depends(get_db)):

    # Total clients
    total_clients = db.query(Client).count()

    # Total pickups (sum of pickup_count)
    total_pickups = db.query(func.sum(Pickup.pickup_count)).scalar() or 0

    # Today's pickups
    today = date.today()
    today_pickups = (
        db.query(func.sum(Pickup.pickup_count))
        .filter(Pickup.pickup_date == today)
        .scalar() or 0
    )

    # Client-wise totals
    client_totals = (
        db.query(
            Client.client_id,
            Client.name,
            func.sum(Pickup.pickup_count).label("total")
        )
        .join(Pickup, Pickup.client_id == Client.id)
        .group_by(Client.id)
        .all()
    )

    summary = [
        {
            "client_id": c.client_id,
            "client_name": c.name,
            "total_pickups": c.total or 0
        }
        for c in client_totals
    ]

    return {
        "total_clients": total_clients,
        "total_pickups": total_pickups,
        "today_pickups": today_pickups,
        "client_summary": summary
    }

from fastapi.responses import StreamingResponse
import io
import pandas as pd

@router.get("/export-pickups")
def export_pickups(db: Session = Depends(get_db)):

    pickups = db.query(Pickup).join(Client).all()

    data = [
        {
            "Date": p.pickup_date,
            "Client Code": p.client.client_id,
            "Client Name": p.client.name,
            "Pickup Count": p.pickup_count
        }
        for p in pickups
    ]

    df = pd.DataFrame(data)

    stream = io.BytesIO()
    df.to_excel(stream, index=False, engine="openpyxl")
    stream.seek(0)

    return StreamingResponse(
        stream,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=pickups.xlsx"}
    )
