"""Business logic for recruitment operations."""
import logging
import uuid
from datetime import datetime, date, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy import select, and_, func
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.recruitment import (
    RecruitmentRequest, Candidate, Interview, Evaluation,
    RECRUITMENT_STAGES, INTERVIEW_TYPES, EMPLOYMENT_TYPES
)
from app.models.passes import Pass
from app.schemas.recruitment import (
    RecruitmentRequestCreate, RecruitmentRequestUpdate,
    CandidateCreate, CandidateUpdate,
    InterviewCreate, InterviewUpdate,
    EvaluationCreate, EvaluationUpdate,
    InterviewSlotsProvide, InterviewSlotConfirm
)

logger = logging.getLogger(__name__)

# Constants for slot booking status
SLOT_BOOKED_BY_OTHER = "__SLOT_UNAVAILABLE__"  # Marks slot as taken by another candidate

class RecruitmentService:
    """Service for recruitment operations."""

    # =========================================================================
    # RECRUITMENT REQUESTS
    # =========================================================================

    async def create_request(
        self,
        session: AsyncSession,
        data: RecruitmentRequestCreate,
        created_by: str
    ) -> RecruitmentRequest:
        """Create a new recruitment request."""
        # Generate request number
        request_number = await self._generate_request_number(session)

        # Create request
        request = RecruitmentRequest(
            request_number=request_number,
            requested_by=created_by,
            request_date=date.today(),
            status="pending",
            approval_status={
                'requisition': {'status': 'pending', 'approver': None, 'date': None},
                'budget': {'status': 'pending', 'approver': None, 'date': None},
                'offer': {'status': 'pending', 'approver': None, 'date': None}
            },
            **data.model_dump()
        )

        session.add(request)
        await session.commit()
        await session.refresh(request)

        # Create manager pass if hiring manager specified
        if request.hiring_manager_id:
            manager_pass = await self._create_manager_pass(session, request, created_by)
            request.manager_pass_number = manager_pass.pass_number
            await session.commit()
            await session.refresh(request)

        return request

    async def get_request(
        self,
        session: AsyncSession,
        request_id: int
    ) -> Optional[RecruitmentRequest]:
        """Get a recruitment request by ID."""
        result = await session.execute(
            select(RecruitmentRequest).where(RecruitmentRequest.id == request_id)
        )
        return result.scalar_one_or_none()

    async def get_request_by_number(
        self,
        session: AsyncSession,
        request_number: str
    ) -> Optional[RecruitmentRequest]:
        """Get a recruitment request by request number."""
        result = await session.execute(
            select(RecruitmentRequest).where(RecruitmentRequest.request_number == request_number)
        )
        return result.scalar_one_or_none()

    async def list_requests(
        self,
        session: AsyncSession,
        status: Optional[str] = None,
        department: Optional[str] = None
    ) -> List[RecruitmentRequest]:
        """List recruitment requests with optional filters."""
        query = select(RecruitmentRequest)

        filters = []
        if status:
            filters.append(RecruitmentRequest.status == status)
        if department:
            filters.append(RecruitmentRequest.department == department)

        if filters:
            query = query.where(and_(*filters))

        query = query.order_by(RecruitmentRequest.created_at.desc())

        result = await session.execute(query)
        return list(result.scalars().all())

    async def update_request(
        self,
        session: AsyncSession,
        request_id: int,
        data: RecruitmentRequestUpdate
    ) -> Optional[RecruitmentRequest]:
        """Update a recruitment request."""
        request = await self.get_request(session, request_id)
        if not request:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(request, key, value)

        await session.commit()
        await session.refresh(request)
        return request

    async def approve_request(
        self,
        session: AsyncSession,
        request_id: int,
        approval_type: str,
        approver_id: str
    ) -> Optional[RecruitmentRequest]:
        """Approve a recruitment request (requisition, budget, or offer)."""
        request = await self.get_request(session, request_id)
        if not request:
            return None

        if approval_type not in ['requisition', 'budget', 'offer']:
            raise ValueError(f"Invalid approval type: {approval_type}")

        # Update approval status
        approval_status = request.approval_status or {}
        approval_status[approval_type] = {
            'status': 'approved',
            'approver': approver_id,
            'date': datetime.now().isoformat()
        }
        request.approval_status = approval_status

        # If requisition and budget approved, move to approved status
        if (approval_status.get('requisition', {}).get('status') == 'approved' and
            approval_status.get('budget', {}).get('status') == 'approved'):
            request.status = 'approved'

        await session.commit()
        await session.refresh(request)
        return request

    # =========================================================================
    # CANDIDATES
    # =========================================================================

    async def add_candidate(
        self,
        session: AsyncSession,
        data: CandidateCreate,
        created_by: str
    ) -> Candidate:
        """Add a new candidate to the pipeline."""
        import secrets
        
        # Generate candidate number
        candidate_number = await self._generate_candidate_number(session)
        
        # Generate secure pass token for self-service verification
        pass_token = secrets.token_hex(32)

        # Create candidate
        candidate = Candidate(
            candidate_number=candidate_number,
            stage='applied',
            status='applied',
            stage_changed_at=datetime.now(),
            pass_token=pass_token,
            **data.model_dump()
        )

        session.add(candidate)
        await session.commit()
        await session.refresh(candidate)

        # Create candidate pass
        candidate_pass = await self._create_candidate_pass(session, candidate, created_by)
        candidate.pass_number = candidate_pass.pass_number
        await session.commit()
        await session.refresh(candidate)

        return candidate

    async def get_candidate(
        self,
        session: AsyncSession,
        candidate_id: int
    ) -> Optional[Candidate]:
        """Get a candidate by ID."""
        result = await session.execute(
            select(Candidate).where(Candidate.id == candidate_id)
        )
        return result.scalar_one_or_none()

    async def get_candidate_by_number(
        self,
        session: AsyncSession,
        candidate_number: str
    ) -> Optional[Candidate]:
        """Get a candidate by candidate number."""
        result = await session.execute(
            select(Candidate).where(Candidate.candidate_number == candidate_number)
        )
        return result.scalar_one_or_none()

    async def list_candidates(
        self,
        session: AsyncSession,
        recruitment_request_id: Optional[int] = None,
        stage: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[Candidate]:
        """List candidates with optional filters."""
        query = select(Candidate)

        filters = []
        if recruitment_request_id:
            filters.append(Candidate.recruitment_request_id == recruitment_request_id)
        if stage:
            filters.append(Candidate.stage == stage)
        if status:
            filters.append(Candidate.status == status)

        if filters:
            query = query.where(and_(*filters))

        query = query.order_by(Candidate.created_at.desc())

        result = await session.execute(query)
        return list(result.scalars().all())

    async def update_candidate(
        self,
        session: AsyncSession,
        candidate_id: int,
        data: CandidateUpdate
    ) -> Optional[Candidate]:
        """Update a candidate."""
        candidate = await self.get_candidate(session, candidate_id)
        if not candidate:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(candidate, key, value)

        await session.commit()
        await session.refresh(candidate)
        return candidate

    async def move_candidate_stage(
        self,
        session: AsyncSession,
        candidate_id: int,
        new_stage: str
    ) -> Candidate:
        """Move candidate to a new stage in the pipeline."""
        candidate = await self.get_candidate(session, candidate_id)
        if not candidate:
            raise ValueError("Candidate not found")

        # Validate stage
        valid_stages = [s['key'] for s in RECRUITMENT_STAGES]
        if new_stage not in valid_stages:
            raise ValueError(f"Invalid stage: {new_stage}")

        # Update stage
        candidate.stage = new_stage
        candidate.stage_changed_at = datetime.now()

        # Update status based on stage
        stage_status_map = {
            'applied': 'applied',
            'screening': 'screening',
            'interview': 'interview',
            'offer': 'offer',
            'hired': 'hired',
            'rejected': 'rejected'
        }
        candidate.status = stage_status_map.get(new_stage, candidate.status)

        await session.commit()
        await session.refresh(candidate)

        return candidate

    async def reject_candidate(
        self,
        session: AsyncSession,
        candidate_id: int,
        reason: str
    ) -> Candidate:
        """Reject a candidate."""
        candidate = await self.get_candidate(session, candidate_id)
        if not candidate:
            raise ValueError("Candidate not found")

        candidate.stage = 'rejected'
        candidate.status = 'rejected'
        candidate.rejection_reason = reason
        candidate.stage_changed_at = datetime.now()

        await session.commit()
        await session.refresh(candidate)

        return candidate

    async def get_pipeline_counts(
        self,
        session: AsyncSession,
        recruitment_request_id: Optional[int] = None
    ) -> Dict[str, int]:
        """Get count of candidates by stage."""
        query = select(Candidate.stage, func.count(Candidate.id))

        if recruitment_request_id:
            query = query.where(Candidate.recruitment_request_id == recruitment_request_id)

        query = query.group_by(Candidate.stage)

        result = await session.execute(query)
        counts = {row[0]: row[1] for row in result.all()}

        # Ensure all stages are present
        for stage in RECRUITMENT_STAGES:
            if stage['key'] not in counts:
                counts[stage['key']] = 0

        return counts

    # =========================================================================
    # INTERVIEWS
    # =========================================================================

    async def create_interview(
        self,
        session: AsyncSession,
        data: InterviewCreate
    ) -> Interview:
        """Create a new interview."""
        # Generate interview number
        interview_number = await self._generate_interview_number(session)

        interview = Interview(
            interview_number=interview_number,
            status='pending',
            **data.model_dump()
        )

        session.add(interview)
        await session.commit()
        await session.refresh(interview)

        return interview

    async def get_interview(
        self,
        session: AsyncSession,
        interview_id: int
    ) -> Optional[Interview]:
        """Get an interview by ID."""
        result = await session.execute(
            select(Interview).where(Interview.id == interview_id)
        )
        return result.scalar_one_or_none()

    async def list_interviews(
        self,
        session: AsyncSession,
        candidate_id: Optional[int] = None,
        recruitment_request_id: Optional[int] = None,
        status: Optional[str] = None
    ) -> List[Interview]:
        """List interviews with optional filters."""
        query = select(Interview)

        filters = []
        if candidate_id:
            filters.append(Interview.candidate_id == candidate_id)
        if recruitment_request_id:
            filters.append(Interview.recruitment_request_id == recruitment_request_id)
        if status:
            filters.append(Interview.status == status)

        if filters:
            query = query.where(and_(*filters))

        query = query.order_by(Interview.created_at.desc())

        result = await session.execute(query)
        return list(result.scalars().all())

    async def provide_interview_slots(
        self,
        session: AsyncSession,
        interview_id: int,
        slots: InterviewSlotsProvide
    ) -> Interview:
        """
        Provide available interview slots (by hiring manager).
        
        Once slots are provided, the interview status changes to 'slots_provided'
        and the candidate can select from these slots via their pass.
        """
        interview = await self.get_interview(session, interview_id)
        if not interview:
            raise ValueError("Interview not found")

        # Convert slots to JSON-serializable format with booking status
        slots_data = [
            {
                "id": f"slot-{i}",
                "start": slot.start.isoformat(),
                "end": slot.end.isoformat(),
                "is_booked": False,
                "booked_by": None
            }
            for i, slot in enumerate(slots.available_slots)
        ]

        interview.available_slots = {"slots": slots_data}
        interview.status = 'slots_provided'

        # Update candidate status to indicate slots are available
        if interview.candidate_id:
            candidate = await self.get_candidate(session, interview.candidate_id)
            if candidate:
                candidate.status = 'slots_available'
                candidate.last_activity_at = datetime.now()

        await session.commit()
        await session.refresh(interview)

        return interview

    async def confirm_interview_slot(
        self,
        session: AsyncSession,
        interview_id: int,
        confirmation: InterviewSlotConfirm,
        candidate_id: Optional[int] = None
    ) -> Interview:
        """
        Confirm an interview slot (by candidate).
        
        Once a slot is confirmed:
        1. The slot is marked as booked by this candidate
        2. The interview status changes to 'scheduled'
        3. The candidate status is updated
        4. The slot becomes unavailable to other candidates for the same recruitment request
        """
        interview = await self.get_interview(session, interview_id)
        if not interview:
            raise ValueError("Interview not found")
        
        # Validate the interview has available slots
        if not interview.available_slots or 'slots' not in interview.available_slots:
            raise ValueError("No available slots for this interview")
        
        # Find and validate the selected slot
        selected_start = confirmation.selected_slot.start.isoformat()
        selected_end = confirmation.selected_slot.end.isoformat()
        candidate_id_str = str(interview.candidate_id)
        
        slot_found = False
        for slot in interview.available_slots['slots']:
            if slot['start'] == selected_start and slot['end'] == selected_end:
                # Check if booked by another candidate (compare as strings)
                if slot.get('is_booked') and slot.get('booked_by') != candidate_id_str:
                    raise ValueError("This slot has already been booked by another candidate")
                slot_found = True
                # Mark this slot as booked
                slot['is_booked'] = True
                slot['booked_by'] = candidate_id_str
                break
        
        if not slot_found:
            raise ValueError("Selected slot is not available")

        interview.scheduled_date = confirmation.selected_slot.start
        interview.status = 'scheduled'
        interview.confirmed_by_candidate = True
        interview.confirmed_at = datetime.now()

        # Update candidate status
        if interview.candidate_id:
            candidate = await self.get_candidate(session, interview.candidate_id)
            if candidate:
                candidate.status = 'scheduled'
                candidate.last_activity_at = datetime.now()
        
        # Mark this slot as unavailable in other interviews for the same recruitment request
        # This prevents double-booking of manager's time
        await self._mark_slot_unavailable_for_request(
            session,
            interview.recruitment_request_id,
            selected_start,
            selected_end,
            interview.id
        )

        await session.commit()
        await session.refresh(interview)

        return interview
    
    async def _mark_slot_unavailable_for_request(
        self,
        session: AsyncSession,
        recruitment_request_id: int,
        slot_start: str,
        slot_end: str,
        exclude_interview_id: int
    ) -> None:
        """
        Mark a time slot as unavailable in all other interviews for the same recruitment request.
        
        This ensures that once a candidate books a slot, no other candidate can book
        the same time slot for the same position.
        """
        # Get all interviews for this recruitment request
        result = await session.execute(
            select(Interview).where(
                and_(
                    Interview.recruitment_request_id == recruitment_request_id,
                    Interview.id != exclude_interview_id,
                    Interview.status.in_(['pending', 'slots_provided'])
                )
            )
        )
        interviews = result.scalars().all()
        
        for interview in interviews:
            if interview.available_slots and 'slots' in interview.available_slots:
                for slot in interview.available_slots['slots']:
                    if slot['start'] == slot_start and slot['end'] == slot_end:
                        slot['is_booked'] = True
                        slot['booked_by'] = SLOT_BOOKED_BY_OTHER
                        break

    async def complete_interview(
        self,
        session: AsyncSession,
        interview_id: int,
        notes: Optional[str] = None
    ) -> Interview:
        """Mark an interview as completed."""
        interview = await self.get_interview(session, interview_id)
        if not interview:
            raise ValueError("Interview not found")

        interview.status = 'completed'
        interview.completed_at = datetime.now()
        if notes:
            interview.notes = notes

        await session.commit()
        await session.refresh(interview)

        return interview

    # =========================================================================
    # EVALUATIONS
    # =========================================================================

    async def create_evaluation(
        self,
        session: AsyncSession,
        data: EvaluationCreate,
        evaluator_id: str
    ) -> Evaluation:
        """Create a new evaluation."""
        # Generate evaluation number
        evaluation_number = await self._generate_evaluation_number(session)

        evaluation = Evaluation(
            evaluation_number=evaluation_number,
            evaluator_id=evaluator_id,
            **data.model_dump()
        )

        session.add(evaluation)
        await session.commit()
        await session.refresh(evaluation)

        return evaluation

    async def get_evaluation(
        self,
        session: AsyncSession,
        evaluation_id: int
    ) -> Optional[Evaluation]:
        """Get an evaluation by ID."""
        result = await session.execute(
            select(Evaluation).where(Evaluation.id == evaluation_id)
        )
        return result.scalar_one_or_none()

    async def list_evaluations(
        self,
        session: AsyncSession,
        candidate_id: Optional[int] = None,
        interview_id: Optional[int] = None
    ) -> List[Evaluation]:
        """List evaluations with optional filters."""
        query = select(Evaluation)

        filters = []
        if candidate_id:
            filters.append(Evaluation.candidate_id == candidate_id)
        if interview_id:
            filters.append(Evaluation.interview_id == interview_id)

        if filters:
            query = query.where(and_(*filters))

        query = query.order_by(Evaluation.created_at.desc())

        result = await session.execute(query)
        return list(result.scalars().all())

    # =========================================================================
    # STATISTICS
    # =========================================================================

    async def get_stats(self, session: AsyncSession) -> Dict[str, Any]:
        """Get recruitment statistics."""
        # Count requests
        total_requests = await session.execute(
            select(func.count(RecruitmentRequest.id))
        )
        active_requests = await session.execute(
            select(func.count(RecruitmentRequest.id)).where(
                RecruitmentRequest.status.in_(['pending', 'approved'])
            )
        )

        # Count candidates
        total_candidates = await session.execute(
            select(func.count(Candidate.id))
        )

        # Get pipeline counts
        pipeline_counts = await self.get_pipeline_counts(session)

        # Count by source
        source_result = await session.execute(
            select(Candidate.source, func.count(Candidate.id))
            .where(Candidate.source.isnot(None))
            .group_by(Candidate.source)
        )
        by_source = {row[0]: row[1] for row in source_result.all()}

        # Recent hires (last 30 days)
        thirty_days_ago = datetime.now() - timedelta(days=30)
        recent_hires = await session.execute(
            select(func.count(Candidate.id)).where(
                and_(
                    Candidate.stage == 'hired',
                    Candidate.stage_changed_at >= thirty_days_ago
                )
            )
        )

        return {
            "total_requests": total_requests.scalar() or 0,
            "active_requests": active_requests.scalar() or 0,
            "total_candidates": total_candidates.scalar() or 0,
            "by_stage": pipeline_counts,
            "by_source": by_source,
            "recent_hires": recent_hires.scalar() or 0
        }

    # =========================================================================
    # HELPER METHODS
    # =========================================================================

    async def _generate_request_number(self, session: AsyncSession) -> str:
        """
        Generate unique request number: RRF-YYYYMMDD-XXXX.
        Uses retry logic with max attempts to handle race conditions.
        Falls back to UUID suffix if unable to generate sequential number.
        """
        today = date.today().strftime('%Y%m%d')
        max_attempts = 5
        
        for attempt in range(max_attempts):
            try:
                # Get max sequence number for today using MAX instead of COUNT
                # This is more race-condition resistant
                result = await session.execute(
                    select(func.max(RecruitmentRequest.request_number)).where(
                        RecruitmentRequest.request_number.like(f'RRF-{today}-%')
                    )
                )
                max_number = result.scalar()
                
                if max_number:
                    # Extract sequence number from last requisition
                    try:
                        last_seq = int(max_number.split('-')[-1])
                        next_seq = last_seq + 1
                    except (ValueError, IndexError):
                        next_seq = 1
                else:
                    next_seq = 1
                
                # Try this number - if it fails due to unique constraint, retry
                return f"RRF-{today}-{next_seq:04d}"
                
            except IntegrityError:
                # Race condition detected - another request got this number
                # Retry with next iteration
                await session.rollback()
                continue
        
        # Fallback: Use UUID suffix to guarantee uniqueness
        unique_suffix = str(uuid.uuid4())[:8].upper()
        logging.warning(f"Failed to generate sequential request number after {max_attempts} attempts. Using UUID fallback.")
        return f"RRF-{today}-{unique_suffix}"

    async def _generate_candidate_number(self, session: AsyncSession) -> str:
        """
        Generate unique candidate number: CAN-YYYYMMDD-XXXX.
        Uses retry logic with max attempts to handle race conditions.
        Falls back to UUID suffix if unable to generate sequential number.
        """
        today = date.today().strftime('%Y%m%d')
        max_attempts = 5
        
        for attempt in range(max_attempts):
            try:
                # Get max sequence number for today
                result = await session.execute(
                    select(func.max(Candidate.candidate_number)).where(
                        Candidate.candidate_number.like(f'CAN-{today}-%')
                    )
                )
                max_number = result.scalar()
                
                if max_number:
                    try:
                        last_seq = int(max_number.split('-')[-1])
                        next_seq = last_seq + 1
                    except (ValueError, IndexError):
                        next_seq = 1
                else:
                    next_seq = 1
                
                return f"CAN-{today}-{next_seq:04d}"
                
            except IntegrityError:
                await session.rollback()
                continue
        
        # Fallback: Use UUID suffix
        unique_suffix = str(uuid.uuid4())[:8].upper()
        logging.warning(f"Failed to generate sequential candidate number after {max_attempts} attempts. Using UUID fallback.")
        return f"CAN-{today}-{unique_suffix}"

    async def _generate_interview_number(self, session: AsyncSession) -> str:
        """
        Generate unique interview number: INT-YYYYMMDD-XXXX.
        Uses retry logic with max attempts to handle race conditions.
        Falls back to UUID suffix if unable to generate sequential number.
        """
        today = date.today().strftime('%Y%m%d')
        max_attempts = 5
        
        for attempt in range(max_attempts):
            try:
                result = await session.execute(
                    select(func.max(Interview.interview_number)).where(
                        Interview.interview_number.like(f'INT-{today}-%')
                    )
                )
                max_number = result.scalar()
                
                if max_number:
                    try:
                        last_seq = int(max_number.split('-')[-1])
                        next_seq = last_seq + 1
                    except (ValueError, IndexError):
                        next_seq = 1
                else:
                    next_seq = 1
                
                return f"INT-{today}-{next_seq:04d}"
                
            except IntegrityError:
                await session.rollback()
                continue
        
        # Fallback: Use UUID suffix
        unique_suffix = str(uuid.uuid4())[:8].upper()
        logging.warning(f"Failed to generate sequential interview number after {max_attempts} attempts. Using UUID fallback.")
        return f"INT-{today}-{unique_suffix}"

    async def _generate_evaluation_number(self, session: AsyncSession) -> str:
        """
        Generate unique evaluation number: EVL-YYYYMMDD-XXXX.
        Uses retry logic with max attempts to handle race conditions.
        Falls back to UUID suffix if unable to generate sequential number.
        """
        today = date.today().strftime('%Y%m%d')
        max_attempts = 5
        
        for attempt in range(max_attempts):
            try:
                result = await session.execute(
                    select(func.max(Evaluation.evaluation_number)).where(
                        Evaluation.evaluation_number.like(f'EVL-{today}-%')
                    )
                )
                max_number = result.scalar()
                
                if max_number:
                    try:
                        last_seq = int(max_number.split('-')[-1])
                        next_seq = last_seq + 1
                    except (ValueError, IndexError):
                        next_seq = 1
                else:
                    next_seq = 1
                
                return f"EVL-{today}-{next_seq:04d}"
                
            except IntegrityError:
                await session.rollback()
                continue
        
        # Fallback: Use UUID suffix
        unique_suffix = str(uuid.uuid4())[:8].upper()
        logging.warning(f"Failed to generate sequential evaluation number after {max_attempts} attempts. Using UUID fallback.")
        return f"EVL-{today}-{unique_suffix}"

    async def _create_manager_pass(
        self,
        session: AsyncSession,
        request: RecruitmentRequest,
        created_by: str
    ) -> Pass:
        """
        Create manager pass for hiring manager.
        Uses MAX-based approach with retry logic to avoid race conditions.
        """
        today = date.today().strftime('%Y%m%d')
        max_attempts = 5
        
        for attempt in range(max_attempts):
            try:
                # Get max sequence number for today
                result = await session.execute(
                    select(func.max(Pass.pass_number)).where(
                        Pass.pass_number.like(f'MGR-{today}-%')
                    )
                )
                max_number = result.scalar()
                
                if max_number:
                    try:
                        last_seq = int(max_number.split('-')[-1])
                        next_seq = last_seq + 1
                    except (ValueError, IndexError):
                        next_seq = 1
                else:
                    next_seq = 1
                
                pass_number = f"MGR-{today}-{next_seq:04d}"
                break  # Exit loop if successful
                
            except IntegrityError:
                await session.rollback()
                if attempt == max_attempts - 1:
                    # Fallback: Use UUID suffix
                    unique_suffix = str(uuid.uuid4())[:8].upper()
                    logging.warning(f"Failed to generate sequential manager pass number after {max_attempts} attempts. Using UUID fallback.")
                    pass_number = f"MGR-{today}-{unique_suffix}"
                continue

        # Create pass
        manager_pass = Pass(
            pass_number=pass_number,
            pass_type='recruitment',  # Using existing pass type
            full_name=request.hiring_manager_id or "Hiring Manager",
            department=request.department,
            position=request.position_title,
            valid_from=date.today(),
            valid_until=date.today() + timedelta(days=90),  # 3 months
            purpose=f"Recruitment: {request.position_title} (Request: {request.request_number})",
            status='active',
            created_by=created_by
        )

        session.add(manager_pass)
        await session.commit()
        await session.refresh(manager_pass)

        return manager_pass

    async def _create_candidate_pass(
        self,
        session: AsyncSession,
        candidate: Candidate,
        created_by: str
    ) -> Pass:
        """
        Create recruitment pass for candidate.
        Uses MAX-based approach with retry logic to avoid race conditions.
        """
        today = date.today().strftime('%Y%m%d')
        max_attempts = 5
        
        for attempt in range(max_attempts):
            try:
                # Get max sequence number for today
                result = await session.execute(
                    select(func.max(Pass.pass_number)).where(
                        Pass.pass_number.like(f'REC-{today}-%')
                    )
                )
                max_number = result.scalar()
                
                if max_number:
                    try:
                        last_seq = int(max_number.split('-')[-1])
                        next_seq = last_seq + 1
                    except (ValueError, IndexError):
                        next_seq = 1
                else:
                    next_seq = 1
                
                pass_number = f"REC-{today}-{next_seq:04d}"
                break  # Exit loop if successful
                
            except IntegrityError:
                await session.rollback()
                if attempt == max_attempts - 1:
                    # Fallback: Use UUID suffix
                    unique_suffix = str(uuid.uuid4())[:8].upper()
                    logging.warning(f"Failed to generate sequential candidate pass number after {max_attempts} attempts. Using UUID fallback.")
                    pass_number = f"REC-{today}-{unique_suffix}"
                continue

        # Create pass
        candidate_pass = Pass(
            pass_number=pass_number,
            pass_type='recruitment',
            full_name=candidate.full_name,
            email=candidate.email,
            phone=candidate.phone,
            position=candidate.current_position,
            valid_from=date.today(),
            valid_until=date.today() + timedelta(days=60),  # 2 months
            purpose=f"Candidate application (Ref: {candidate.candidate_number})",
            status='active',
            created_by=created_by
        )

        session.add(candidate_pass)
        await session.commit()
        await session.refresh(candidate_pass)

        return candidate_pass

    def get_stages(self) -> List[Dict[str, Any]]:
        """Get list of recruitment stages."""
        return RECRUITMENT_STAGES

    def get_interview_types(self) -> List[Dict[str, str]]:
        """Get list of interview types."""
        return INTERVIEW_TYPES

    def get_employment_types(self) -> List[Dict[str, str]]:
        """Get list of employment types."""
        return EMPLOYMENT_TYPES

    # =========================================================================
    # BULK OPERATIONS
    # =========================================================================

    async def bulk_update_stage(
        self,
        session: AsyncSession,
        candidate_ids: List[int],
        new_stage: str,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """Bulk update candidate stages for efficiency."""
        # Validate stage
        valid_stages = [s['key'] for s in RECRUITMENT_STAGES]
        if new_stage not in valid_stages:
            raise ValueError(f"Invalid stage: {new_stage}")

        success_count = 0
        failed_ids = []

        for candidate_id in candidate_ids:
            try:
                candidate = await self.get_candidate(session, candidate_id)
                if candidate:
                    candidate.stage = new_stage
                    candidate.stage_changed_at = datetime.now()
                    # Update status based on stage
                    stage_status_map = {
                        'applied': 'applied',
                        'screening': 'screening',
                        'interview': 'interview',
                        'offer': 'offer',
                        'hired': 'hired',
                        'rejected': 'rejected'
                    }
                    candidate.status = stage_status_map.get(new_stage, candidate.status)
                    if notes:
                        existing_notes = candidate.recruiter_notes or ""
                        candidate.recruiter_notes = f"{existing_notes}\n[{datetime.now().strftime('%Y-%m-%d')}] Stage changed to {new_stage}: {notes}".strip()
                    success_count += 1
                else:
                    failed_ids.append(candidate_id)
            except SQLAlchemyError as e:
                logger.warning(f"Database error updating candidate {candidate_id}: {e}")
                failed_ids.append(candidate_id)

        await session.commit()

        return {
            "success_count": success_count,
            "failed_count": len(failed_ids),
            "failed_ids": failed_ids,
            "message": f"Successfully updated {success_count} candidates to stage '{new_stage}'"
        }

    async def bulk_reject_candidates(
        self,
        session: AsyncSession,
        candidate_ids: List[int],
        rejection_reason: str
    ) -> Dict[str, Any]:
        """Bulk reject candidates for efficiency."""
        success_count = 0
        failed_ids = []

        for candidate_id in candidate_ids:
            try:
                candidate = await self.get_candidate(session, candidate_id)
                if candidate and candidate.stage != 'hired':
                    candidate.stage = 'rejected'
                    candidate.status = 'rejected'
                    candidate.rejection_reason = rejection_reason
                    candidate.stage_changed_at = datetime.now()
                    success_count += 1
                else:
                    failed_ids.append(candidate_id)
            except SQLAlchemyError as e:
                logger.warning(f"Database error rejecting candidate {candidate_id}: {e}")
                failed_ids.append(candidate_id)

        await session.commit()

        return {
            "success_count": success_count,
            "failed_count": len(failed_ids),
            "failed_ids": failed_ids,
            "message": f"Successfully rejected {success_count} candidates"
        }

    # =========================================================================
    # ENHANCED ANALYTICS
    # =========================================================================

    async def get_recruitment_metrics(self, session: AsyncSession) -> Dict[str, Any]:
        """Get detailed recruitment metrics for dashboard and analytics."""
        thirty_days_ago = datetime.now() - timedelta(days=30)

        # Request counts
        total_requests = await session.execute(
            select(func.count(RecruitmentRequest.id))
        )
        active_requests = await session.execute(
            select(func.count(RecruitmentRequest.id)).where(
                RecruitmentRequest.status.in_(['pending', 'approved'])
            )
        )
        filled_requests = await session.execute(
            select(func.count(RecruitmentRequest.id)).where(
                RecruitmentRequest.status == 'filled'
            )
        )
        cancelled_requests = await session.execute(
            select(func.count(RecruitmentRequest.id)).where(
                RecruitmentRequest.status == 'cancelled'
            )
        )

        # Total candidates
        total_candidates = await session.execute(
            select(func.count(Candidate.id))
        )

        # Pipeline counts
        pipeline_counts = await self.get_pipeline_counts(session)

        # By source
        source_result = await session.execute(
            select(Candidate.source, func.count(Candidate.id))
            .where(Candidate.source.isnot(None))
            .group_by(Candidate.source)
        )
        by_source = {row[0]: row[1] for row in source_result.all()}

        # By status
        status_result = await session.execute(
            select(Candidate.status, func.count(Candidate.id))
            .group_by(Candidate.status)
        )
        by_status = {row[0]: row[1] for row in status_result.all()}

        # Recent hires
        recent_hires = await session.execute(
            select(func.count(Candidate.id)).where(
                and_(
                    Candidate.stage == 'hired',
                    Candidate.stage_changed_at >= thirty_days_ago
                )
            )
        )

        # Pending interviews
        pending_interviews = await session.execute(
            select(func.count(Candidate.id)).where(
                and_(
                    Candidate.stage == 'interview',
                    Candidate.status != 'completed'
                )
            )
        )

        # Pending offers
        pending_offers = await session.execute(
            select(func.count(Candidate.id)).where(
                and_(
                    Candidate.stage == 'offer',
                    Candidate.status.in_(['offer', 'in_preparation', 'released'])
                )
            )
        )

        # Priority counts
        priority_result = await session.execute(
            select(RecruitmentRequest.priority, func.count(RecruitmentRequest.id))
            .where(RecruitmentRequest.status.in_(['pending', 'approved']))
            .group_by(RecruitmentRequest.priority)
        )
        by_priority = {row[0] or 'normal': row[1] for row in priority_result.all()}

        # Calculate conversion rates
        total_cand = total_candidates.scalar() or 0
        screening_count = pipeline_counts.get('screening', 0) + pipeline_counts.get('interview', 0) + pipeline_counts.get('offer', 0) + pipeline_counts.get('hired', 0)
        interview_count = pipeline_counts.get('interview', 0) + pipeline_counts.get('offer', 0) + pipeline_counts.get('hired', 0)
        offer_count = pipeline_counts.get('offer', 0) + pipeline_counts.get('hired', 0)
        hired_count = pipeline_counts.get('hired', 0)

        applied_count = pipeline_counts.get('applied', 0) + screening_count

        app_to_screen_rate = (screening_count / applied_count * 100) if applied_count > 0 else None
        screen_to_interview_rate = (interview_count / screening_count * 100) if screening_count > 0 else None
        interview_to_offer_rate = (offer_count / interview_count * 100) if interview_count > 0 else None
        offer_accept_rate = (hired_count / offer_count * 100) if offer_count > 0 else None

        # Overdue requests (past target hire date)
        overdue = await session.execute(
            select(func.count(RecruitmentRequest.id)).where(
                and_(
                    RecruitmentRequest.target_hire_date < date.today(),
                    RecruitmentRequest.status.in_(['pending', 'approved'])
                )
            )
        )

        return {
            "total_requests": total_requests.scalar() or 0,
            "active_requests": active_requests.scalar() or 0,
            "filled_requests": filled_requests.scalar() or 0,
            "cancelled_requests": cancelled_requests.scalar() or 0,
            "total_candidates": total_cand,
            "candidates_by_stage": pipeline_counts,
            "candidates_by_source": by_source,
            "candidates_by_status": by_status,
            "avg_time_to_fill": None,  # Would need historical data
            "avg_time_in_screening": None,
            "avg_time_to_offer": None,
            "application_to_screening_rate": round(app_to_screen_rate, 1) if app_to_screen_rate else None,
            "screening_to_interview_rate": round(screen_to_interview_rate, 1) if screen_to_interview_rate else None,
            "interview_to_offer_rate": round(interview_to_offer_rate, 1) if interview_to_offer_rate else None,
            "offer_acceptance_rate": round(offer_accept_rate, 1) if offer_accept_rate else None,
            "recent_hires": recent_hires.scalar() or 0,
            "pending_interviews": pending_interviews.scalar() or 0,
            "pending_offers": pending_offers.scalar() or 0,
            "overdue_requests": overdue.scalar() or 0,
            "requests_by_priority": by_priority
        }


    async def bulk_update_candidate_stage(
        self,
        session: AsyncSession,
        candidate_ids: List[int],
        new_stage: str,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Bulk update candidate stages.
        
        Returns:
            {"success_count": int, "failed_count": int, "failed_ids": List[int], "message": str}
        """
        success_count = 0
        failed_count = 0
        failed_ids = []
        now = datetime.now()
        
        for candidate_id in candidate_ids:
            try:
                candidate = await self.get_candidate(session, candidate_id)
                if not candidate:
                    failed_count += 1
                    failed_ids.append(candidate_id)
                    continue
                
                candidate.stage = new_stage
                candidate.stage_changed_at = now
                candidate.status = new_stage  # Sync status with stage
                
                if notes:
                    # Append notes to recruiter_notes
                    timestamp = now.strftime("%Y-%m-%d %H:%M")
                    note_entry = f"[{timestamp}] Stage changed to {new_stage}: {notes}"
                    if candidate.recruiter_notes:
                        candidate.recruiter_notes += f"\n{note_entry}"
                    else:
                        candidate.recruiter_notes = note_entry
                
                success_count += 1
                
            except Exception as e:
                logger.error(f"Failed to update candidate {candidate_id}: {str(e)}")
                failed_count += 1
                failed_ids.append(candidate_id)
        
        await session.commit()
        
        return {
            "success_count": success_count,
            "failed_count": failed_count,
            "failed_ids": failed_ids,
            "message": f"Successfully updated {success_count} candidates, {failed_count} failed"
        }

    async def bulk_reject_candidates(
        self,
        session: AsyncSession,
        candidate_ids: List[int],
        rejection_reason: str
    ) -> Dict[str, Any]:
        """
        Bulk reject candidates with reason.
        
        Returns:
            {"success_count": int, "failed_count": int, "failed_ids": List[int], "message": str}
        """
        success_count = 0
        failed_count = 0
        failed_ids = []
        now = datetime.now()
        
        for candidate_id in candidate_ids:
            try:
                candidate = await self.get_candidate(session, candidate_id)
                if not candidate:
                    failed_count += 1
                    failed_ids.append(candidate_id)
                    continue
                
                candidate.stage = "rejected"
                candidate.status = "rejected"
                candidate.stage_changed_at = now
                candidate.rejection_reason = rejection_reason
                
                # Add note to recruiter_notes
                timestamp = now.strftime("%Y-%m-%d %H:%M")
                note_entry = f"[{timestamp}] Rejected: {rejection_reason}"
                if candidate.recruiter_notes:
                    candidate.recruiter_notes += f"\n{note_entry}"
                else:
                    candidate.recruiter_notes = note_entry
                
                success_count += 1
                
            except Exception as e:
                logger.error(f"Failed to reject candidate {candidate_id}: {str(e)}")
                failed_count += 1
                failed_ids.append(candidate_id)
        
        await session.commit()
        
        return {
            "success_count": success_count,
            "failed_count": failed_count,
            "failed_ids": failed_ids,
            "message": f"Successfully rejected {success_count} candidates, {failed_count} failed"
        }

    async def get_recruitment_metrics(self, session: AsyncSession) -> Dict[str, Any]:
        """
        Get detailed recruitment metrics including time-to-hire and source effectiveness.
        
        Enhanced version of get_stats with additional analytics.
        """
        # Get basic stats first
        stats = await self.get_stats(session)
        
        # Calculate time-to-hire average (from created_at to offer stage)
        time_to_hire_query = select(
            func.avg(
                func.extract('epoch', Candidate.stage_changed_at - Candidate.created_at) / 86400
            )
        ).where(
            and_(
                Candidate.stage == "offer",
                Candidate.stage_changed_at.isnot(None)
            )
        )
        time_to_hire_result = await session.execute(time_to_hire_query)
        avg_time_to_hire = time_to_hire_result.scalar()
        
        # Calculate source effectiveness (conversion rate from applied to hired by source)
        source_effectiveness = {}
        
        # Get all unique sources
        sources_query = select(Candidate.source).distinct().where(Candidate.source.isnot(None))
        sources_result = await session.execute(sources_query)
        sources = [row[0] for row in sources_result.fetchall()]
        
        for source in sources:
            total_count = (await session.execute(
                select(func.count()).select_from(Candidate).where(Candidate.source == source)
            )).scalar() or 0
            
            hired_count = (await session.execute(
                select(func.count()).select_from(Candidate).where(
                    and_(Candidate.source == source, Candidate.stage == "hired")
                )
            )).scalar() or 0
            
            conversion_rate = round((hired_count / total_count * 100), 1) if total_count > 0 else 0
            
            source_effectiveness[source] = {
                "total": total_count,
                "hired": hired_count,
                "conversion_rate": conversion_rate
            }
        
        # Merge with basic stats
        return {
            **stats,
            "avg_time_to_hire_days": round(avg_time_to_hire, 1) if avg_time_to_hire else None,
            "source_effectiveness": source_effectiveness
        }


# Singleton instance
recruitment_service = RecruitmentService()
