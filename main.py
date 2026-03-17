from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from database import engine, get_db
import models
import schemas
from fastapi.middleware.cors import CORSMiddleware
from auth import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_lawyer,
)

# Create tables

models.Base.metadata.create_all(bind=engine)




app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===============================
# Dummy AI Case Analyzer
# ===============================

def analyze_case(lead_data):
    score = 50  # base score

    # Accident type impact
    if "truck" in lead_data.accident_type.lower():
        score += 20
    elif "car" in lead_data.accident_type.lower():
        score += 10

    # Injury impact
    if "fracture" in lead_data.injury_description.lower():
        score += 20
    elif "minor" in lead_data.injury_description.lower():
        score -= 10

    # Liability clarity
    if "other driver" in lead_data.liability.lower():
        score += 15
    elif "unclear" in lead_data.liability.lower():
        score -= 15

    # Keep score between 0–100
    score = max(0, min(score, 100))

    # Strength classification
    if score >= 75:
        strength = "Strong"
    elif score >= 50:
        strength = "Moderate"
    else:
        strength = "Weak"

    summary = f"""
    Case involves a {lead_data.accident_type}.
    Injury reported: {lead_data.injury_description}.
    Liability: {lead_data.liability}.
    Estimated case strength: {strength}.
    """

    return score, strength, summary.strip()


# ===============================
# Register Lawyer
# ===============================

@app.post("/register/")
def register(lawyer: schemas.LawyerCreate, db: Session = Depends(get_db)):
    existing = db.query(models.Lawyer).filter(
        models.Lawyer.email == lawyer.email
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_lawyer = models.Lawyer(
        email=lawyer.email,
        hashed_password=hash_password(lawyer.password),
    )

    db.add(new_lawyer)
    db.commit()
    db.refresh(new_lawyer)

    return {"message": "Lawyer registered successfully"}


# ===============================
# Login Lawyer
# ===============================

@app.post("/login/")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    lawyer = db.query(models.Lawyer).filter(
        models.Lawyer.email == form_data.username
    ).first()

    if not lawyer or not verify_password(
        form_data.password, lawyer.hashed_password
    ):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token(data={"sub": lawyer.email})

    return {"access_token": access_token, "token_type": "bearer"}


# ===============================
# Create Lead (With AI Scoring)
# ===============================

@app.post("/leads/", response_model=schemas.LeadOut)
def create_lead(
    lead: schemas.LeadCreate,
    db: Session = Depends(get_db),
    current_lawyer: models.Lawyer = Depends(get_current_lawyer),
):
    score, strength, summary = analyze_case(lead)

    new_lead = models.Lead(
        **lead.dict(),
        score=score,
        case_strength=strength,
        summary=summary,
        lawyer_id=current_lawyer.id
    )

    db.add(new_lead)
    db.commit()
    db.refresh(new_lead)

    return new_lead


# ===============================
# Get Leads (Only Logged Lawyer)
# ===============================

@app.get("/leads/", response_model=list[schemas.LeadOut])
def get_leads(
    db: Session = Depends(get_db),
    current_lawyer: models.Lawyer = Depends(get_current_lawyer),
):
    leads = db.query(models.Lead).filter(
        models.Lead.lawyer_id == current_lawyer.id
    ).all()

    return leads


# ===============================
# Delete Lead
# ===============================

@app.delete("/leads/{lead_id}")
def delete_lead(
    lead_id: int,
    db: Session = Depends(get_db),
    current_lawyer: models.Lawyer = Depends(get_current_lawyer),
):
    lead = db.query(models.Lead).filter(
        models.Lead.id == lead_id,
        models.Lead.lawyer_id == current_lawyer.id,
    ).first()

    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    db.delete(lead)
    db.commit()

    return {"message": "Lead deleted successfully"}

@app.put("/leads/{lead_id}")
def update_lead(
    lead_id: int,
    updated_data: schemas.LeadUpdate,
    db: Session = Depends(get_db),
    current_lawyer: models.Lawyer = Depends(get_current_lawyer),
):
    lead = db.query(models.Lead).filter(
        models.Lead.id == lead_id,
        models.Lead.lawyer_id == current_lawyer.id,
    ).first()

    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    for key, value in updated_data.dict().items():
        setattr(lead, key, value)

    db.commit()
    db.refresh(lead)

    return lead
@app.get("/dashboard/")
def get_dashboard(
    db: Session = Depends(get_db),
    current_lawyer: models.Lawyer = Depends(get_current_lawyer),
):
    leads = db.query(models.Lead).filter(
        models.Lead.lawyer_id == current_lawyer.id
    ).all()

    total = len(leads)
    strong = len([l for l in leads if l.case_strength == "Strong"])
    moderate = len([l for l in leads if l.case_strength == "Moderate"])
    weak = len([l for l in leads if l.case_strength == "Weak"])
    signed = len([l for l in leads if l.status == "Signed"])

    conversion_rate = (signed / total * 100) if total > 0 else 0
@app.get("/")
def home():
    return {"message": "Legal AI API is running"}

    }
    return {
        "total_leads": total,
        "strong_cases": strong,
        "moderate_cases": moderate,
        "weak_cases": weak,
        "signed_cases": signed,
        "conversion_rate": f"{round(conversion_rate, 2)}%"


