from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class EmployeeDocumentBase(BaseModel):
    """Base schema for employee documents."""
    document_type: str
    document_name: str
    document_number: Optional[str] = None
    issue_date: Optional[date] = None
    expiry_date: Optional[date] = None
    notes: Optional[str] = None


class EmployeeDocumentCreate(EmployeeDocumentBase):
    """Schema for creating document metadata."""
    employee_id: int


class EmployeeDocumentUpdate(BaseModel):
    """Schema for updating document metadata."""
    document_name: Optional[str] = None
    document_number: Optional[str] = None
    issue_date: Optional[date] = None
    expiry_date: Optional[date] = None
    notes: Optional[str] = None


class EmployeeDocumentResponse(EmployeeDocumentBase):
    """Schema for document response."""
    id: int
    employee_id: int
    status: str
    file_path: Optional[str] = None
    file_name: Optional[str] = None
    file_size: Optional[int] = None
    file_type: Optional[str] = None
    ocr_processed: bool = False
    ocr_confidence: Optional[int] = None
    verified_by: Optional[str] = None
    verified_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    uploaded_by: Optional[str] = None
    uploaded_at: Optional[datetime] = None
    is_employee_visible: bool = True
    created_at: datetime
    updated_at: datetime
    
    # Computed fields
    days_until_expiry: Optional[int] = None
    is_expired: bool = False
    is_expiring_soon: bool = False
    
    model_config = ConfigDict(from_attributes=True)


class DocumentVerificationRequest(BaseModel):
    """Request to verify or reject a document."""
    action: str = Field(..., pattern="^(verify|reject)$")
    rejection_reason: Optional[str] = None


class OCRExtractedData(BaseModel):
    """Data extracted from document via OCR."""
    document_number: Optional[str] = None
    name: Optional[str] = None
    name_arabic: Optional[str] = None
    date_of_birth: Optional[date] = None
    issue_date: Optional[date] = None
    expiry_date: Optional[date] = None
    nationality: Optional[str] = None
    gender: Optional[str] = None
    raw_text: Optional[str] = None
    confidence: Optional[int] = None


class OCRResultResponse(BaseModel):
    """Response after OCR processing."""
    success: bool
    extracted_data: Optional[OCRExtractedData] = None
    error: Optional[str] = None


class DocumentListResponse(BaseModel):
    """Response for document listing."""
    documents: list[EmployeeDocumentResponse]
    total: int
    by_type: dict[str, int]
    expired_count: int
    expiring_soon_count: int
