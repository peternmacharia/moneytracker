"""
app/utils/filters.py — Custom Jinja template filters and context processors for the app
"""

from datetime import datetime, timezone


def register_filters(app):
    """
    A function filter for the jinja templates
    """
    # ------------------------------------------------------------------
    # Time and date filters
    # ------------------------------------------------------------------
    @app.template_filter("timeago")
    def timeago_filter(dt):
        if not dt:
            return ""
        now = datetime.now(timezone.utc)
        diff = now - dt.replace(tzinfo=timezone.utc) if dt.tzinfo is None else now - dt
        seconds = int(diff.total_seconds())
        if seconds < 60:
            return "just now"
        if seconds < 3600:
            return f"{seconds // 60}m ago"
        if seconds < 86400:
            return f"{seconds // 3600}h ago"
        return f"{seconds // 86400}d ago"

    @app.template_filter("fmt_dt")
    def fmt_dt_filter(dt, fmt="%b %d, %Y at %H:%M %p"):
        if not dt:
            return "—"
        return dt.strftime(fmt)

    @app.template_filter("date")
    def date_filter(dt, fmt="%b %d, %Y"):
        if not dt:
            return "—"
        return dt.strftime(fmt)


    # ------------------------------------------------------------------
    # Percentage and currency filters
    # ------------------------------------------------------------------
    @app.template_filter("pct")
    def pct_filter(value, total):
        if not total:
            return 0
        return round((value / total) * 100, 1)


    # Comma formater for larger numbers
    @app.template_filter('currency')
    def currency_format(value):
        """
        Format value as currency with commas and 2 decimal places
        """
        if value is None:
            return "0.00"
        return f"{float(value):,.2f}"


    # Percentage formatter
    @app.template_filter('percentage')
    def percentage_format(value):
        """
        Format value as percentage with 2 decimal places
        """
        if value is None:
            return "0.00%"
        return f"{float(value):.2f}%"


    # ------------------------------------------------------------------
    # Boolean filters
    # ------------------------------------------------------------------
    @app.template_filter("active_badge")
    def active_badge(is_active):
        return "badge bg-success" if is_active else "badge bg-secondary"


    # ------------------------------------------------------------------
    # Asset status and condition badge filters
    # ------------------------------------------------------------------
    @app.template_filter("asset_condition")
    def asset_condition_badge(status):
        badges = {
            "NEW": "badge text-bg-success",
            "GOOD": "badge text-bg-primary",
            "FAIR": "badge text-bg-secondary",
            "POOR": "badge text-bg-warning",
            "DAMAGED": "badge text-bg-danger",
        }
        return badges.get(status, "badge text-bg-dark")


    # ------------------------------------------------------------------
    # Asset Maintenance type and priority badge filters
    # ------------------------------------------------------------------
    @app.template_filter("maintenance_type")
    def maintenance_type_badge(status):
        badges = {
            "PREVENTIVE": "badge text-bg-success",
            "CORRECTIVE": "badge text-bg-warning",
            "INSPECTION": "badge text-bg-info",
            "ROUTINE": "badge text-bg-primary",
        }
        return badges.get(status, "badge text-bg-dark")

    @app.template_filter("maintenance_priority")
    def maintenance_priority_badge(status):
        badges = {
            "CRITICAL": "badge text-bg-danger",
            "HIGH": "badge text-bg-warning",
            "MEDIUM": "badge text-bg-info",
            "LOW": "badge text-bg-secondary",
            "ROUTINE": "badge text-bg-primary",
        }
        return badges.get(status, "badge text-bg-dark")


    # ------------------------------------------------------------------
    # Asset Audit outcome badge filters
    # ------------------------------------------------------------------
    @app.template_filter("audit_badge")
    def asset_audit_badge(status):
        badges = {
            "VERIFIED": "badge text-bg-success",
            "MISSING": "badge text-bg-danger",
            "DISCREPANCY": "badge text-bg-warning",
        }
        return badges.get(status, "badge text-bg-dark")


    # ------------------------------------------------------------------
    # Asset depreciation method badge filters
    # ------------------------------------------------------------------
    @app.template_filter("depreciation_badge")
    def depreciation_method_badge(status):
        badges = {
            "STRAIGHT_LINE": "badge text-bg-primary",
            "DECLINING_BALANCE": "badge text-bg-info",
            "SUM_OF_YEARS_DIGITS": "badge text-bg-secondary",
        }
        return badges.get(status, "badge text-bg-dark")


    # ------------------------------------------------------------------
    # Asset Disposal method and status badge filter
    # ------------------------------------------------------------------
    @app.template_filter("disposal_method")
    def disposal_method_badge(status):
        badges = {
            "SALE": "badge text-bg-success",
            "SCRAP": "badge text-bg-warning",
            "DONATION": "badge text-bg-info",
            "WRITE_OFF": "badge text-bg-danger",
            "RETURNED_TO_LESSOR": "badge text-bg-dark",
            "DESTROYED": "badge text-bg-secondary",

        }
        return badges.get(status, "badge text-bg-dark")

    @app.template_filter("disposal_status")
    def disposal_status_badge(status):
        badges = {
            "PENDING_APPROVAL": "badge text-bg-secondary",
            "APPROVED": "badge text-bg-primary",
            "IN_PROGRESS": "badge text-bg-warning",
            "COMPLETED": "badge text-bg-success",
            "REJECTED": "badge text-bg-danger",
            "CANCELLED": "badge text-bg-dark",
        }
        return badges.get(status, "badge text-bg-dark")


    # ------------------------------------------------------------------
    # Software badge filter
    # ------------------------------------------------------------------
    @app.template_filter("software_type")
    def software_license_type_badge(status):
        badges = {
            "PERPETUAL": "badge text-bg-success",
            "SUBSCRIPTION": "badge text-bg-warning",
            "OPEN_SOURCE": "badge text-bg-info",
            "FREEWARE": "badge text-bg-secondary",
            "OEM": "badge text-bg-dark",
            "ENTERPRISE": "badge text-bg-primary",
            "CLOUD_BASED": "badge text-bg-danger",
        }
        return badges.get(status, "badge text-bg-dark")

    @app.template_filter("software_category")
    def software_category_badge(status):
        badges = {
            "OPERATING_SYSTEM": "badge text-bg-secondary",
            "PRODUCTIVITY": "badge text-bg-primary",
            "DEVELOPMENT": "badge text-bg-warning",
            "DESIGN": "badge text-bg-info",
            "SECURITY": "badge text-bg-danger",
            "DATABASE": "badge text-bg-dark",
            "COMMUNICATION": "badge text-bg-secondary",
            "ACCOUNTING": "badge text-bg-primary",
            "CRM": "badge text-bg-warning",
            "ERP": "badge text-bg-info",
            "PROJECT_MANAGEMENT": "badge text-bg-danger",
            "MONITORING": "badge text-bg-dark",
            "BACKUP": "badge text-bg-secondary",
            "VIRTUALIZATION": "badge text-bg-primary",
        }
        return badges.get(status, "badge text-bg-dark")

    @app.template_filter("software_subscription")
    def software_renewal_period_badge(status):
        badges = {
            "MONTHLY": "badge text-bg-warning",
            "ANNUALLY": "badge text-bg-primary",
            "NONE": "badge text-bg-secondary",
        }
        return badges.get(status, "badge text-bg-dark")

    @app.template_filter("software_status")
    def software_status_badge(status):
        badges = {
            "ACTIVE": "badge text-bg-success",
            "EXPIRED": "badge text-bg-danger",
            "SUSPENDED": "badge text-bg-warning",
            "CANCELLED": "badge text-bg-secondary",
            "PENDING_RENEWAL": "badge text-bg-info",
            "RETIRED": "badge text-bg-dark",
            "REVOKED": "badge text-bg-secondary",
        }
        return badges.get(status, "badge text-bg-dark")


    # ------------------------------------------------------------------
    # Software License Assignment and Renewal filter
    # ------------------------------------------------------------------
    @app.template_filter("sassignment_status")
    def software_assignment_status_badge(status):
        badges = {
            "ACTIVE": "badge text-bg-success",
            "SUSPENDED": "badge text-bg-warning",
            "EXPIRED": "badge text-bg-danger",
            "REVOKED": "badge text-bg-secondary",
            "RETURNED": "badge text-bg-info",
            "TRANSFERRED": "badge text-bg-primary",
        }
        return badges.get(status, "badge text-bg-dark")

    @app.template_filter("srenewal_status")
    def software_renewal_status_badge(status):
        badges = {
            "PENDING": "badge text-bg-warning",
            "COMPLETED": "badge text-bg-success",
            "FAILED": "badge text-bg-danger",
            "CANCELLED": "badge text-bg-secondary",
        }
        return badges.get(status, "badge text-bg-dark")

    @app.template_filter("srenewal_payment")
    def software_renewal_payment_status_badge(status):
        badges = {
            "PENDING": "badge text-bg-warning",
            "PAID": "badge text-bg-success",
            "FAILED": "badge text-bg-danger",
            "CANCELLED": "badge text-bg-secondary",
        }
        return badges.get(status, "badge text-bg-dark")


    # ------------------------------------------------------------------
    # Attachment Entity Name filter
    # ------------------------------------------------------------------
    @app.template_filter("entity_badge")
    def entity_name_badge(status):
        badges = {
            "asset": "badge text-bg-primary",
            "assignment": "badge text-bg-info",
            "maintenance": "badge text-bg-warning",
            "disposal": "badge text-bg-secondary",
        }
        return badges.get(status, "badge text-bg-dark")


    # ------------------------------------------------------------------
    # Attachment Type Name filter
    # ------------------------------------------------------------------
    @app.template_filter("type_badge")
    def type_name_badge(status):
        badges = {
            "IMAGE": "badge text-bg-primary",
            "DOCUMENT": "badge text-bg-info",
        }
        return badges.get(status, "badge text-bg-dark")







def register_context_processors(app):
    """A function to register the context processor"""
    @app.context_processor
    def inject_globals():
        return {"now": datetime.now(timezone.utc)}


# End of file
