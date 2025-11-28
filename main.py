from fastapi import FastAPI
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base
from pydantic import BaseModel, Field
from passlib.context import CryptContext
from fastapi import Depends, HTTPException

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Welcome Students"}

DATABASE_URL = "sqlite:///books.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class User(Base):
    __tablename__ = "Users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)


class Course(Base):
    __tablename__ = "Course"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    professor = Column(String)
    description = Column(String)

Base.metadata.create_all(bind=engine)



class UserCreate(BaseModel):
    username: str
    password: str = Field(ax_length=72)


class ClassCreate(BaseModel):
    title: str
    professor: str
    description: str



pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str):
    return pwd_context.hash(password)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/register")
def register(user: UserCreate, db: SessionLocal = Depends(get_db)): # type: ignore
    existing = db.query(User).filter(User.username == user.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already taken")
    
    hashed_pw = hash_password(user.password)
    new_user = User(username=user.username, password=hashed_pw)
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "User created successfully"}


