from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from PIL import Image
import io

from ..models import schemas, db_models, database
from ..services.model_service import analyze_fruit
from .auth import get_current_user

router = APIRouter()

@router.post("/analyze", response_model=schemas.AnalysisResult)
async def analyze_image(
    file: UploadFile = File(...),
    current_user: db_models.User = Depends(get_current_user),
    db: Session = Depends(database.get_db)
):
    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents)).convert("RGB")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid image file: {str(e)}")

    try:
        result = analyze_fruit(image)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing image: {str(e)}")

    # Save to history
    history_record = db_models.History(
        fruit_name=result["fruit_name"],
        confidence=result["confidence"],
        quality=result["quality"],
        quality_confidence=result["quality_confidence"],
        size_cm=result["size_cm"],
        image_mask=result["mask"],
        owner_id=current_user.id
    )
    db.add(history_record)
    db.commit()
    db.refresh(history_record)

    return result

@router.get("/history", response_model=List[schemas.History])
def get_history(
    skip: int = 0, 
    limit: int = 100, 
    current_user: db_models.User = Depends(get_current_user),
    db: Session = Depends(database.get_db)
):
    histories = db.query(db_models.History).filter(db_models.History.owner_id == current_user.id).order_by(db_models.History.timestamp.desc()).offset(skip).limit(limit).all()
    return histories
