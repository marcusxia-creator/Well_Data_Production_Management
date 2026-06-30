from datetime import date

from django.db.models import Q
from django.utils import timezone


STATUS_ABD = "ABD"
STATUS_SUSPENDED = "Suspended"
STATUS_INACTIVE = "Inactive"
STATUS_ACTIVE = "Active"
STATUS_CATEGORIES = [STATUS_ABD, STATUS_SUSPENDED, STATUS_INACTIVE, STATUS_ACTIVE]


def cutoff_24_months(today=None):
    today = today or timezone.localdate()
    year = today.year - 2
    day = min(today.day, 28)
    return date(year, today.month, day)


def parse_year_month(value):
    if not value:
        return None
    value = str(value).strip()
    for separator in ("-", "/", "_"):
        if separator in value:
            parts = value.split(separator)
            break
    else:
        parts = [value[:4], value[4:6]] if len(value) >= 6 else []

    if len(parts) < 2:
        return None

    try:
        day = int(parts[2]) if len(parts) > 2 else 1
        return date(int(parts[0]), int(parts[1]), day)
    except (TypeError, ValueError):
        return None


def activity_dates(production_summary):
    if not production_summary:
        return []

    dates = [
        production_summary.on_prod_yyyy_mm_dd,
        production_summary.on_inject_yyyy_mm_dd,
        parse_year_month(production_summary.last_prod_yyyy_mm),
        parse_year_month(production_summary.last_inject_yyyy_mm),
    ]
    return [value for value in dates if value]


def latest_activity_date(production_summary):
    dates = activity_dates(production_summary)
    return max(dates) if dates else None


def categorize_status(status_text, production_summary=None, today=None):
    normalized = (status_text or "").lower()
    if "abd" in normalized:
        return STATUS_ABD
    if "susp" in normalized:
        return STATUS_SUSPENDED

    dates = activity_dates(production_summary)
    if any(activity_date < cutoff_24_months(today) for activity_date in dates):
        return STATUS_INACTIVE

    return STATUS_ACTIVE


def status_category_filter(category):
    cutoff = cutoff_24_months()
    if category == STATUS_ABD:
        return Q(statuses__well_status_text__icontains="ABD")
    if category == STATUS_SUSPENDED:
        return Q(statuses__well_status_text__icontains="susp")
    if category == STATUS_INACTIVE:
        return (
            ~Q(statuses__well_status_text__icontains="ABD")
            & ~Q(statuses__well_status_text__icontains="susp")
            & (
                Q(production_summaries__on_prod_yyyy_mm_dd__lt=cutoff)
                | Q(production_summaries__on_inject_yyyy_mm_dd__lt=cutoff)
            )
        )
    if category == STATUS_ACTIVE:
        return (
            ~Q(statuses__well_status_text__icontains="ABD")
            & ~Q(statuses__well_status_text__icontains="susp")
            & (
                Q(production_summaries__on_prod_yyyy_mm_dd__isnull=True)
                & Q(production_summaries__on_inject_yyyy_mm_dd__isnull=True)
                | Q(production_summaries__on_prod_yyyy_mm_dd__gte=cutoff)
                | Q(production_summaries__on_inject_yyyy_mm_dd__gte=cutoff)
            )
        )
    return Q()


def inactive_activity_where(exists=True):
    prefix = "EXISTS" if exists else "NOT EXISTS"
    return f"""
        {prefix} (
        SELECT 1
        FROM well_production_summary
        WHERE well_production_summary.base_uwi = well_header.base_uwi
        AND (
        (
            last_prod_yyyy_mm ~ '^[0-9]{4}/[0-9]{2}/[0-9]{2}$'
            AND to_date(last_prod_yyyy_mm, 'YYYY/MM/DD') < %s
        )
        OR (
            last_inject_yyyy_mm ~ '^[0-9]{4}/[0-9]{2}/[0-9]{2}$'
            AND to_date(last_inject_yyyy_mm, 'YYYY/MM/DD') < %s
        )
        OR on_prod_yyyy_mm_dd < %s
        OR on_inject_yyyy_mm_dd < %s
        )
        )
    """


def apply_status_category_filter(queryset, category):
    cutoff = cutoff_24_months()
    non_abd_suspended = queryset.exclude(statuses__well_status_text__icontains="ABD").exclude(
        statuses__well_status_text__icontains="susp"
    )

    if category == STATUS_ABD:
        return queryset.filter(statuses__well_status_text__icontains="ABD")
    if category == STATUS_SUSPENDED:
        return queryset.filter(statuses__well_status_text__icontains="susp").exclude(
            statuses__well_status_text__icontains="ABD"
        )
    if category == STATUS_INACTIVE:
        return non_abd_suspended.extra(
            where=[inactive_activity_where(exists=True)],
            params=[cutoff, cutoff, cutoff, cutoff],
        )
    if category == STATUS_ACTIVE:
        return non_abd_suspended.extra(
            where=[inactive_activity_where(exists=False)],
            params=[cutoff, cutoff, cutoff, cutoff],
        )
    return queryset
