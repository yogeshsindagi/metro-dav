from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes import matrix, threshold, zone, stations, compare, prediction

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Next.js
        "http://localhost:5173",  # Vite
        "http://127.0.0.1:5173",  # Vite alternative
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(compare.router)
app.include_router(matrix.router)
app.include_router(threshold.router)
app.include_router(zone.router)
app.include_router(stations.router)
app.include_router(prediction.router)

@app.get("/")
def root():
    return {"message": "TransitCost Analyzer API is running"}
