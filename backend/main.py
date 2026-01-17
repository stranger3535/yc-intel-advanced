from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routers import companies, leaderboard, search, trends, chat

app = FastAPI(
    title="YC Intel Advanced",
    version="0.1.0"
)

# ✅ CORS FIX (THIS IS IMPORTANT)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
        "http://127.0.0.1:3000",
        "http://localhost:3000",
        "https://your-frontend.vercel.app",
    ],
    allow_credentials=False,  # 🔥 MUST BE FALSE
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(chat.router)
app.include_router(search.router, prefix="/api")
app.include_router(trends.router, prefix="/api")
app.include_router(companies.router, prefix="/companies")
app.include_router(leaderboard.router, prefix="/leaderboard")

@app.get("/")
def root():
    return {"status": "ok"}
