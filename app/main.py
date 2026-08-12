import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers.auth_router import router as auth_router
from app.routers.user_router import router as user_router
from app.routers.logistics_router import router as logistics_router
from app.routers.customer_router import router as customer_router
from app.routers.driver_router import router as driver_router
from app.routers.container_router import router as container_router
from app.routers.shipment_router import router as shipment_router
from app.routers.document_router import router as document_router 
from app.routers.tracking_router import router as tracking_router
from app.routers.dashboard_router import router as dashboard_router


from fastapi.staticfiles import StaticFiles
from app.core.config import settings

API_PREFIX = "/api/v1"

app = FastAPI(
    
    title="FastAPI JWT UUID Role API",
    description="Reusable JWT authentication, refresh token, UUID IDs and role-based permissions",
    version="1.0.0",
)

os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
app.mount(
    settings.MEDIA_URL,
    StaticFiles(directory=str(settings.MEDIA_ROOT)),
    name="media",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {
        "message": "congratulations...your FastAPI API is running successfully🥳🎉",
    }


app.include_router(auth_router, prefix=API_PREFIX)
app.include_router(user_router, prefix=API_PREFIX)
app.include_router(logistics_router, prefix= API_PREFIX)
app.include_router(customer_router, prefix=API_PREFIX)
app.include_router(driver_router, prefix=API_PREFIX) 
app.include_router(container_router, prefix=API_PREFIX)  
app.include_router(shipment_router,prefix=API_PREFIX) 
app.include_router(document_router, prefix=API_PREFIX)
app.include_router(tracking_router, prefix=API_PREFIX)
app.include_router(dashboard_router, prefix= API_PREFIX)