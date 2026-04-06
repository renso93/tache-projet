from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base, get_db
from main import app
import models
import os

# Supprimer la DB de test si elle existe déjà
if os.path.exists("./test.db"):
    os.remove("./test.db")

# Base de données séparée pour les tests
TEST_DATABASE_URL = "sqlite:///./test.db"

engine_test = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(bind=engine_test)
Base.metadata.create_all(bind=engine_test)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

# ─── Tests Register ───

def test_register_succes():
    response = client.post("/register", json={
        "nom": "Renso",
        "email": "test@gmail.com",
        "mot_de_passe": "test123"
    })
    assert response.status_code == 200
    assert response.json()["message"] == "Compte créé avec succès"

def test_register_email_deja_utilise():
    client.post("/register", json={
        "nom": "Renso",
        "email": "double@gmail.com",  # ← email, pas username
        "mot_de_passe": "test123"     # ← mot_de_passe, pas password
    })
    response = client.post("/register", json={
        "nom": "Renso",
        "email": "double@gmail.com",  # ← même email
        "mot_de_passe": "test123"
    })
    assert response.status_code == 400

# ─── Tests Login ───

def test_login_succes():
    client.post("/register", json={
        "nom": "Renso",
        "email": "login@gmail.com",
        "mot_de_passe": "test123"
    })
    response = client.post("/login", data={
        "username": "login@gmail.com",  # ← username seulement
        "password": "test123"           # ← password seulement
    })
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_login_mauvais_identifiants():
    response = client.post("/login", data={
        "username": "login@gmail.com",
        "password": "mauvais"
    })
    assert response.status_code == 401

# ─── Tests Tâches ───

def get_token():
    client.post("/register", json={
        "nom": "Renso",
        "email": "taches@gmail.com",
        "mot_de_passe": "test123"
    })
    response = client.post("/login", data={
        "username": "taches@gmail.com",
        "password": "test123"
    })
    return response.json()["access_token"]

def test_ajouter_tache():
    token = get_token()
    response = client.post("/taches", json={
        "titre": "Ma tâche de test",
        "description": "Description de ma tâche de test",
        "terminee": False
    }, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["titre"] == "Ma tâche de test"

def test_lister_taches():
    token = get_token()
    response = client.get(
        "/taches",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_tache_sans_token():
    response = client.get("/taches")
    assert response.status_code == 401