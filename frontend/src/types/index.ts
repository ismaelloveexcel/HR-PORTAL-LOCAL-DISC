// User and Authentication types
export interface User {
  id: number
  employee_id: string
  name: string
  role: string
  token: string
}

// Employee types
export interface Employee {
  id: number
  employee_id: string
  name: string
  email: string | null
  department: string | null
  date_of_birth: string
  role: string
  is_active: boolean
  password_changed: boolean
  created_at: string
  job_title?: string
  location?: string
  probation_status?: string
  employment_status?: string
  profile_status?: string
  // UAE Compliance fields
  visa_number?: string
  visa_issue_date?: string
  visa_expiry_date?: string
  emirates_id_number?: string
  emirates_id_expiry?: string
  medical_fitness_date?: string
  medical_fitness_expiry?: string
  iloe_status?: string
  iloe_expiry?: string
  contract_type?: string
  contract_start_date?: string
  contract_end_date?: string
  nationality?: string
  gender?: string
  joining_date?: string
  line_manager_name?: string
  function?: string
  status?: string
}

export interface EmployeeFormData {
  name: string
  email: string
  department: string
  job_title: string
  location: string
  nationality: string
  gender: string
  employment_status: string
  visa_number: string
  visa_issue_date: string
  visa_expiry_date: string
  emirates_id_number: string
  emirates_id_expiry: string
  medical_fitness_date: string
  medical_fitness_expiry: string
  iloe_status: string
  iloe_expiry: string
  contract_type: string
  contract_start_date: string
  contract_end_date: string
}

// Admin types
export interface FeatureToggle {
  key: string
  description: string
  is_enabled: boolean
  category: string
}

export interface AdminDashboard {
  total_employees: number
  active_employees: number
  pending_renewals: number
  features_enabled: number
  features_total: number
  system_status: string
}

// Pass types
export interface Pass {
  id: number
  pass_number: string
  pass_type: string
  full_name: string
  email: string | null
  phone: string | null
  department: string | null
  position: string | null
  valid_from: string
  valid_until: string
  access_areas: string | null
  purpose: string | null
  sponsor_name: string | null
  employee_id: string | null
  status: string
  is_printed: boolean
  created_by: string
  created_at: string
}

export interface PassFormData {
  pass_type: string
  full_name: string
  email: string
  phone: string
  department: string
  position: string
  valid_from: string
  valid_until: string
  access_areas: string
  purpose: string
  sponsor_name: string
  employee_id: string
  start_stage?: string
  stage_order?: string
}

// Onboarding types
export interface OnboardingToken {
  token: string
  employee_id: string
  employee_name: string
  created_at: string
  expires_at: string
  is_used: boolean
  is_expired: boolean
  access_count: number
}

export interface OnboardingWelcome {
  employee_id: string
  name: string
  email: string | null
  department: string | null
  job_title: string | null
  joining_date: string | null
  line_manager_name: string | null
  location: string | null
}

export interface ProfileFormData {
  emergency_contact_name: string
  emergency_contact_phone: string
  emergency_contact_relationship: string
  personal_phone: string
  personal_email: string
  current_address: string
  city: string
  country: string
  bank_name: string
  bank_account_number: string
  bank_iban: string
  passport_number: string
  passport_expiry: string
  uae_id_number: string
  uae_id_expiry: string
  highest_education: string
  shirt_size: string
  pants_size: string
  shoe_size: string
}

export interface PendingProfile {
  employee_id: string
  name: string
  department: string | null
  job_title: string | null
  submitted_at: string | null
}

// Attendance types
export interface TodayAttendanceStatus {
  date: string
  is_clocked_in: boolean
  clock_in_time: string | null
  is_on_break: boolean
  break_start_time: string | null
  work_type: string | null
  can_clock_in: boolean
  can_clock_out: boolean
  can_start_break: boolean
  can_end_break: boolean
  message: string
}

export interface AttendanceRecord {
  id: number
  employee_id: number
  employee_name: string
  attendance_date: string
  clock_in: string | null
  clock_out: string | null
  work_type: string
  total_hours: number | null
  regular_hours: number | null
  overtime_hours: number | null
  status: string
  is_late: boolean
  late_minutes: number | null
  is_early_departure: boolean
  notes: string | null
}

export interface AttendanceDashboard {
  total_employees: number
  clocked_in_today: number
  wfh_today: number
  absent_today: number
  late_today: number
  pending_wfh_approvals: number
  pending_overtime_approvals: number
  on_leave_today: number
}

// Compliance types
export interface ComplianceAlertItem {
  employee_id: string
  employee_name: string
  document_type: string
  expiry_date: string
  days_until_expiry: number
  status: string
}

export interface ComplianceAlerts {
  expired: ComplianceAlertItem[]
  days_7: ComplianceAlertItem[]
  days_30: ComplianceAlertItem[]
  days_custom: ComplianceAlertItem[]
}

// Recruitment types
export interface RecruitmentStats {
  active_positions: number
  total_candidates: number
  in_interview: number
  hired_30_days: number
}

export interface PipelineCounts {
  applied: number
  screening: number
  interview: number
  offer: number
  hired: number
}

export interface Candidate {
  id: number
  candidate_id: string
  full_name: string
  email: string
  phone: string
  position_applied: string
  status: string
  source: string
  resume_path?: string
  notes?: string
  created_at: string
  updated_at: string
}

export interface RecruitmentRequest {
  id: number
  position_title: string
  department: string
  requested_by: string
  status: string
  priority: string
  created_at: string
}

// Navigation types
/**
 * LEGACY: Section type for App.tsx navigation system
 * 
 * This type is used by the existing App.tsx (5,730 lines) which uses
 * activeSection state for navigation. As we migrate to React Router,
 * this type will eventually be removed.
 * 
 * DO NOT use this type in new code - use React Router routes instead.
 */
export type Section = 
  | 'home' 
  | 'employees' 
  | 'onboarding' 
  | 'external' 
  | 'admin' 
  | 'secret-chamber' 
  | 'passes' 
  | 'public-onboarding' 
  | 'recruitment' 
  | 'recruitment-request' 
  | 'recruitment-benefits' 
  | 'templates' 
  | 'template-manager' 
  | 'template-candidate' 
  | 'template-onboarding' 
  | 'template-employee' 
  | 'attendance' 
  | 'compliance-alerts' 
  | 'candidate-pass' 
  | 'manager-pass' 
  | 'performance' 
  | 'insurance-census' 
  | 'nomination-pass'
