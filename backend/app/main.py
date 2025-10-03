from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from datetime import datetime, timedelta
from typing import Optional
import pandas as pd
import os
from pydantic import BaseModel
from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "changeme123")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

app = FastAPI(title="Marketing Metrics API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "https://*.vercel.app", "http://localhost"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(__file__)
USERS_CSV = os.path.normpath(os.path.join(BASE_DIR, "../data/users.csv"))
METRICS_CSV = os.path.normpath(os.path.join(BASE_DIR, "../data/metrics.csv"))

# Load data
users_df = pd.read_csv(USERS_CSV)
metrics_df = pd.read_csv(METRICS_CSV, parse_dates=["date"])  # expect 'date' column

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None


class User(BaseModel):
    email: str
    full_name: Optional[str] = None
    role: str


def verify_password(plain_password, hashed_password):
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        return False


def get_password_hash(password):
    return pwd_context.hash(password)


def authenticate_user(email: str, password: str):
    row = users_df[users_df.email == email]
    if row.empty:
        return None
    user = row.iloc[0]
    if not verify_password(password, user.password_hash):
        return None
    return User(email=user.email, full_name=user.full_name, role=user.role)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception
    row = users_df[users_df.email == token_data.email]
    if row.empty:
        raise credentials_exception
    user = row.iloc[0]
    return User(email=user.email, full_name=user.full_name, role=user.role)


@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/register")
async def register(email: str, password: str):
    """Register a user only if the email exists in the provided users.csv and has no password yet.
    This follows the project's constraint: registrations are limited to known users.
    """
    global users_df
    row = users_df[users_df.email == email]
    if row.empty:
        raise HTTPException(status_code=400, detail="Email not found in allowed users")
    existing_hash = row.iloc[0].get("password_hash", "")
    if pd.notna(existing_hash) and str(existing_hash).strip() != "":
        raise HTTPException(status_code=400, detail="User already registered; use login")
    hashed = get_password_hash(password)
    users_df.loc[users_df.email == email, "password_hash"] = hashed
    # persist the change to disk so subsequent runs/readers see it
    users_df.to_csv(USERS_CSV, index=False)
    return {"msg": "registered"}


@app.get("/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user


@app.get("/metrics")
async def get_metrics(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    sort_by: Optional[str] = None,
    sort_dir: str = "asc",
    page: int = 1,
    page_size: int = 100,
    current_user: User = Depends(get_current_user),
):
    df = metrics_df.copy()
    if start_date:
        df = df[df.date >= pd.to_datetime(start_date)]
    if end_date:
        df = df[df.date <= pd.to_datetime(end_date)]

    if sort_by:
        if sort_by not in df.columns:
            raise HTTPException(status_code=400, detail=f"Invalid sort_by column: {sort_by}")
        ascending = True if str(sort_dir).lower() == "asc" else False
        # handle missing values gracefully
        df = df.sort_values(by=sort_by, ascending=ascending, na_position="last")

    # pagination
    page_size = max(1, min(page_size, 1000))
    page = max(1, page)
    start = (page - 1) * page_size
    end = start + page_size
    total = len(df)
    rows = df.iloc[start:end].to_dict(orient="records")

    # If user is not admin, remove cost_micros
    if current_user.role != "admin":
        for r in rows:
            r.pop("cost_micros", None)

    return {"data": rows, "page": page, "page_size": page_size, "total": total}

