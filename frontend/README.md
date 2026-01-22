# YC Intel Advanced 🚀

YC Intel Advanced is a **full-stack analytics and chat platform for Y Combinator companies**.  
It combines **data scraping, a FastAPI backend, and a Next.js frontend** to explore YC companies, trends, leaderboards, and interact with an AI-powered chat assistant.

---

## 🧱 Project Structure

This repository is a **single monorepo** (not submodules).

yc-intel-advanced/ │ ├── backend/ # FastAPI backend (API + AI) │ ├── api/ # API routes (companies, trends, leaderboard, chat) │ ├── core/ # Config, settings │ ├── db/ # Database models & sessions │ ├── services/ # RAG, Gemini, data logic │ ├── main.py # FastAPI entry point │ └── requirements.txt │ ├── frontend/ # Next.js frontend (App Router) │ ├── app/ │ │ ├── page.tsx # Chat page (home) │ │ ├── companies/ │ │ │ └── page.tsx # Companies list (table + pagination-ready) │ │ ├── trends/ │ │ │ └── page.tsx # Trends table │ │ ├── leaderboard/ │ │ │ └── page.tsx # Leaderboard │ │ ├── search/ │ │ │ └── page.tsx │ │ ├── components/ # UI components │ │ ├── globals.css # Plain CSS (NO Tailwind) │ │ └── layout.tsx # App layout + navbar │ │ │ ├── lib/ │ │ └── api.ts # Frontend → backend API helpers │ │ │ ├── public/ # Static assets │ ├── package.json │ ├── next.config.ts │ └── tsconfig.json │ ├── scraper/ # YC data scraper ├── yc_finetuned_model/ # Model artifacts (if any) ├── venv/ # Python virtual environment (local only) ├── .env # Backend environment variables ├── package.json # Root helpers (optional) └── README.md

---

## ⚙️ Tech Stack

### Backend

- **FastAPI**
- **Uvicorn**
- **SQLAlchemy**
- **SQLite / PostgreSQL**
- **Gemini LLM**
- **RAG (Retrieval-Augmented Generation)**

### Frontend

- **Next.js 16 (App Router)**
- **React**
- **TypeScript**
- **Plain CSS (no Tailwind)**

---

## 📊 Features

### ✅ Chat (Home Page)

- Ask questions about YC companies
- Uses **RAG + Gemini**
- Example prompts included
- Handles backend failures gracefully

### ✅ Companies

- Lists YC companies from database
- Shows:
  - Name
  - Website
  - Founded year
  - Active status
- Pagination-ready (Next / Previous can be added easily)

### ✅ Trends

- Category-wise trend counts
- Data normalized safely from backend
- Clean table view

### ✅ Leaderboard

- Top momentum companies
- Most stable companies
- Recent changes

---

## 🔌 Backend API Endpoints

Base URL:

http://127.0.0.1:8000

| Endpoint           | Method | Description            |
| ------------------ | ------ | ---------------------- |
| `/api/chat`        | POST   | AI chat (RAG + Gemini) |
| `/api/companies`   | GET    | List YC companies      |
| `/api/trends`      | GET    | Trend counts           |
| `/api/leaderboard` | GET    | Leaderboard data       |

Swagger UI:

http://127.0.0.1:8000/docs

---

## ▶️ Running the Project (Local)

### 1️⃣ Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate   # Windows
pip install -r requirements.txt
uvicorn main:app --reload

Backend runs at:

http://127.0.0.1:8000


---

2️⃣ Frontend

cd frontend
npm install
npm run dev

Frontend runs at:

http://localhost:3000


---

🧠 How Chat Works (High Level)

1. User enters a question


2. Frontend sends it to /api/chat


3. Backend:

Retrieves relevant YC company data (RAG)

Sends context + question to Gemini



4. Gemini generates response


5. Answer is returned and displayed




---

🧪 Data Notes

Company data comes from scraped YC sources

Some fields may be null (e.g., founded_year)

Frontend safely handles missing data using fallbacks (—)



---

🧹 Git Notes (Important)

This repo uses ONE Git repository

frontend/ is not a submodule

No nested .git folders

Safe to clone with:


git clone https://github.com/stranger3535/yc-intel-advanced.git


---

🚀 Future Improvements

Pagination for companies (server-side)

Filters (batch, tags, year)

Charts for trends

Authentication

Deployment (Vercel + Railway / Render)



---

👤 Author

Abhijith (stranger3535)
GitHub: https://github.com/stranger3535


---

📝 License

MIT
```
