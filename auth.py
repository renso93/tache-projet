from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from database import get_db
import models
from dotenv import load_dotenv
import os

load_dotenv(encoding="utf-8")

# Configuration pour JWT
SECRET_KEY = os.getenv("SECRET_KEY", "votre_cle_secrete_pour_jwt")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))


""" # Configuration pour JWT 
SECRET_KEY = "votre_cle_secrete_pour_jwt"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30 """

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def hasher_mot_de_passe(mot_de_passe: str) -> str:
    return pwd_context.hash(mot_de_passe)

def verifier_mot_de_passe(mot_de_passe: str, hash: str) -> bool:
    return pwd_context.verify(mot_de_passe, hash)

def creer_token(data: dict) -> str:
    expiration  = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES) 
    data.update({"exp": expiration})
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

def verifier_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("user_id")
        if user_id is None:
            raise credentials_exception
        return user_id
    except JWTError:
        raise credentials_exception
    
def get_utilisateur_actuel(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token invalide")
        utilisateur = db.query(models.Utilisateur).filter(models.Utilisateur.email == email).first()
        if utilisateur is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Utilisateur non trouvé")
        return utilisateur
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token invalide")