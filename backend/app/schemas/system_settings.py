from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class FeatureToggle(BaseModel):
    """Schema for a feature toggle."""
    
    key: str = Field(..., description="Unique feature key")
    description: str = Field(..., description="Human-readable description")
    is_enabled: bool = Field(..., description="Whether the feature is enabled")
    category: str = Field(..., description="Feature category")
    
    model_config = ConfigDict(from_attributes=True)


class FeatureToggleUpdate(BaseModel):
    """Schema for updating a feature toggle."""
    
    key: str = Field(..., description="Feature key to update")
    is_enabled: bool = Field(..., description="New enabled state")


class FeatureToggleBulkUpdate(BaseModel):
    """Schema for bulk updating feature toggles."""
    
    toggles: List[FeatureToggleUpdate] = Field(..., description="List of toggles to update")


class SystemSettingResponse(BaseModel):
    """Schema for system setting response."""
    
    id: int = Field(..., description="Setting ID")
    key: str = Field(..., description="Setting key")
    value: str = Field(..., description="Setting value")
    description: Optional[str] = Field(None, description="Setting description")
    is_enabled: bool = Field(..., description="Whether enabled")
    category: str = Field(..., description="Setting category")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    model_config = ConfigDict(from_attributes=True)


class FeaturesByCategory(BaseModel):
    """Schema for features grouped by category."""
    
    core: List[FeatureToggle] = Field(default_factory=list, description="Core features")
    auth: List[FeatureToggle] = Field(default_factory=list, description="Authentication features")
    notifications: List[FeatureToggle] = Field(default_factory=list, description="Notification features")
    onboarding: List[FeatureToggle] = Field(default_factory=list, description="Onboarding features")
    external: List[FeatureToggle] = Field(default_factory=list, description="External users features")
    workflow: List[FeatureToggle] = Field(default_factory=list, description="Workflow features")
    reports: List[FeatureToggle] = Field(default_factory=list, description="Reporting features")
    documents: List[FeatureToggle] = Field(default_factory=list, description="Document features")
    passes: List[FeatureToggle] = Field(default_factory=list, description="Pass generation features")


class AdminDashboard(BaseModel):
    """Schema for admin dashboard overview."""
    
    total_employees: int = Field(..., description="Total number of employees")
    active_employees: int = Field(..., description="Number of active employees")
    pending_renewals: int = Field(..., description="Number of pending renewals")
    features_enabled: int = Field(..., description="Number of enabled features")
    features_total: int = Field(..., description="Total number of features")
    system_status: str = Field(..., description="System status: setup, active, maintenance")


# ==================== AdminSettings API Schemas ====================

class FieldConfig(BaseModel):
    """Schema for field configuration in AdminSettings."""
    
    id: str = Field(..., description="Unique field identifier")
    name: str = Field(..., description="Human-readable field name")
    category: str = Field(..., description="Field category (Basic Info, UAE Compliance, Contract, Personal)")
    required: bool = Field(..., description="Whether the field is required")
    visible: bool = Field(..., description="Whether the field is visible")
    description: str = Field(..., description="Field description")


class WorkflowConfig(BaseModel):
    """Schema for workflow configuration in AdminSettings."""
    
    id: str = Field(..., description="Unique workflow identifier")
    name: str = Field(..., description="Human-readable workflow name")
    enabled: bool = Field(..., description="Whether the workflow is enabled")
    description: str = Field(..., description="Workflow description")
    category: str = Field(..., description="Workflow category")


class ModuleConfig(BaseModel):
    """Schema for module configuration in AdminSettings."""
    
    id: str = Field(..., description="Unique module identifier")
    name: str = Field(..., description="Human-readable module name")
    enabled: bool = Field(..., description="Whether the module is enabled")
    description: str = Field(..., description="Module description")


class AdminSettingsResponse(BaseModel):
    """Schema for full AdminSettings response."""
    
    fields: List[FieldConfig] = Field(default_factory=list, description="Field configurations")
    workflows: List[WorkflowConfig] = Field(default_factory=list, description="Workflow configurations")
    modules: List[ModuleConfig] = Field(default_factory=list, description="Module configurations")


class AdminSettingsUpdate(BaseModel):
    """Schema for updating AdminSettings."""
    
    fields: Optional[List[FieldConfig]] = Field(None, description="Field configurations to update")
    workflows: Optional[List[WorkflowConfig]] = Field(None, description="Workflow configurations to update")
    modules: Optional[List[ModuleConfig]] = Field(None, description="Module configurations to update")
