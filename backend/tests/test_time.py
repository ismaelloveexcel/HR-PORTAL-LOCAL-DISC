from datetime import date, datetime, timedelta, timezone

from app.core.time import get_uae_today_from_utc, to_uae


def test_get_uae_today_from_utc_rollover():
    now_utc = datetime(2026, 1, 10, 22, 30, tzinfo=timezone.utc)
    assert get_uae_today_from_utc(now_utc) == date(2026, 1, 11)


def test_to_uae_offset():
    now_utc = datetime(2026, 1, 10, 0, 0, tzinfo=timezone.utc)
    assert to_uae(now_utc).utcoffset() == timedelta(hours=4)
