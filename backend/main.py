from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routers import companies, leaderboard, search, trends, chat

app = FastAPI(title="YC Intel Advanced", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

#  ALL APIs under /api
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])
app.include_router(search.router, prefix="/api/search", tags=["Search"])
app.include_router(trends.router,)
app.include_router(leaderboard.router, prefix="/api", )
app.include_router(companies.router,)

@app.get("/")
def root():
    return {"status": "ok"}
