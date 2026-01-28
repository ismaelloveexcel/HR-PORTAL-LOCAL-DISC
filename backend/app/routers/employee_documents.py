"""Employee Documents API routes - Document registry with OCR support."""

import os
import json
from datetime import date, datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.models import Employee, EmployeeDocument
from app.schemas.employee_document import (
    EmployeeDocumentCreate,
    EmployeeDocumentUpdate,
    EmployeeDocumentResponse,
    DocumentVerificationRequest,
    OCRExtractedData,
    OCRResultResponse,
    DocumentListResponse,
)
from app.auth.dependencies import require_auth, require_hr

router = APIRouter(prefix="/api/employees", tags=["Employee Documents"])

UPLOAD_DIR = "uploads/documents"
ALLOWED_EXTENSIONS = {".pdf", ".jpg", ".jpeg", ".png", ".gif", ".webp"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


def calculate_days_until_expiry(expiry_date: Optional[date]) -> Optional[int]:
    """Calculate days until a date expires."""
    if not expiry_date:
        return None
    return (expiry_date - date.today()).days


def enrich_document_response(doc: EmployeeDocument) -> EmployeeDocumentResponse:
    """Add computed fields to document response."""
    response = EmployeeDocumentResponse.model_validate(doc)
    days = calculate_days_until_expiry(doc.expiry_date)
    response.days_until_expiry = days
    response.is_expired = days is not None and days < 0
    response.is_expiring_soon = days is not None and 0 <= days <= 30
    return response


@router.get("/{employee_id}/documents", response_model=DocumentListResponse)
async def get_employee_documents(
    employee_id: str,
    document_type: Optional[str] = None,
    session: AsyncSession = Depends(get_session),
    current_user: Employee = Depends(require_auth),
):
    """Get all documents for an employee.
    
    Employees can view their own visible documents.
    HR can view all documents including HR-only ones.
    """
    result = await session.execute(
        select(Employee).where(Employee.employee_id == employee_id)
    )
    employee = result.scalar_one_or_none()
    
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    is_hr = current_user.role in ["hr", "admin"]
    is_own = current_user.employee_id == employee_id
    
    if not is_hr and not is_own:
        raise HTTPException(status_code=403, detail="Access denied")
    
    query = select(EmployeeDocument).where(EmployeeDocument.employee_id == employee.id)
    
    if not is_hr:
        query = query.where(EmployeeDocument.is_employee_visible == True)
    
    if document_type:
        query = query.where(EmployeeDocument.document_type == document_type)
    
    query = query.order_by(EmployeeDocument.created_at.desc())
    
    result = await session.execute(query)
    documents = result.scalars().all()
    
    enriched = [enrich_document_response(doc) for doc in documents]
    
    by_type = {}
    expired_count = 0
    expiring_soon_count = 0
    
    for doc in enriched:
        by_type[doc.document_type] = by_type.get(doc.document_type, 0) + 1
        if doc.is_expired:
            expired_count += 1
        elif doc.is_expiring_soon:
            expiring_soon_count += 1
    
    return DocumentListResponse(
        documents=enriched,
        total=len(enriched),
        by_type=by_type,
        expired_count=expired_count,
        expiring_soon_count=expiring_soon_count,
    )


@router.get("/{employee_id}/documents/{document_id}", response_model=EmployeeDocumentResponse)
async def get_document(
    employee_id: str,
    document_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: Employee = Depends(require_auth),
):
    """Get a specific document."""
    result = await session.execute(
        select(Employee).where(Employee.employee_id == employee_id)
    )
    employee = result.scalar_one_or_none()
    
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    result = await session.execute(
        select(EmployeeDocument).where(
            EmployeeDocument.id == document_id,
            EmployeeDocument.employee_id == employee.id,
        )
    )
    document = result.scalar_one_or_none()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    is_hr = current_user.role in ["hr", "admin"]
    is_own = current_user.employee_id == employee_id
    
    if not is_hr and not is_own:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if not is_hr and not document.is_employee_visible:
        raise HTTPException(status_code=403, detail="Document not accessible")
    
    return enrich_document_response(document)


@router.post("/{employee_id}/documents", response_model=EmployeeDocumentResponse)
async def create_document_metadata(
    employee_id: str,
    data: EmployeeDocumentCreate,
    session: AsyncSession = Depends(get_session),
    current_user: Employee = Depends(require_auth),
):
    """Create document metadata (before file upload)."""
    result = await session.execute(
        select(Employee).where(Employee.employee_id == employee_id)
    )
    employee = result.scalar_one_or_none()
    
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    is_hr = current_user.role in ["hr", "admin"]
    is_own = current_user.employee_id == employee_id
    
    if not is_hr and not is_own:
        raise HTTPException(status_code=403, detail="Access denied")
    
    document = EmployeeDocument(
        employee_id=employee.id,
        document_type=data.document_type,
        document_name=data.document_name,
        document_number=data.document_number,
        issue_date=data.issue_date,
        expiry_date=data.expiry_date,
        notes=data.notes,
        status="pending",
        uploaded_by=current_user.employee_id,
        uploaded_at=datetime.now(),
    )
    
    session.add(document)
    await session.commit()
    await session.refresh(document)
    
    return enrich_document_response(document)


@router.post("/{employee_id}/documents/{document_id}/upload")
async def upload_document_file(
    employee_id: str,
    document_id: int,
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_session),
    current_user: Employee = Depends(require_auth),
):
    """Upload file for a document. Triggers OCR if applicable."""
    result = await session.execute(
        select(Employee).where(Employee.employee_id == employee_id)
    )
    employee = result.scalar_one_or_none()
    
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    result = await session.execute(
        select(EmployeeDocument).where(
            EmployeeDocument.id == document_id,
            EmployeeDocument.employee_id == employee.id,
        )
    )
    document = result.scalar_one_or_none()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    is_hr = current_user.role in ["hr", "admin"]
    is_own = current_user.employee_id == employee_id
    
    if not is_hr and not is_own:
        raise HTTPException(status_code=403, detail="Access denied")
    
    ext = os.path.splitext(file.filename)[1].lower() if file.filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"File type not allowed. Allowed: {ALLOWED_EXTENSIONS}")
    
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large. Maximum 10MB")
    
    employee_dir = os.path.join(UPLOAD_DIR, employee_id)
    os.makedirs(employee_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = f"{document.document_type}_{timestamp}{ext}"
    file_path = os.path.join(employee_dir, safe_name)
    
    with open(file_path, "wb") as f:
        f.write(content)
    
    document.file_path = file_path
    document.file_name = file.filename
    document.file_size = len(content)
    document.file_type = file.content_type
    document.uploaded_at = datetime.now()
    document.uploaded_by = current_user.employee_id
    
    await session.commit()
    await session.refresh(document)
    
    return {
        "success": True,
        "document": enrich_document_response(document),
        "ocr_available": ext in {".jpg", ".jpeg", ".png", ".webp"},
    }


@router.post("/{employee_id}/documents/{document_id}/ocr", response_model=OCRResultResponse)
async def process_document_ocr(
    employee_id: str,
    document_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: Employee = Depends(require_auth),
):
    """Process document with OCR to extract data.
    
    Uses free open-source OCR (Tesseract/PaddleOCR).
    """
    result = await session.execute(
        select(Employee).where(Employee.employee_id == employee_id)
    )
    employee = result.scalar_one_or_none()
    
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    result = await session.execute(
        select(EmployeeDocument).where(
            EmployeeDocument.id == document_id,
            EmployeeDocument.employee_id == employee.id,
        )
    )
    document = result.scalar_one_or_none()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    if not document.file_path or not os.path.exists(document.file_path):
        raise HTTPException(status_code=400, detail="No file uploaded for this document")
    
    try:
        extracted = await perform_ocr(document.file_path, document.document_type)
        
        document.ocr_extracted_data = json.dumps(extracted.model_dump())
        document.ocr_processed = True
        document.ocr_confidence = extracted.confidence
        
        if extracted.document_number and not document.document_number:
            document.document_number = extracted.document_number
        if extracted.issue_date and not document.issue_date:
            document.issue_date = extracted.issue_date
        if extracted.expiry_date and not document.expiry_date:
            document.expiry_date = extracted.expiry_date
        
        await session.commit()
        await session.refresh(document)
        
        return OCRResultResponse(success=True, extracted_data=extracted)
    
    except Exception as e:
        return OCRResultResponse(success=False, error=str(e))


async def perform_ocr(file_path: str, document_type: str) -> OCRExtractedData:
    """Perform OCR on a document image using free Tesseract.
    
    Falls back to basic text extraction if OCR fails.
    """
    try:
        import pytesseract
        from PIL import Image
        
        img = Image.open(file_path)
        text = pytesseract.image_to_string(img, lang='eng+ara')
        
        extracted = OCRExtractedData(raw_text=text, confidence=70)
        
        import re
        
        eid_pattern = r'\b\d{3}-\d{4}-\d{7}-\d{1}\b'
        eid_match = re.search(eid_pattern, text)
        if eid_match:
            extracted.document_number = eid_match.group()
        
        date_pattern = r'\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b'
        dates = re.findall(date_pattern, text)
        
        if dates:
            from datetime import datetime
            for d in dates:
                try:
                    for fmt in ["%d/%m/%Y", "%d-%m-%Y", "%m/%d/%Y", "%Y/%m/%d"]:
                        try:
                            parsed = datetime.strptime(d, fmt).date()
                            if parsed.year > 2000:
                                if parsed > date.today():
                                    extracted.expiry_date = parsed
                                else:
                                    extracted.issue_date = parsed
                            break
                        except ValueError:
                            continue
                except:
                    pass
        
        return extracted
        
    except ImportError:
        return OCRExtractedData(
            raw_text="OCR libraries not installed. Please install pytesseract.",
            confidence=0,
        )
    except Exception as e:
        return OCRExtractedData(raw_text=str(e), confidence=0)


@router.put("/{employee_id}/documents/{document_id}", response_model=EmployeeDocumentResponse)
async def update_document(
    employee_id: str,
    document_id: int,
    data: EmployeeDocumentUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: Employee = Depends(require_auth),
):
    """Update document metadata."""
    result = await session.execute(
        select(Employee).where(Employee.employee_id == employee_id)
    )
    employee = result.scalar_one_or_none()
    
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    result = await session.execute(
        select(EmployeeDocument).where(
            EmployeeDocument.id == document_id,
            EmployeeDocument.employee_id == employee.id,
        )
    )
    document = result.scalar_one_or_none()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    is_hr = current_user.role in ["hr", "admin"]
    is_own = current_user.employee_id == employee_id
    
    if not is_hr and not is_own:
        raise HTTPException(status_code=403, detail="Access denied")
    
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(document, field, value)
    
    await session.commit()
    await session.refresh(document)
    
    return enrich_document_response(document)


@router.post("/{employee_id}/documents/{document_id}/verify", response_model=EmployeeDocumentResponse)
async def verify_document(
    employee_id: str,
    document_id: int,
    request: DocumentVerificationRequest,
    session: AsyncSession = Depends(get_session),
    current_user: Employee = Depends(require_hr),
):
    """Verify or reject a document. HR-only."""
    result = await session.execute(
        select(Employee).where(Employee.employee_id == employee_id)
    )
    employee = result.scalar_one_or_none()
    
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    result = await session.execute(
        select(EmployeeDocument).where(
            EmployeeDocument.id == document_id,
            EmployeeDocument.employee_id == employee.id,
        )
    )
    document = result.scalar_one_or_none()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    if request.action == "verify":
        document.status = "verified"
        document.verified_by = current_user.employee_id
        document.verified_at = datetime.now()
        document.rejection_reason = None
    else:
        document.status = "rejected"
        document.rejection_reason = request.rejection_reason
        document.verified_by = current_user.employee_id
        document.verified_at = datetime.now()
    
    await session.commit()
    await session.refresh(document)
    
    return enrich_document_response(document)


@router.delete("/{employee_id}/documents/{document_id}")
async def delete_document(
    employee_id: str,
    document_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: Employee = Depends(require_hr),
):
    """Delete a document. HR-only."""
    result = await session.execute(
        select(Employee).where(Employee.employee_id == employee_id)
    )
    employee = result.scalar_one_or_none()
    
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    result = await session.execute(
        select(EmployeeDocument).where(
            EmployeeDocument.id == document_id,
            EmployeeDocument.employee_id == employee.id,
        )
    )
    document = result.scalar_one_or_none()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    if document.file_path and os.path.exists(document.file_path):
        os.remove(document.file_path)
    
    await session.delete(document)
    await session.commit()
    
    return {"success": True, "message": "Document deleted"}
