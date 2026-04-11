from pydantic import BaseModel, ConfigDict

class TacheCreate(BaseModel):
    titre: str
    description: str = ""
    terminee: bool = False

class TacheResponse(TacheCreate):
    id:int

    model_config = ConfigDict(from_attributes=True)

class UtilisateurCreate(BaseModel):
    nom: str
    email: str
    mot_de_passe: str

class Token(BaseModel):
    access_token: str
    token_type: str

class UtilisateurResponse(UtilisateurCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)