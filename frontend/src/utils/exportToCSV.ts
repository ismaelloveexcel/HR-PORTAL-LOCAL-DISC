/**
 * CSV Export Utilities
 * Provides functions to export data to CSV files for Excel analysis
 */

/**
 * Generic function to export array of objects to CSV
 */
export function exportToCSV<T extends Record<string, any>>(
  data: T[],
  filename: string,
  columns?: Array<{ key: keyof T; label: string }>
) {
  if (data.length === 0) {
    alert('No data to export')
    return
  }

  // If columns not specified, use all keys from first object
  const headers = columns
    ? columns.map(col => col.label)
    : Object.keys(data[0])

  const keys = columns
    ? columns.map(col => col.key as string)
    : Object.keys(data[0])

  // Build CSV content
  const csvRows = [
    headers.join(','), // Header row
    ...data.map(row =>
      keys.map(key => {
        const value = row[key]
        // Handle values that might contain commas or quotes
        if (value === null || value === undefined) return ''
        const stringValue = String(value)
        if (stringValue.includes(',') || stringValue.includes('"') || stringValue.includes('\n')) {
          return `"${stringValue.replace(/"/g, '""')}"`
        }
        return stringValue
      }).join(',')
    )
  ]

  const csvContent = csvRows.join('\n')

  // Create download link
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  const url = URL.createObjectURL(blob)
  
  link.setAttribute('href', url)
  link.setAttribute('download', filename)
  link.style.visibility = 'hidden'
  
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

/**
 * Export employees list to CSV
 */
export function exportEmployeesToCSV(employees: any[]) {
  const columns = [
    { key: 'employee_id', label: 'Employee ID' },
    { key: 'name', label: 'Name' },
    { key: 'email', label: 'Email' },
    { key: 'department', label: 'Department' },
    { key: 'job_title', label: 'Job Title' },
    { key: 'employment_status', label: 'Status' },
    { key: 'joining_date', label: 'Joining Date' },
    { key: 'nationality', label: 'Nationality' },
    { key: 'visa_number', label: 'Visa Number' },
    { key: 'visa_expiry_date', label: 'Visa Expiry' },
    { key: 'emirates_id_number', label: 'Emirates ID' },
    { key: 'emirates_id_expiry', label: 'EID Expiry' },
    { key: 'contract_type', label: 'Contract Type' },
    { key: 'contract_end_date', label: 'Contract End' }
  ]
  
  const timestamp = new Date().toISOString().split('T')[0]
  exportToCSV(employees, `employees_export_${timestamp}.csv`, columns)
}

/**
 * Export compliance alerts to CSV
 */
export function exportComplianceAlertsToCSV(alerts: any[]) {
  const columns = [
    { key: 'employee_id', label: 'Employee ID' },
    { key: 'employee_name', label: 'Employee Name' },
    { key: 'document_type', label: 'Document Type' },
    { key: 'expiry_date', label: 'Expiry Date' },
    { key: 'days_until_expiry', label: 'Days Until Expiry' },
    { key: 'status', label: 'Status' }
  ]
  
  const timestamp = new Date().toISOString().split('T')[0]
  exportToCSV(alerts, `compliance_alerts_${timestamp}.csv`, columns)
}

/**
 * Export attendance records to CSV
 */
export function exportAttendanceToCSV(records: any[]) {
  const columns = [
    { key: 'attendance_date', label: 'Date' },
    { key: 'employee_name', label: 'Employee' },
    { key: 'clock_in', label: 'Clock In' },
    { key: 'clock_out', label: 'Clock Out' },
    { key: 'work_type', label: 'Work Type' },
    { key: 'total_hours', label: 'Total Hours' },
    { key: 'regular_hours', label: 'Regular Hours' },
    { key: 'overtime_hours', label: 'Overtime Hours' },
    { key: 'status', label: 'Status' },
    { key: 'is_late', label: 'Late' },
    { key: 'late_minutes', label: 'Late Minutes' },
    { key: 'notes', label: 'Notes' }
  ]
  
  const timestamp = new Date().toISOString().split('T')[0]
  exportToCSV(records, `attendance_${timestamp}.csv`, columns)
}

/**
 * Export candidates list to CSV
 */
export function exportCandidatesToCSV(candidates: any[]) {
  const columns = [
    { key: 'full_name', label: 'Full Name' },
    { key: 'email', label: 'Email' },
    { key: 'phone', label: 'Phone' },
    { key: 'position_applied', label: 'Position Applied' },
    { key: 'status', label: 'Status' },
    { key: 'source', label: 'Source' },
    { key: 'applied_date', label: 'Applied Date' },
    { key: 'cv_scoring', label: 'CV Score' },
    { key: 'experience_years', label: 'Years Experience' },
    { key: 'current_company', label: 'Current Company' },
    { key: 'current_position', label: 'Current Position' }
  ]
  
  const timestamp = new Date().toISOString().split('T')[0]
  exportToCSV(candidates, `candidates_${timestamp}.csv`, columns)
}

/**
 * Export recruitment positions to CSV
 */
export function exportRecruitmentRequestsToCSV(requests: any[]) {
  const columns = [
    { key: 'position_title', label: 'Position Title' },
    { key: 'department', label: 'Department' },
    { key: 'employment_type', label: 'Employment Type' },
    { key: 'status', label: 'Status' },
    { key: 'requested_date', label: 'Requested Date' },
    { key: 'headcount', label: 'Headcount' },
    { key: 'salary_range_min', label: 'Salary Min' },
    { key: 'salary_range_max', label: 'Salary Max' },
    { key: 'requested_by', label: 'Requested By' }
  ]
  
  const timestamp = new Date().toISOString().split('T')[0]
  exportToCSV(requests, `recruitment_positions_${timestamp}.csv`, columns)
}
