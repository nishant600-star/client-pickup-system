from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi import Request
templates = Jinja2Templates(directory="app/templates")


from fastapi import FastAPI

# Database
from app.database import engine, Base

# Models (important so tables get created)
from app import models

# Routers
from app.clients import router as client_router
from app.pickups import router as pickup_router


# Create app
app = FastAPI(title="Client Pickup Management System")



# Include routers
app.include_router(client_router)
app.include_router(pickup_router)


# Create tables
Base.metadata.create_all(bind=engine)

from app.dashboard import router as dashboard_router
app.include_router(dashboard_router)

from fastapi.staticfiles import StaticFiles
app.mount("/static", StaticFiles(directory="app/static"), name="static")



# Home route
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request}
    )


@app.get("/dashboard-page", response_class=HTMLResponse)
def dashboard_page(request: Request):
    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request}
    )

@app.get("/clients-page", response_class=HTMLResponse)
def clients_page(request: Request):
    return templates.TemplateResponse(
        "clients.html",
        {"request": request}
    )

@app.get("/pickup-page", response_class=HTMLResponse)
def pickup_page(request: Request):
    return templates.TemplateResponse(
        "pickup.html",
        {"request": request}
    )

