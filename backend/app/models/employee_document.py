from datetime import date, datetime
from typing import Optional, TYPE_CHECKING

from sqlalchemy import Boolean, Date, DateTime, Enum, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.models.renewal import Base

if TYPE_CHECKING:
    from app.models.employee import Employee


class DocumentType(str, enum.Enum):
    """Types of employee documents."""
    PASSPORT = "passport"
    VISA = "visa"
    EMIRATES_ID = "emirates_id"
    WORK_PERMIT = "work_permit"
    MEDICAL_FITNESS = "medical_fitness"
    DRIVING_LICENSE = "driving_license"
    EDUCATIONAL = "educational"
    CONTRACT = "contract"
    OFFER_LETTER = "offer_letter"
    PROMOTION_LETTER = "promotion_letter"
    EXPERIENCE_CERTIFICATE = "experience_certificate"
    TRAINING_CERTIFICATE = "training_certificate"
    SECURITY_CLEARANCE = "security_clearance"
    BANK_LETTER = "bank_letter"
    JOB_DESCRIPTION = "job_description"
    PROFILE_PHOTO = "profile_photo"
    PERSONAL_DOCUMENT = "personal_document"
    OTHER = "other"


class DocumentStatus(str, enum.Enum):
    """Document verification status."""
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"
    EXPIRED = "expired"
    EXPIRING_SOON = "expiring_soon"


class EmployeeDocument(Base):
    """Document registry with metadata.
    
    Stores document metadata first, then file attachments.
    Tracks expiry dates and sends alerts for renewals.
    Supports OCR auto-fill for ID documents.
    """

    __tablename__ = "employee_documents"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    employee_id: Mapped[int] = mapped_column(
        ForeignKey("employees.id", ondelete="CASCADE"), 
        nullable=False,
        index=True
    )
    
    # Document identification
    document_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    document_name: Mapped[str] = mapped_column(String(200), nullable=False)
    document_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Dates
    issue_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    expiry_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True, index=True)
    
    # Status
    status: Mapped[str] = mapped_column(
        String(50), 
        default=DocumentStatus.PENDING.value, 
        nullable=False,
        index=True
    )
    
    # File storage
    file_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    file_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    file_size: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    file_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # OCR extracted data (stored as JSON-like text)
    ocr_extracted_data: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ocr_processed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    ocr_confidence: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Verification
    verified_by: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    rejection_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Upload tracking
    uploaded_by: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    uploaded_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Alert tracking
    expiry_alert_sent: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    expiry_alert_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Notes
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Visibility (some documents are employee-visible, some are HR-only)
    is_employee_visible: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
    
    # Relationship
    employee: Mapped["Employee"] = relationship(back_populates="documents")
