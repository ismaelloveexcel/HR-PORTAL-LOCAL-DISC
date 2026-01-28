from datetime import datetime
from typing import List, Optional
from decimal import Decimal

from sqlalchemy import select, func, Integer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.performance import PerformanceCycle, PerformanceReview, PerformanceRating
from app.models.employee import Employee
from app.schemas.performance import (
    PerformanceCycleCreate, PerformanceCycleUpdate,
    PerformanceReviewCreate, SelfAssessmentSubmit, ManagerReviewSubmit,
    PerformanceRatingCreate, BulkReviewCreate
)


DEFAULT_COMPETENCIES = [
    {"name": "Job Knowledge & Skills", "category": "core", "weight": 20},
    {"name": "Quality of Work", "category": "core", "weight": 20},
    {"name": "Productivity & Efficiency", "category": "core", "weight": 15},
    {"name": "Communication & Collaboration", "category": "core", "weight": 15},
    {"name": "Initiative & Problem Solving", "category": "core", "weight": 15},
    {"name": "Integrity & Ethics", "category": "values", "weight": 10},
    {"name": "Adaptability & Growth", "category": "values", "weight": 5},
]

RATING_LABELS = {
    5: "Outstanding",
    4: "Exceeds Expectations",
    3: "Meets Expectations",
    2: "Developing",
    1: "Needs Improvement"
}


class PerformanceService:
    
    async def get_cycles(self, db: AsyncSession, status: Optional[str] = None) -> List[PerformanceCycle]:
        query = select(PerformanceCycle).order_by(PerformanceCycle.start_date.desc())
        if status:
            query = query.where(PerformanceCycle.status == status)
        result = await db.execute(query)
        return result.scalars().all()
    
    async def get_cycle(self, db: AsyncSession, cycle_id: int) -> Optional[PerformanceCycle]:
        result = await db.execute(
            select(PerformanceCycle).where(PerformanceCycle.id == cycle_id)
        )
        return result.scalar_one_or_none()
    
    async def create_cycle(self, db: AsyncSession, data: PerformanceCycleCreate, created_by: str) -> PerformanceCycle:
        cycle = PerformanceCycle(
            name=data.name,
            cycle_type=data.cycle_type,
            start_date=data.start_date,
            end_date=data.end_date,
            self_assessment_deadline=data.self_assessment_deadline,
            manager_review_deadline=data.manager_review_deadline,
            status="draft",
            created_by=created_by
        )
        db.add(cycle)
        await db.commit()
        await db.refresh(cycle)
        return cycle
    
    async def update_cycle(self, db: AsyncSession, cycle_id: int, data: PerformanceCycleUpdate) -> Optional[PerformanceCycle]:
        cycle = await self.get_cycle(db, cycle_id)
        if not cycle:
            return None
        
        if data.name is not None:
            cycle.name = data.name
        if data.status is not None:
            cycle.status = data.status
        if data.self_assessment_deadline is not None:
            cycle.self_assessment_deadline = data.self_assessment_deadline
        if data.manager_review_deadline is not None:
            cycle.manager_review_deadline = data.manager_review_deadline
        
        await db.commit()
        await db.refresh(cycle)
        return cycle
    
    async def get_cycle_stats(self, db: AsyncSession, cycle_id: int) -> dict:
        result = await db.execute(
            select(
                func.count(PerformanceReview.id).label("total"),
                func.sum(func.cast(PerformanceReview.status == "pending", Integer)).label("pending"),
                func.sum(func.cast(PerformanceReview.status == "self_assessment", Integer)).label("self_assessment"),
                func.sum(func.cast(PerformanceReview.status == "manager_review", Integer)).label("manager_review"),
                func.sum(func.cast(PerformanceReview.status == "completed", Integer)).label("completed"),
                func.avg(PerformanceReview.overall_rating).label("avg_rating")
            ).where(PerformanceReview.cycle_id == cycle_id)
        )
        row = result.one()
        return {
            "total_reviews": row.total or 0,
            "pending": row.pending or 0,
            "self_assessment": row.self_assessment or 0,
            "manager_review": row.manager_review or 0,
            "completed": row.completed or 0,
            "average_rating": float(row.avg_rating) if row.avg_rating else None
        }
    
    async def get_reviews(
        self, db: AsyncSession, 
        cycle_id: Optional[int] = None,
        employee_id: Optional[int] = None,
        reviewer_id: Optional[int] = None,
        status: Optional[str] = None
    ) -> List[dict]:
        query = (
            select(PerformanceReview, Employee, PerformanceCycle)
            .join(Employee, PerformanceReview.employee_id == Employee.id)
            .join(PerformanceCycle, PerformanceReview.cycle_id == PerformanceCycle.id)
            .order_by(PerformanceReview.created_at.desc())
        )
        
        if cycle_id:
            query = query.where(PerformanceReview.cycle_id == cycle_id)
        if employee_id:
            query = query.where(PerformanceReview.employee_id == employee_id)
        if reviewer_id:
            query = query.where(PerformanceReview.reviewer_id == reviewer_id)
        if status:
            query = query.where(PerformanceReview.status == status)
        
        result = await db.execute(query)
        rows = result.all()
        
        reviews = []
        for review, employee, cycle in rows:
            ratings_result = await db.execute(
                select(PerformanceRating).where(PerformanceRating.review_id == review.id)
            )
            ratings = ratings_result.scalars().all()
            
            review_dict = {
                "id": review.id,
                "cycle_id": review.cycle_id,
                "employee_id": review.employee_id,
                "reviewer_id": review.reviewer_id,
                "status": review.status,
                "self_assessment_submitted": review.self_assessment_submitted,
                "self_assessment_date": review.self_assessment_date,
                "self_achievements": review.self_achievements,
                "self_challenges": review.self_challenges,
                "self_goals_next_period": review.self_goals_next_period,
                "self_training_needs": review.self_training_needs,
                "self_overall_comments": review.self_overall_comments,
                "manager_review_submitted": review.manager_review_submitted,
                "manager_review_date": review.manager_review_date,
                "manager_achievements": review.manager_achievements,
                "manager_areas_improvement": review.manager_areas_improvement,
                "manager_recommendations": review.manager_recommendations,
                "manager_overall_comments": review.manager_overall_comments,
                "overall_rating": review.overall_rating,
                "rating_label": review.rating_label,
                "created_at": review.created_at,
                "updated_at": review.updated_at,
                "employee_name": employee.name,
                "employee_department": employee.department,
                "employee_job_title": employee.job_title,
                "cycle_name": cycle.name,
                "ratings": [
                    {
                        "id": r.id,
                        "competency_name": r.competency_name,
                        "competency_category": r.competency_category,
                        "weight": r.weight,
                        "self_rating": r.self_rating,
                        "self_comments": r.self_comments,
                        "manager_rating": r.manager_rating,
                        "manager_comments": r.manager_comments
                    }
                    for r in ratings
                ]
            }
            reviews.append(review_dict)
        
        return reviews
    
    async def get_review(self, db: AsyncSession, review_id: int) -> Optional[dict]:
        result = await db.execute(
            select(PerformanceReview, Employee, PerformanceCycle)
            .join(Employee, PerformanceReview.employee_id == Employee.id)
            .join(PerformanceCycle, PerformanceReview.cycle_id == PerformanceCycle.id)
            .where(PerformanceReview.id == review_id)
        )
        row = result.one_or_none()
        if not row:
            return None
        
        review, employee, cycle = row
        
        ratings_result = await db.execute(
            select(PerformanceRating).where(PerformanceRating.review_id == review_id)
        )
        ratings = ratings_result.scalars().all()
        
        reviewer_name = None
        if review.reviewer_id:
            reviewer_result = await db.execute(
                select(Employee.name).where(Employee.id == review.reviewer_id)
            )
            reviewer_name = reviewer_result.scalar_one_or_none()
        
        return {
            "id": review.id,
            "cycle_id": review.cycle_id,
            "employee_id": review.employee_id,
            "reviewer_id": review.reviewer_id,
            "status": review.status,
            "self_assessment_submitted": review.self_assessment_submitted,
            "self_assessment_date": review.self_assessment_date,
            "self_achievements": review.self_achievements,
            "self_challenges": review.self_challenges,
            "self_goals_next_period": review.self_goals_next_period,
            "self_training_needs": review.self_training_needs,
            "self_overall_comments": review.self_overall_comments,
            "manager_review_submitted": review.manager_review_submitted,
            "manager_review_date": review.manager_review_date,
            "manager_achievements": review.manager_achievements,
            "manager_areas_improvement": review.manager_areas_improvement,
            "manager_recommendations": review.manager_recommendations,
            "manager_overall_comments": review.manager_overall_comments,
            "overall_rating": review.overall_rating,
            "rating_label": review.rating_label,
            "created_at": review.created_at,
            "updated_at": review.updated_at,
            "employee_name": employee.name,
            "employee_department": employee.department,
            "employee_job_title": employee.job_title,
            "reviewer_name": reviewer_name,
            "cycle_name": cycle.name,
            "ratings": [
                {
                    "id": r.id,
                    "competency_name": r.competency_name,
                    "competency_category": r.competency_category,
                    "weight": r.weight,
                    "self_rating": r.self_rating,
                    "self_comments": r.self_comments,
                    "manager_rating": r.manager_rating,
                    "manager_comments": r.manager_comments
                }
                for r in ratings
            ]
        }
    
    async def create_review(self, db: AsyncSession, data: PerformanceReviewCreate) -> PerformanceReview:
        review = PerformanceReview(
            cycle_id=data.cycle_id,
            employee_id=data.employee_id,
            reviewer_id=data.reviewer_id,
            status="pending"
        )
        db.add(review)
        await db.commit()
        await db.refresh(review)
        
        for comp in DEFAULT_COMPETENCIES:
            rating = PerformanceRating(
                review_id=review.id,
                competency_name=comp["name"],
                competency_category=comp["category"],
                weight=comp["weight"]
            )
            db.add(rating)
        
        await db.commit()
        return review
    
    async def create_bulk_reviews(self, db: AsyncSession, data: BulkReviewCreate) -> List[PerformanceReview]:
        reviews = []
        for emp_id in data.employee_ids:
            existing = await db.execute(
                select(PerformanceReview).where(
                    PerformanceReview.cycle_id == data.cycle_id,
                    PerformanceReview.employee_id == emp_id
                )
            )
            if existing.scalar_one_or_none():
                continue
            
            emp_result = await db.execute(
                select(Employee).where(Employee.id == emp_id)
            )
            employee = emp_result.scalar_one_or_none()
            
            review = PerformanceReview(
                cycle_id=data.cycle_id,
                employee_id=emp_id,
                reviewer_id=employee.line_manager_id if employee else None,
                status="pending"
            )
            db.add(review)
            await db.flush()
            
            for comp in DEFAULT_COMPETENCIES:
                rating = PerformanceRating(
                    review_id=review.id,
                    competency_name=comp["name"],
                    competency_category=comp["category"],
                    weight=comp["weight"]
                )
                db.add(rating)
            
            reviews.append(review)
        
        await db.commit()
        return reviews
    
    async def submit_self_assessment(
        self, db: AsyncSession, review_id: int, data: SelfAssessmentSubmit
    ) -> Optional[PerformanceReview]:
        result = await db.execute(
            select(PerformanceReview).where(PerformanceReview.id == review_id)
        )
        review = result.scalar_one_or_none()
        if not review:
            return None
        
        review.self_achievements = data.self_achievements
        review.self_challenges = data.self_challenges
        review.self_goals_next_period = data.self_goals_next_period
        review.self_training_needs = data.self_training_needs
        review.self_overall_comments = data.self_overall_comments
        review.self_assessment_submitted = True
        review.self_assessment_date = datetime.utcnow()
        review.status = "self_assessment"
        
        for rating_data in data.ratings:
            rating_result = await db.execute(
                select(PerformanceRating).where(
                    PerformanceRating.review_id == review_id,
                    PerformanceRating.competency_name == rating_data.competency_name
                )
            )
            rating = rating_result.scalar_one_or_none()
            if rating:
                rating.self_rating = rating_data.self_rating
                rating.self_comments = rating_data.self_comments
        
        await db.commit()
        await db.refresh(review)
        return review
    
    async def submit_manager_review(
        self, db: AsyncSession, review_id: int, data: ManagerReviewSubmit
    ) -> Optional[PerformanceReview]:
        result = await db.execute(
            select(PerformanceReview).where(PerformanceReview.id == review_id)
        )
        review = result.scalar_one_or_none()
        if not review:
            return None
        
        review.manager_achievements = data.manager_achievements
        review.manager_areas_improvement = data.manager_areas_improvement
        review.manager_recommendations = data.manager_recommendations
        review.manager_overall_comments = data.manager_overall_comments
        review.overall_rating = data.overall_rating
        review.rating_label = data.rating_label or (RATING_LABELS.get(int(data.overall_rating)) if data.overall_rating else None)
        review.manager_review_submitted = True
        review.manager_review_date = datetime.utcnow()
        review.status = "completed"
        
        for rating_data in data.ratings:
            rating_result = await db.execute(
                select(PerformanceRating).where(
                    PerformanceRating.review_id == review_id,
                    PerformanceRating.competency_name == rating_data.competency_name
                )
            )
            rating = rating_result.scalar_one_or_none()
            if rating:
                rating.manager_rating = rating_data.manager_rating
                rating.manager_comments = rating_data.manager_comments
        
        await db.commit()
        await db.refresh(review)
        return review
    
    async def get_employee_reviews(self, db: AsyncSession, employee_id: int) -> List[dict]:
        return await self.get_reviews(db, employee_id=employee_id)
    
    async def get_manager_reviews(self, db: AsyncSession, manager_id: int) -> List[dict]:
        return await self.get_reviews(db, reviewer_id=manager_id)

    async def submit_review(self, db: AsyncSession, review_id: int) -> Optional[PerformanceReview]:
        """
        Submit a review (mark as submitted, ready for manager approval).
        Transitions from self_assessment to manager_review status.
        """
        review = await self.get_review(db, review_id)
        if not review:
            return None
        
        if not review.self_assessment_submitted:
            raise ValueError("Self-assessment must be completed before submission")
        
        review.status = "manager_review"
        await db.commit()
        await db.refresh(review)
        return review

    async def approve_review(
        self, db: AsyncSession, review_id: int, approved_by: int
    ) -> Optional[PerformanceReview]:
        """
        Manager approves the review (final approval).
        Transitions to completed status and calculates final rating.
        """
        review = await self.get_review(db, review_id)
        if not review:
            return None
        
        if not review.manager_review_submitted:
            raise ValueError("Manager review must be completed before approval")
        
        # Calculate final rating from criteria
        final_rating = await self.calculate_final_rating(db, review_id)
        
        review.status = "completed"
        review.overall_rating = Decimal(str(final_rating))
        review.rating_label = RATING_LABELS.get(round(final_rating), "Meets Expectations")
        
        await db.commit()
        await db.refresh(review)
        return review

    async def calculate_final_rating(self, db: AsyncSession, review_id: int) -> float:
        """
        Calculate weighted average rating across all criteria.
        Returns final rating as float (1-5 scale).
        """
        result = await db.execute(
            select(PerformanceRating)
            .where(PerformanceRating.review_id == review_id)
        )
        ratings = result.scalars().all()
        
        if not ratings:
            return 3.0  # Default to "Meets Expectations" if no ratings
        
        # Calculate weighted average
        total_weight = sum(r.weight for r in ratings if r.manager_rating is not None)
        if total_weight == 0:
            # Fallback to simple average if no weights
            valid_ratings = [r.manager_rating for r in ratings if r.manager_rating is not None]
            return sum(valid_ratings) / len(valid_ratings) if valid_ratings else 3.0
        
        weighted_sum = sum(
            r.manager_rating * r.weight 
            for r in ratings 
            if r.manager_rating is not None
        )
        
        return round(weighted_sum / total_weight, 2)

    async def get_final_rating(self, db: AsyncSession, review_id: int) -> dict:
        """
        Get the final rating for a review with breakdown.
        """
        review = await self.get_review(db, review_id)
        if not review:
            return {"error": "Review not found"}
        
        result = await db.execute(
            select(PerformanceRating)
            .where(PerformanceRating.review_id == review_id)
        )
        ratings = result.scalars().all()
        
        breakdown = []
        for rating in ratings:
            breakdown.append({
                "competency": rating.competency_name,
                "category": rating.competency_category,
                "weight": rating.weight,
                "self_rating": rating.self_rating,
                "manager_rating": rating.manager_rating,
                "weighted_score": (rating.manager_rating or 0) * rating.weight / 100 if rating.manager_rating else 0
            })
        
        final_rating = await self.calculate_final_rating(db, review_id)
        
        return {
            "review_id": review_id,
            "final_rating": final_rating,
            "rating_label": RATING_LABELS.get(round(final_rating), "Meets Expectations"),
            "breakdown": breakdown,
            "status": review.status
        }

    async def get_cycle_summary(self, db: AsyncSession, cycle_id: int) -> dict:
        """
        Get summary report for a performance cycle (completed vs pending).
        """
        stats = await self.get_cycle_stats(db, cycle_id)
        cycle = await self.get_cycle(db, cycle_id)
        
        if not cycle:
            return {"error": "Cycle not found"}
        
        # Get employee details for completed reviews
        result = await db.execute(
            select(PerformanceReview, Employee)
            .join(Employee, PerformanceReview.employee_id == Employee.id)
            .where(
                PerformanceReview.cycle_id == cycle_id,
                PerformanceReview.status == "completed"
            )
        )
        completed_reviews = []
        for review, employee in result.fetchall():
            completed_reviews.append({
                "employee_id": employee.employee_id,
                "employee_name": employee.name,
                "department": employee.department,
                "final_rating": float(review.overall_rating) if review.overall_rating else None,
                "rating_label": review.rating_label,
                "completed_at": review.manager_review_date
            })
        
        # Get pending reviews
        result = await db.execute(
            select(PerformanceReview, Employee)
            .join(Employee, PerformanceReview.employee_id == Employee.id)
            .where(
                PerformanceReview.cycle_id == cycle_id,
                PerformanceReview.status != "completed"
            )
        )
        pending_reviews = []
        for review, employee in result.fetchall():
            pending_reviews.append({
                "employee_id": employee.employee_id,
                "employee_name": employee.name,
                "department": employee.department,
                "status": review.status,
                "self_assessment_submitted": review.self_assessment_submitted,
                "manager_review_submitted": review.manager_review_submitted
            })
        
        return {
            "cycle_id": cycle_id,
            "cycle_name": cycle.name,
            "cycle_status": cycle.status,
            "stats": stats,
            "completed_reviews": completed_reviews,
            "pending_reviews": pending_reviews
        }

    async def get_employee_history(self, db: AsyncSession, employee_id: int) -> List[dict]:
        """
        Get performance review history for an employee.
        """
        result = await db.execute(
            select(PerformanceReview, PerformanceCycle)
            .join(PerformanceCycle, PerformanceReview.cycle_id == PerformanceCycle.id)
            .where(PerformanceReview.employee_id == employee_id)
            .order_by(PerformanceCycle.start_date.desc())
        )
        
        history = []
        for review, cycle in result.fetchall():
            history.append({
                "cycle_id": cycle.id,
                "cycle_name": cycle.name,
                "cycle_type": cycle.cycle_type,
                "review_id": review.id,
                "status": review.status,
                "final_rating": float(review.overall_rating) if review.overall_rating else None,
                "rating_label": review.rating_label,
                "self_assessment_date": review.self_assessment_date,
                "manager_review_date": review.manager_review_date,
                "start_date": cycle.start_date,
                "end_date": cycle.end_date
            })
        
        return history


from sqlalchemy import Integer
performance_service = PerformanceService()
