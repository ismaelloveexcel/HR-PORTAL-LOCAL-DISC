from datetime import date, datetime
from decimal import Decimal
from typing import Optional, TYPE_CHECKING

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, Numeric, String, Text, func, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.renewal import Base

if TYPE_CHECKING:
    from app.models.employee import Employee


class PerformanceCycle(Base):
    """Performance review cycle (e.g., Annual 2025, Q1 2025)"""
    
    __tablename__ = "performance_cycles"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    cycle_type: Mapped[str] = mapped_column(String(50), nullable=False)  # annual, quarterly, probation
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    self_assessment_deadline: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    manager_review_deadline: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="draft", nullable=False)  # draft, active, completed
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    created_by: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    reviews: Mapped[list["PerformanceReview"]] = relationship("PerformanceReview", back_populates="cycle")


class PerformanceReview(Base):
    """Individual performance review for an employee"""
    
    __tablename__ = "performance_reviews"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    cycle_id: Mapped[int] = mapped_column(ForeignKey("performance_cycles.id"), nullable=False)
    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id"), nullable=False)
    reviewer_id: Mapped[Optional[int]] = mapped_column(ForeignKey("employees.id"), nullable=True)
    
    status: Mapped[str] = mapped_column(String(30), default="pending", nullable=False)
    # pending, self_assessment, manager_review, completed
    
    # Self-assessment
    self_assessment_submitted: Mapped[bool] = mapped_column(Boolean, default=False)
    self_assessment_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    self_achievements: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    self_challenges: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    self_goals_next_period: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    self_training_needs: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    self_overall_comments: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Manager review
    manager_review_submitted: Mapped[bool] = mapped_column(Boolean, default=False)
    manager_review_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    manager_achievements: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    manager_areas_improvement: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    manager_recommendations: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    manager_overall_comments: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Overall rating (1-5)
    overall_rating: Mapped[Optional[Decimal]] = mapped_column(Numeric(3, 2), nullable=True)
    rating_label: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    # Outstanding, Exceeds Expectations, Meets Expectations, Developing, Needs Improvement
    
    # Reminder system
    reminder_sent: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    reminder_sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, onupdate=func.now(), nullable=True)
    
    cycle: Mapped["PerformanceCycle"] = relationship("PerformanceCycle", back_populates="reviews")
    ratings: Mapped[list["PerformanceRating"]] = relationship("PerformanceRating", back_populates="review")


class PerformanceRating(Base):
    """Individual competency ratings within a review"""
    
    __tablename__ = "performance_ratings"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    review_id: Mapped[int] = mapped_column(ForeignKey("performance_reviews.id"), nullable=False)
    competency_name: Mapped[str] = mapped_column(String(100), nullable=False)
    competency_category: Mapped[str] = mapped_column(String(50), nullable=False)  # core, values, leadership
    weight: Mapped[int] = mapped_column(Integer, default=0)  # percentage weight
    
    self_rating: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # 1-5
    self_comments: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    manager_rating: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # 1-5
    manager_comments: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    review: Mapped["PerformanceReview"] = relationship("PerformanceReview", back_populates="ratings")
