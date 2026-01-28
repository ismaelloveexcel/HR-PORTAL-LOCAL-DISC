from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field


class PerformanceCycleCreate(BaseModel):
    name: str
    cycle_type: str = "annual"
    start_date: date
    end_date: date
    self_assessment_deadline: Optional[date] = None
    manager_review_deadline: Optional[date] = None


class PerformanceCycleUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None
    self_assessment_deadline: Optional[date] = None
    manager_review_deadline: Optional[date] = None


class PerformanceCycleResponse(BaseModel):
    id: int
    name: str
    cycle_type: str
    start_date: date
    end_date: date
    self_assessment_deadline: Optional[date]
    manager_review_deadline: Optional[date]
    status: str
    created_at: datetime
    review_count: int = 0
    
    model_config = ConfigDict(from_attributes=True)


class PerformanceRatingCreate(BaseModel):
    competency_name: str
    competency_category: str = "core"
    weight: int = 0
    self_rating: Optional[int] = Field(None, ge=1, le=5)
    self_comments: Optional[str] = None
    manager_rating: Optional[int] = Field(None, ge=1, le=5)
    manager_comments: Optional[str] = None


class PerformanceRatingResponse(BaseModel):
    id: int
    competency_name: str
    competency_category: str
    weight: int
    self_rating: Optional[int]
    self_comments: Optional[str]
    manager_rating: Optional[int]
    manager_comments: Optional[str]
    
    model_config = ConfigDict(from_attributes=True)


class SelfAssessmentSubmit(BaseModel):
    self_achievements: Optional[str] = None
    self_challenges: Optional[str] = None
    self_goals_next_period: Optional[str] = None
    self_training_needs: Optional[str] = None
    self_overall_comments: Optional[str] = None
    ratings: List[PerformanceRatingCreate] = []


class ManagerReviewSubmit(BaseModel):
    manager_achievements: Optional[str] = None
    manager_areas_improvement: Optional[str] = None
    manager_recommendations: Optional[str] = None
    manager_overall_comments: Optional[str] = None
    overall_rating: Optional[Decimal] = Field(None, ge=1, le=5)
    rating_label: Optional[str] = None
    ratings: List[PerformanceRatingCreate] = []


class PerformanceReviewCreate(BaseModel):
    cycle_id: int
    employee_id: int
    reviewer_id: Optional[int] = None


class PerformanceReviewResponse(BaseModel):
    id: int
    cycle_id: int
    employee_id: int
    reviewer_id: Optional[int]
    status: str
    
    self_assessment_submitted: bool
    self_assessment_date: Optional[datetime]
    self_achievements: Optional[str]
    self_challenges: Optional[str]
    self_goals_next_period: Optional[str]
    self_training_needs: Optional[str]
    self_overall_comments: Optional[str]
    
    manager_review_submitted: bool
    manager_review_date: Optional[datetime]
    manager_achievements: Optional[str]
    manager_areas_improvement: Optional[str]
    manager_recommendations: Optional[str]
    manager_overall_comments: Optional[str]
    
    overall_rating: Optional[Decimal]
    rating_label: Optional[str]
    
    created_at: datetime
    updated_at: Optional[datetime]
    
    employee_name: Optional[str] = None
    employee_department: Optional[str] = None
    employee_job_title: Optional[str] = None
    reviewer_name: Optional[str] = None
    cycle_name: Optional[str] = None
    
    ratings: List[PerformanceRatingResponse] = []
    
    model_config = ConfigDict(from_attributes=True)


class BulkReviewCreate(BaseModel):
    cycle_id: int
    employee_ids: List[int]


class PerformanceStats(BaseModel):
    total_reviews: int
    pending: int
    self_assessment: int
    manager_review: int
    completed: int
    average_rating: Optional[float] = None
