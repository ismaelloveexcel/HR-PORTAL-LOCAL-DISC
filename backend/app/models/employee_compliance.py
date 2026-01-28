from datetime import date, datetime
from typing import Optional, TYPE_CHECKING

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.renewal import Base

if TYPE_CHECKING:
    from app.models.employee import Employee


class EmployeeCompliance(Base):
    """UAE Compliance data - HR-only access.
    
    Contains visa, Emirates ID, medical fitness, insurance (ILOE),
    and contract information. This is sensitive HR data that
    employees cannot edit directly.
    """

    __tablename__ = "employee_compliance"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    employee_id: Mapped[int] = mapped_column(
        ForeignKey("employees.id", ondelete="CASCADE"), 
        unique=True, 
        nullable=False,
        index=True
    )
    
    # Visa Information
    visa_number: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    visa_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    visa_status: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    visa_issue_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    visa_expiry_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    visa_sponsor: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Emirates ID
    emirates_id_number: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    emirates_id_issue_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    emirates_id_expiry: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    emirates_id_status: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # Medical Fitness Certificate
    medical_fitness_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    medical_fitness_expiry: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    medical_fitness_status: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    medical_fitness_location: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # ILOE (Insurance)
    iloe_policy_number: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    iloe_status: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    iloe_provider: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    iloe_start_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    iloe_expiry: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    
    # Medical Insurance
    medical_insurance_number: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    medical_insurance_provider: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    medical_insurance_category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    medical_insurance_start: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    medical_insurance_expiry: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    
    # Contract
    contract_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    contract_number: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    contract_start_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    contract_end_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    contract_status: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # Security Clearance
    security_clearance: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    security_clearance_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    security_clearance_expiry: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    
    # Work Permit
    work_permit_number: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    work_permit_issue_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    work_permit_expiry: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    
    # Audit fields
    last_verified_by: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    last_verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
    
    # Relationship
    employee: Mapped["Employee"] = relationship(back_populates="compliance")
