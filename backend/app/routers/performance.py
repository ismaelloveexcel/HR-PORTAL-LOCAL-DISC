from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.auth.dependencies import require_auth, require_hr
from app.models.employee import Employee
from app.schemas.performance import (
    PerformanceCycleCreate, PerformanceCycleUpdate, PerformanceCycleResponse,
    PerformanceReviewCreate, PerformanceReviewResponse,
    SelfAssessmentSubmit, ManagerReviewSubmit,
    BulkReviewCreate, PerformanceStats
)
from app.services.performance_service import performance_service

router = APIRouter(prefix="/performance", tags=["Performance Management"])


@router.get("/cycles", response_model=List[PerformanceCycleResponse])
async def list_cycles(
    status: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_session),
    current_user: Employee = Depends(require_auth)
):
    cycles = await performance_service.get_cycles(db, status)
    result = []
    for cycle in cycles:
        stats = await performance_service.get_cycle_stats(db, cycle.id)
        result.append({
            "id": cycle.id,
            "name": cycle.name,
            "cycle_type": cycle.cycle_type,
            "start_date": cycle.start_date,
            "end_date": cycle.end_date,
            "self_assessment_deadline": cycle.self_assessment_deadline,
            "manager_review_deadline": cycle.manager_review_deadline,
            "status": cycle.status,
            "created_at": cycle.created_at,
            "review_count": stats["total_reviews"]
        })
    return result


@router.post("/cycles", response_model=PerformanceCycleResponse)
async def create_cycle(
    data: PerformanceCycleCreate,
    db: AsyncSession = Depends(get_session),
    current_user: Employee = Depends(require_hr)
):
    cycle = await performance_service.create_cycle(db, data, current_user.employee_id)
    return {
        "id": cycle.id,
        "name": cycle.name,
        "cycle_type": cycle.cycle_type,
        "start_date": cycle.start_date,
        "end_date": cycle.end_date,
        "self_assessment_deadline": cycle.self_assessment_deadline,
        "manager_review_deadline": cycle.manager_review_deadline,
        "status": cycle.status,
        "created_at": cycle.created_at,
        "review_count": 0
    }


@router.get("/cycles/{cycle_id}", response_model=PerformanceCycleResponse)
async def get_cycle(
    cycle_id: int,
    db: AsyncSession = Depends(get_session),
    current_user: Employee = Depends(require_auth)
):
    cycle = await performance_service.get_cycle(db, cycle_id)
    if not cycle:
        raise HTTPException(status_code=404, detail="Cycle not found")
    stats = await performance_service.get_cycle_stats(db, cycle_id)
    return {
        "id": cycle.id,
        "name": cycle.name,
        "cycle_type": cycle.cycle_type,
        "start_date": cycle.start_date,
        "end_date": cycle.end_date,
        "self_assessment_deadline": cycle.self_assessment_deadline,
        "manager_review_deadline": cycle.manager_review_deadline,
        "status": cycle.status,
        "created_at": cycle.created_at,
        "review_count": stats["total_reviews"]
    }


@router.put("/cycles/{cycle_id}", response_model=PerformanceCycleResponse)
async def update_cycle(
    cycle_id: int,
    data: PerformanceCycleUpdate,
    db: AsyncSession = Depends(get_session),
    current_user: Employee = Depends(require_hr)
):
    cycle = await performance_service.update_cycle(db, cycle_id, data)
    if not cycle:
        raise HTTPException(status_code=404, detail="Cycle not found")
    stats = await performance_service.get_cycle_stats(db, cycle_id)
    return {
        "id": cycle.id,
        "name": cycle.name,
        "cycle_type": cycle.cycle_type,
        "start_date": cycle.start_date,
        "end_date": cycle.end_date,
        "self_assessment_deadline": cycle.self_assessment_deadline,
        "manager_review_deadline": cycle.manager_review_deadline,
        "status": cycle.status,
        "created_at": cycle.created_at,
        "review_count": stats["total_reviews"]
    }


@router.get("/cycles/{cycle_id}/stats", response_model=PerformanceStats)
async def get_cycle_stats(
    cycle_id: int,
    db: AsyncSession = Depends(get_session),
    current_user: Employee = Depends(require_auth)
):
    stats = await performance_service.get_cycle_stats(db, cycle_id)
    return stats


@router.get("/reviews", response_model=List[PerformanceReviewResponse])
async def list_reviews(
    cycle_id: Optional[int] = Query(None),
    employee_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_session),
    current_user: Employee = Depends(require_auth)
):
    reviews = await performance_service.get_reviews(db, cycle_id, employee_id, status=status)
    return reviews


@router.post("/reviews", response_model=PerformanceReviewResponse)
async def create_review(
    data: PerformanceReviewCreate,
    db: AsyncSession = Depends(get_session),
    current_user: Employee = Depends(require_hr)
):
    review = await performance_service.create_review(db, data)
    return await performance_service.get_review(db, review.id)


@router.post("/reviews/bulk")
async def create_bulk_reviews(
    data: BulkReviewCreate,
    db: AsyncSession = Depends(get_session),
    current_user: Employee = Depends(require_hr)
):
    reviews = await performance_service.create_bulk_reviews(db, data)
    return {"created": len(reviews)}


@router.get("/reviews/{review_id}", response_model=PerformanceReviewResponse)
async def get_review(
    review_id: int,
    db: AsyncSession = Depends(get_session),
    current_user: Employee = Depends(require_auth)
):
    review = await performance_service.get_review(db, review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    return review


@router.post("/reviews/{review_id}/self-assessment")
async def submit_self_assessment(
    review_id: int,
    data: SelfAssessmentSubmit,
    db: AsyncSession = Depends(get_session),
    current_user: Employee = Depends(require_auth)
):
    review = await performance_service.get_review(db, review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    if review["employee_id"] != current_user.id and current_user.role not in ["admin", "hr"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    updated = await performance_service.submit_self_assessment(db, review_id, data)
    return {"status": "submitted", "review_id": updated.id}


@router.post("/reviews/{review_id}/manager-review")
async def submit_manager_review(
    review_id: int,
    data: ManagerReviewSubmit,
    db: AsyncSession = Depends(get_session),
    current_user: Employee = Depends(require_auth)
):
    review = await performance_service.get_review(db, review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    if review["reviewer_id"] != current_user.id and current_user.role not in ["admin", "hr"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    updated = await performance_service.submit_manager_review(db, review_id, data)
    return {"status": "completed", "review_id": updated.id}


@router.get("/my-reviews", response_model=List[PerformanceReviewResponse])
async def get_my_reviews(
    db: AsyncSession = Depends(get_session),
    current_user: Employee = Depends(require_auth)
):
    reviews = await performance_service.get_employee_reviews(db, current_user.id)
    return reviews


@router.get("/team-reviews", response_model=List[PerformanceReviewResponse])
async def get_team_reviews(
    db: AsyncSession = Depends(get_session),
    current_user: Employee = Depends(require_auth)
):
    reviews = await performance_service.get_manager_reviews(db, current_user.id)
    return reviews


@router.post("/reviews/{review_id}/submit")
async def submit_review(
    review_id: int,
    db: AsyncSession = Depends(get_session),
    current_user: Employee = Depends(require_auth)
):
    """
    Submit a review after self-assessment is complete.
    
    Transitions review from self_assessment to manager_review status.
    Employee must complete self-assessment before submission.
    """
    review = await performance_service.get_review(db, review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    if review["employee_id"] != current_user.id and current_user.role not in ["admin", "hr"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    try:
        updated = await performance_service.submit_review(db, review_id)
        return {
            "status": "submitted",
            "review_id": updated.id,
            "message": "Review submitted for manager approval"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/reviews/{review_id}/approve")
async def approve_review(
    review_id: int,
    db: AsyncSession = Depends(get_session),
    current_user: Employee = Depends(require_auth)
):
    """
    Manager approves the review (final approval).
    
    Transitions to completed status and calculates final rating.
    Manager must complete manager review before approval.
    """
    review = await performance_service.get_review(db, review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    if review["reviewer_id"] != current_user.id and current_user.role not in ["admin", "hr"]:
        raise HTTPException(status_code=403, detail="Not authorized to approve")
    
    try:
        updated = await performance_service.approve_review(db, review_id, current_user.id)
        return {
            "status": "approved",
            "review_id": updated.id,
            "final_rating": float(updated.overall_rating) if updated.overall_rating else None,
            "rating_label": updated.rating_label,
            "message": "Review approved and completed"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/reviews/{review_id}/final-rating")
async def get_final_rating(
    review_id: int,
    db: AsyncSession = Depends(get_session),
    current_user: Employee = Depends(require_auth)
):
    """
    Get the final rating for a review with detailed breakdown.
    
    Returns:
    - Final rating (1-5 scale)
    - Rating label (Outstanding, Exceeds Expectations, etc.)
    - Breakdown by competency with weights and scores
    """
    result = await performance_service.get_final_rating(db, review_id)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


@router.get("/reports/summary")
async def get_performance_summary(
    cycle_id: int = Query(..., description="Performance cycle ID"),
    db: AsyncSession = Depends(get_session),
    current_user: Employee = Depends(require_hr)
):
    """
    Get performance cycle summary report.
    
    **Admin and HR only.**
    
    Returns:
    - Cycle statistics (completed, pending, average rating)
    - List of completed reviews with final ratings
    - List of pending reviews with current status
    """
    result = await performance_service.get_cycle_summary(db, cycle_id)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


@router.get("/reports/employee/{employee_id}")
async def get_employee_performance_history(
    employee_id: int,
    db: AsyncSession = Depends(get_session),
    current_user: Employee = Depends(require_auth)
):
    """
    Get performance review history for an employee.
    
    Returns all performance reviews across cycles with ratings and dates.
    Employees can view their own history. Managers/HR can view any employee.
    """
    # Check authorization
    if current_user.id != employee_id and current_user.role not in ["admin", "hr"]:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to view this employee's history"
        )
    
    history = await performance_service.get_employee_history(db, employee_id)
    return {"employee_id": employee_id, "reviews": history}
