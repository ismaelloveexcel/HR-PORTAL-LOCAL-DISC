"""
Database indexes for performance optimization
Add these indexes to improve query performance
"""

# Run this SQL in your PostgreSQL database or create an Alembic migration

INDEXES_SQL = """
-- Employees table indexes
CREATE INDEX IF NOT EXISTS idx_employees_employee_id ON employees(employee_id);
CREATE INDEX IF NOT EXISTS idx_employees_department ON employees(department);
CREATE INDEX IF NOT EXISTS idx_employees_is_active ON employees(is_active);
CREATE INDEX IF NOT EXISTS idx_employees_profile_status ON employees(profile_status);
CREATE INDEX IF NOT EXISTS idx_employees_created_at ON employees(created_at DESC);

-- Composite index for active employee queries
CREATE INDEX IF NOT EXISTS idx_employees_active_department ON employees(is_active, department);

-- Renewal requests indexes
CREATE INDEX IF NOT EXISTS idx_renewals_status ON renewal_requests(status);
CREATE INDEX IF NOT EXISTS idx_renewals_created_at ON renewal_requests(created_at DESC);

-- Compliance-related indexes for expiry queries
CREATE INDEX IF NOT EXISTS idx_employees_visa_expiry ON employees(visa_expiry_date) WHERE visa_expiry_date IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_employees_emirates_id_expiry ON employees(emirates_id_expiry) WHERE emirates_id_expiry IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_employees_medical_expiry ON employees(medical_fitness_expiry) WHERE medical_fitness_expiry IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_employees_contract_expiry ON employees(contract_end_date) WHERE contract_end_date IS NOT NULL;

-- Onboarding tokens indexes
CREATE INDEX IF NOT EXISTS idx_onboarding_tokens_employee_id ON onboarding_tokens(employee_id);
CREATE INDEX IF NOT EXISTS idx_onboarding_tokens_is_used ON onboarding_tokens(is_used);
CREATE INDEX IF NOT EXISTS idx_onboarding_tokens_expires_at ON onboarding_tokens(expires_at);

-- Passes indexes
CREATE INDEX IF NOT EXISTS idx_passes_status ON passes(status);
CREATE INDEX IF NOT EXISTS idx_passes_valid_until ON passes(valid_until);
CREATE INDEX IF NOT EXISTS idx_passes_employee_id ON passes(employee_id) WHERE employee_id IS NOT NULL;

-- Recruitment indexes
CREATE INDEX IF NOT EXISTS idx_recruitment_requests_status ON recruitment_requests(status);
CREATE INDEX IF NOT EXISTS idx_candidates_status ON candidates(status);
CREATE INDEX IF NOT EXISTS idx_candidates_position_id ON candidates(recruitment_position_id);
"""

# To apply these indexes, run:
# psql -h baynunahhrportal-server.postgres.database.azure.com -U uutfqkhm -d hrportal < indexes.sql
