from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.traffic_lights import router as traffic_lights_router
from routers.mobile import router as mobile_router
from routers.rl_online import router as rl_online_router

app = FastAPI(
    title="Traffic Management System API",
    description="API for managing traffic lights, mobile users, and RL online data",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(traffic_lights_router)
app.include_router(mobile_router)
app.include_router(rl_online_router)

@app.get("/")
def read_root():
    return {"message": "Welcome to Traffic Management System API"}