from datetime import datetime
from typing import Optional, TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.renewal import Base

if TYPE_CHECKING:
    from app.models.employee import Employee


class EmployeeProfile(Base):
    """Employee self-service profile data.
    
    Contains fields that employees can fill in themselves during onboarding
    or update later. Separate from the main Employee model to clearly
    distinguish HR-managed vs employee-managed data.
    """

    __tablename__ = "employee_profiles"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    employee_id: Mapped[int] = mapped_column(
        ForeignKey("employees.id", ondelete="CASCADE"), 
        unique=True, 
        nullable=False
    )
    
    # Emergency contact
    emergency_contact_name: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    emergency_contact_phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    emergency_contact_relationship: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # Secondary emergency contact
    emergency_contact_2_name: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    emergency_contact_2_phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    emergency_contact_2_relationship: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # Personal contact
    personal_phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    personal_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Address
    current_address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    permanent_address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    country: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Bank details
    bank_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    bank_account_number: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    bank_iban: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    bank_swift_code: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    
    # Passport and ID
    passport_number: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    passport_expiry: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    national_id_number: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    uae_id_number: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    uae_id_expiry: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    
    # Driving license
    driving_license_number: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    driving_license_expiry: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    driving_license_country: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Education
    highest_education: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    education_institution: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    graduation_year: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Uniform sizes (for manufacturing/field staff)
    shirt_size: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    pants_size: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    shoe_size: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    
    # Notes
    dietary_restrictions: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    medical_conditions: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    additional_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Submission tracking
    submitted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    reviewed_by: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
    
    # Relationship
    employee: Mapped["Employee"] = relationship(back_populates="profile")
