from datetime import date, datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException

from app.models.attendance import AttendanceRecord
from app.routers import attendance as attendance_router
from app.schemas.attendance import ExceptionalOvertimeRequest, WFHApprovalRequest


class DummyResult:
    def __init__(self, row):
        self._row = row

    def first(self):
        return self._row


@pytest.mark.anyio
async def test_exceptional_overtime_blocks_when_feature_disabled(monkeypatch):
    monkeypatch.setattr(
        attendance_router,
        "check_feature_enabled",
        AsyncMock(return_value=False),
    )
    session = AsyncMock()
    request = ExceptionalOvertimeRequest(reason="urgent", exceptional_overtime=True)
    current_user = SimpleNamespace(role="admin", id=1)

    with pytest.raises(HTTPException) as exc:
        await attendance_router.set_exceptional_overtime(1, request, current_user, session)

    assert exc.value.status_code == 403


@pytest.mark.anyio
async def test_wfh_approval_denies_non_report_manager(monkeypatch):
    monkeypatch.setattr(
        attendance_router,
        "check_feature_enabled",
        AsyncMock(return_value=True),
    )
    now = datetime(2026, 1, 10, 8, 0, tzinfo=timezone.utc)
    record = AttendanceRecord(
        id=1,
        employee_id=10,
        attendance_date=date(2026, 1, 10),
        work_type="wfh",
        status="present",
        overtime_type="none",
        is_late=False,
        is_early_departure=False,
        wfh_approval_confirmed=False,
        exceptional_overtime=False,
        is_night_overtime=False,
        is_holiday_overtime=False,
        food_allowance_eligible=False,
        is_ramadan_hours=False,
        is_rest_day=False,
        exceeds_daily_limit=False,
        exceeds_overtime_limit=False,
        is_manual_entry=False,
        created_at=now,
        updated_at=now,
    )
    session = AsyncMock()
    session.execute = AsyncMock(return_value=DummyResult((record, "Employee", 99)))
    request = WFHApprovalRequest(approved=True)
    current_user = SimpleNamespace(role="manager", id=1)

    with pytest.raises(HTTPException) as exc:
        await attendance_router.approve_wfh(1, request, current_user, session)

    assert exc.value.status_code == 403


@pytest.mark.anyio
async def test_wfh_approval_allows_manager_for_direct_report(monkeypatch):
    monkeypatch.setattr(
        attendance_router,
        "check_feature_enabled",
        AsyncMock(return_value=True),
    )
    now = datetime(2026, 1, 10, 8, 0, tzinfo=timezone.utc)
    record = AttendanceRecord(
        id=1,
        employee_id=10,
        attendance_date=date(2026, 1, 10),
        work_type="wfh",
        status="present",
        overtime_type="none",
        is_late=False,
        is_early_departure=False,
        wfh_approval_confirmed=False,
        exceptional_overtime=False,
        is_night_overtime=False,
        is_holiday_overtime=False,
        food_allowance_eligible=False,
        is_ramadan_hours=False,
        is_rest_day=False,
        exceeds_daily_limit=False,
        exceeds_overtime_limit=False,
        is_manual_entry=False,
        created_at=now,
        updated_at=now,
    )
    session = AsyncMock()
    session.execute = AsyncMock(return_value=DummyResult((record, "Employee", 1)))
    request = WFHApprovalRequest(approved=True)
    current_user = SimpleNamespace(role="manager", id=1)

    response = await attendance_router.approve_wfh(1, request, current_user, session)

    assert response.wfh_approved is True
    assert record.wfh_approved_by == current_user.id
