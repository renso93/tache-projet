from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import or_
import models, schemas, auth
from database import engine, get_db



models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# --- Accueil --- 
@app.post("/")
def accueil():
    api_url = "http//:127.0.0.1/docs"
    return f"Bienvenue sur mon API, merci de visiter {api_url}"

# --- Auth ---
@app.post("/register")
def register(user: schemas.UtilisateurCreate, db: Session = Depends(get_db)):
    existant = db.query(models.Utilisateur).filter(models.Utilisateur.email == user.email).first()
    if existant:
        raise HTTPException(status_code=400, detail="Email déjà utilisé")
    nouveau = models.Utilisateur(nom=user.nom, email=user.email, mot_de_passe=auth.hasher_mot_de_passe(user.mot_de_passe))
    db.add(nouveau)
    db.commit()
    return {
        "message": "Compte créé avec succès"
    }

@app.post("/login", response_model=schemas.Token)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    utilisateur = db.query(models.Utilisateur).filter(or_(models.Utilisateur.email == form.username, models.Utilisateur.nom == form.username)).first()
    if not utilisateur or not auth.verifier_mot_de_passe(form.password, utilisateur.mot_de_passe):
        raise HTTPException(status_code=401, detail="Identifiants incorrect")
    token = auth.creer_token({"sub": utilisateur.email})
    return {"access_token": token, "token_type":"bearer"}

# --- Taches protégées ---
@app.get("/taches")
def lister_taches(db: Session = Depends(get_db),
                  utilisateur=Depends(auth.get_utilisateur_actuel)):
    return db.query(models.Tache).all()

@app.post("/taches")
def ajouter_tache(tache: schemas.TacheCreate, db: Session = Depends(get_db),
                   utilisateur=Depends(auth.get_utilisateur_actuel)):
    nouvelle_tache = models.Tache(**tache.model_dump())
    db.add(nouvelle_tache)
    db.commit()
    db.refresh(nouvelle_tache)
    return nouvelle_tache

@app.put("/taches/{id}")
def terminer_tache(id: int, db: Session = Depends(get_db),
                   utilisateur=Depends(auth.get_utilisateur_actuel)):
    tache = db.query(models.Tache).filter(models.Tache.id == id).first()
    if not tache:
        return {"erreur": "Tâche non trouvée"}
    setattr(tache, "terminee", True)
    db.commit()
    db.refresh(tache)
    return tache

@app.delete("/taches/{id}")
def supprimer_tache(id: int, db: Session = Depends(get_db),
                    utilisateur=Depends(auth.get_utilisateur_actuel)):
    tache = db.query(models.Tache).filter(models.Tache.id == id).first()
    if not tache:
        return {"erreur": "Tâche non trouvée"}
    setattr(tache, "terminee", True)
    db.delete(tache)
    db.commit()
    return {"message": "Tâche supprimée avec succès"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)