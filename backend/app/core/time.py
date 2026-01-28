from datetime import date, datetime, timezone
from zoneinfo import ZoneInfo


UAE_TZ = ZoneInfo("Asia/Dubai")


def get_utc_now() -> datetime:
    return datetime.now(timezone.utc)


def to_uae(now_utc: datetime) -> datetime:
    return now_utc.astimezone(UAE_TZ)


def get_uae_now() -> datetime:
    return to_uae(get_utc_now())


def get_uae_today() -> date:
    return get_uae_now().date()


def get_uae_today_from_utc(now_utc: datetime) -> date:
    return to_uae(now_utc).date()
