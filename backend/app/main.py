from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session

from . import models  # noqa: F401  (importar registra as tabelas no Base)
from .database import Base, engine, get_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Cria as tabelas na inicialização. Mais pra frente, trocar por migrações (Alembic).
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="Organizador de Comprovantes", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # porta padrão do Vite (React)
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/saude")
def saude(db: Session = Depends(get_db)):
    """Confirma que a API está no ar e conectada ao banco."""
    db.execute(text("SELECT 1"))
    return {"status": "ok"}