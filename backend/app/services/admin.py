from typing import Dict, List, Optional

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.system_settings import SystemSetting
from app.repositories.system_settings import SystemSettingsRepository
from app.repositories.employees import EmployeeRepository
from app.repositories.renewals import RenewalRepository
from app.schemas.system_settings import (
    AdminDashboard,
    AdminSettingsResponse,
    AdminSettingsUpdate,
    FeaturesByCategory,
    FeatureToggle,
    FeatureToggleUpdate,
    FieldConfig,
    ModuleConfig,
    WorkflowConfig,
)


class AdminService:
    """Service for admin operations and feature management."""

    def __init__(
        self,
        settings_repo: SystemSettingsRepository,
        employee_repo: EmployeeRepository,
        renewal_repo: RenewalRepository,
    ) -> None:
        self._settings = settings_repo
        self._employees = employee_repo
        self._renewals = renewal_repo

    async def get_dashboard(self, session: AsyncSession) -> AdminDashboard:
        """Get admin dashboard overview."""
        # Initialize defaults if needed
        await self._settings.initialize_defaults(session)
        await session.commit()
        
        # Get counts
        employees = await self._employees.list_all(session, active_only=False)
        active_employees = await self._employees.list_all(session, active_only=True)
        renewals = await self._renewals.list_pending(session)
        features_enabled = await self._settings.count_enabled(session)
        features_total = await self._settings.count_total(session)
        
        # Determine system status
        if features_enabled == 0:
            system_status = "setup"
        elif features_enabled < features_total // 2:
            system_status = "partial"
        else:
            system_status = "active"
        
        return AdminDashboard(
            total_employees=len(employees),
            active_employees=len(active_employees),
            pending_renewals=len(renewals) if renewals else 0,
            features_enabled=features_enabled,
            features_total=features_total,
            system_status=system_status,
        )

    async def get_all_features(self, session: AsyncSession) -> List[FeatureToggle]:
        """Get all feature toggles."""
        await self._settings.initialize_defaults(session)
        await session.commit()
        
        settings = await self._settings.list_all(session)
        return [
            FeatureToggle(
                key=s.key,
                description=s.description or "",
                is_enabled=s.is_enabled,
                category=s.category,
            )
            for s in settings
        ]

    async def get_features_by_category(self, session: AsyncSession) -> FeaturesByCategory:
        """Get features grouped by category."""
        await self._settings.initialize_defaults(session)
        await session.commit()
        
        settings = await self._settings.list_all(session)
        
        result = FeaturesByCategory()
        for s in settings:
            toggle = FeatureToggle(
                key=s.key,
                description=s.description or "",
                is_enabled=s.is_enabled,
                category=s.category,
            )
            if s.category == "core":
                result.core.append(toggle)
            elif s.category == "auth":
                result.auth.append(toggle)
            elif s.category == "notifications":
                result.notifications.append(toggle)
            elif s.category == "onboarding":
                result.onboarding.append(toggle)
            elif s.category == "external":
                result.external.append(toggle)
            elif s.category == "workflow":
                result.workflow.append(toggle)
            elif s.category == "reports":
                result.reports.append(toggle)
            elif s.category == "documents":
                result.documents.append(toggle)
            elif s.category == "passes":
                result.passes.append(toggle)
        
        return result

    async def update_feature(
        self, session: AsyncSession, key: str, is_enabled: bool
    ) -> FeatureToggle:
        """Update a single feature toggle."""
        setting = await self._settings.get_by_key(session, key)
        if not setting:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Feature '{key}' not found",
            )
        
        await self._settings.update_toggle(session, key, is_enabled)
        await session.commit()
        
        return FeatureToggle(
            key=setting.key,
            description=setting.description or "",
            is_enabled=is_enabled,
            category=setting.category,
        )

    async def update_features_bulk(
        self, session: AsyncSession, updates: List[FeatureToggleUpdate]
    ) -> List[FeatureToggle]:
        """Update multiple feature toggles."""
        results = []
        for update in updates:
            result = await self.update_feature(session, update.key, update.is_enabled)
            results.append(result)
        return results

    async def enter_setup_mode(self, session: AsyncSession) -> Dict[str, int]:
        """Disable all features for system setup."""
        await self._settings.initialize_defaults(session)
        disabled = await self._settings.disable_all(session)
        await session.commit()
        return {"disabled_features": disabled}

    async def enable_core_features(self, session: AsyncSession) -> Dict[str, int]:
        """Enable only core features."""
        await self._settings.initialize_defaults(session)
        enabled = await self._settings.enable_core_only(session)
        await session.commit()
        return {"enabled_features": enabled}

    async def is_feature_enabled(self, session: AsyncSession, key: str) -> bool:
        """Check if a specific feature is enabled."""
        return await self._settings.is_feature_enabled(session, key)

    # ==================== AdminSettings API Methods ====================

    def _get_default_fields(self) -> List[FieldConfig]:
        """Return default field configurations."""
        return [
            # Basic Info
            FieldConfig(id="name", name="Employee Name", category="Basic Info", required=True, visible=True, description="Full name of the employee"),
            FieldConfig(id="email", name="Email Address", category="Basic Info", required=True, visible=True, description="Work email address"),
            FieldConfig(id="department", name="Department", category="Basic Info", required=True, visible=True, description="Department assignment"),
            FieldConfig(id="job_title", name="Job Title", category="Basic Info", required=True, visible=True, description="Position title"),
            FieldConfig(id="employee_id", name="Employee ID", category="Basic Info", required=True, visible=True, description="Unique employee identifier"),
            # UAE Compliance
            FieldConfig(id="visa_number", name="Visa Number", category="UAE Compliance", required=False, visible=True, description="UAE visa number"),
            FieldConfig(id="visa_expiry", name="Visa Expiry Date", category="UAE Compliance", required=False, visible=True, description="Visa expiration date"),
            FieldConfig(id="emirates_id", name="Emirates ID", category="UAE Compliance", required=False, visible=True, description="Emirates ID number"),
            FieldConfig(id="emirates_id_expiry", name="Emirates ID Expiry", category="UAE Compliance", required=False, visible=True, description="Emirates ID expiration date"),
            FieldConfig(id="medical_fitness", name="Medical Fitness", category="UAE Compliance", required=False, visible=True, description="Medical fitness certificate"),
            FieldConfig(id="iloe_status", name="ILOE Status", category="UAE Compliance", required=False, visible=True, description="Insurance Letter of Employment status"),
            # Contract
            FieldConfig(id="contract_type", name="Contract Type", category="Contract", required=True, visible=True, description="Employment contract type"),
            FieldConfig(id="contract_start", name="Contract Start Date", category="Contract", required=True, visible=True, description="Contract start date"),
            FieldConfig(id="contract_end", name="Contract End Date", category="Contract", required=False, visible=True, description="Contract end date"),
            FieldConfig(id="probation_end", name="Probation End Date", category="Contract", required=False, visible=True, description="Probation period end date"),
            FieldConfig(id="salary", name="Basic Salary", category="Contract", required=False, visible=False, description="Monthly basic salary"),
            # Personal
            FieldConfig(id="date_of_birth", name="Date of Birth", category="Personal", required=True, visible=True, description="Employee date of birth"),
            FieldConfig(id="nationality", name="Nationality", category="Personal", required=False, visible=True, description="Employee nationality"),
            FieldConfig(id="passport_number", name="Passport Number", category="Personal", required=False, visible=True, description="Passport number"),
            FieldConfig(id="emergency_contact", name="Emergency Contact", category="Personal", required=False, visible=True, description="Emergency contact information"),
        ]

    def _get_default_workflows(self) -> List[WorkflowConfig]:
        """Return default workflow configurations."""
        return [
            WorkflowConfig(id="onboarding", name="Employee Onboarding", enabled=True, description="New employee onboarding workflow", category="Onboarding"),
            WorkflowConfig(id="offboarding", name="Employee Offboarding", enabled=True, description="Employee exit workflow", category="Offboarding"),
            WorkflowConfig(id="contract_renewal", name="Contract Renewal", enabled=True, description="Contract renewal reminders and workflow", category="Compliance"),
            WorkflowConfig(id="visa_renewal", name="Visa Renewal Alerts", enabled=True, description="Visa expiry notifications", category="Compliance"),
            WorkflowConfig(id="medical_renewal", name="Medical Fitness Renewal", enabled=True, description="Medical certificate renewal reminders", category="Compliance"),
            WorkflowConfig(id="probation_review", name="Probation Review", enabled=True, description="Probation period completion workflow", category="HR"),
            WorkflowConfig(id="leave_approval", name="Leave Approval", enabled=True, description="Leave request approval workflow", category="HR"),
            WorkflowConfig(id="timesheet_approval", name="Timesheet Approval", enabled=False, description="Weekly timesheet approval workflow", category="HR"),
            WorkflowConfig(id="recruitment_pipeline", name="Recruitment Pipeline", enabled=True, description="Candidate tracking workflow", category="Recruitment"),
            WorkflowConfig(id="interview_scheduling", name="Interview Scheduling", enabled=True, description="Interview scheduling automation", category="Recruitment"),
        ]

    def _get_default_modules(self) -> List[ModuleConfig]:
        """Return default module configurations."""
        return [
            ModuleConfig(id="employees", name="Employee Management", enabled=True, description="Core employee records and profiles"),
            ModuleConfig(id="renewals", name="Contract Renewals", enabled=True, description="Contract renewal tracking"),
            ModuleConfig(id="compliance", name="UAE Compliance", enabled=True, description="Visa, EID, medical fitness tracking"),
            ModuleConfig(id="attendance", name="Attendance Tracking", enabled=True, description="Time and attendance management"),
            ModuleConfig(id="leave", name="Leave Management", enabled=True, description="Leave requests and balances"),
            ModuleConfig(id="recruitment", name="Recruitment", enabled=True, description="Candidate and interview management"),
            ModuleConfig(id="documents", name="Document Generation", enabled=True, description="Employment letters and certificates"),
            ModuleConfig(id="reports", name="Reports & Analytics", enabled=False, description="HR reports and dashboards"),
        ]

    async def get_admin_settings(self, session: AsyncSession) -> AdminSettingsResponse:
        """Get all admin settings for the AdminSettings UI component."""
        # Try to load from database, fall back to defaults
        fields_setting = await self._settings.get_by_key(session, "admin_settings_fields")
        workflows_setting = await self._settings.get_by_key(session, "admin_settings_workflows")
        modules_setting = await self._settings.get_by_key(session, "admin_settings_modules")
        
        # Use stored values or defaults
        import json
        
        fields = self._get_default_fields()
        if fields_setting and fields_setting.value:
            try:
                stored_fields = json.loads(fields_setting.value)
                fields = [FieldConfig(**f) for f in stored_fields]
            except (json.JSONDecodeError, TypeError):
                pass
        
        workflows = self._get_default_workflows()
        if workflows_setting and workflows_setting.value:
            try:
                stored_workflows = json.loads(workflows_setting.value)
                workflows = [WorkflowConfig(**w) for w in stored_workflows]
            except (json.JSONDecodeError, TypeError):
                pass
        
        modules = self._get_default_modules()
        if modules_setting and modules_setting.value:
            try:
                stored_modules = json.loads(modules_setting.value)
                modules = [ModuleConfig(**m) for m in stored_modules]
            except (json.JSONDecodeError, TypeError):
                pass
        
        return AdminSettingsResponse(
            fields=fields,
            workflows=workflows,
            modules=modules,
        )

    async def update_admin_settings(
        self, session: AsyncSession, settings: AdminSettingsUpdate
    ) -> AdminSettingsResponse:
        """Update admin settings."""
        import json
        
        if settings.fields is not None:
            fields_json = json.dumps([f.model_dump() for f in settings.fields])
            await self._settings.upsert_setting(
                session,
                key="admin_settings_fields",
                value=fields_json,
                category="admin",
                description="Field configurations for AdminSettings UI",
            )
        
        if settings.workflows is not None:
            workflows_json = json.dumps([w.model_dump() for w in settings.workflows])
            await self._settings.upsert_setting(
                session,
                key="admin_settings_workflows",
                value=workflows_json,
                category="admin",
                description="Workflow configurations for AdminSettings UI",
            )
        
        if settings.modules is not None:
            modules_json = json.dumps([m.model_dump() for m in settings.modules])
            await self._settings.upsert_setting(
                session,
                key="admin_settings_modules",
                value=modules_json,
                category="admin",
                description="Module configurations for AdminSettings UI",
            )
        
        await session.commit()
        return await self.get_admin_settings(session)


# Example: Automated compliance report export (placeholder)
def export_compliance_report():
    # Implement scheduled export logic here
    pass

# Placeholder for onboarding and external user modules
# Implement onboarding logic and external user management here

# Singleton instance
admin_service = AdminService(
    SystemSettingsRepository(),
    EmployeeRepository(),
    RenewalRepository(),
)
