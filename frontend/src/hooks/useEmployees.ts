import { useState, useCallback } from 'react'
import { Employee, EmployeeFormData, User } from '../types'
import { API_BASE, fetchWithAuth } from '../utils/api'

interface UseEmployeesReturn {
  employees: Employee[]
  loading: boolean
  error: string | null
  selectedEmployee: Employee | null
  employeeFormData: EmployeeFormData
  showEmployeeModal: boolean
  importLoading: boolean
  importResult: any | null
  fetchEmployees: () => Promise<void>
  openEmployeeModal: (emp: Employee) => void
  closeEmployeeModal: () => void
  updateEmployee: (e: React.FormEvent) => Promise<void>
  handleImportCSV: (e: React.ChangeEvent<HTMLInputElement>) => Promise<void>
  setEmployeeFormData: React.Dispatch<React.SetStateAction<EmployeeFormData>>
  clearError: () => void
}

const initialFormData: EmployeeFormData = {
  name: '',
  email: '',
  department: '',
  job_title: '',
  location: '',
  nationality: '',
  gender: '',
  employment_status: '',
  visa_number: '',
  visa_issue_date: '',
  visa_expiry_date: '',
  emirates_id_number: '',
  emirates_id_expiry: '',
  medical_fitness_date: '',
  medical_fitness_expiry: '',
  iloe_status: '',
  iloe_expiry: '',
  contract_type: '',
  contract_start_date: '',
  contract_end_date: '',
}

export function useEmployees(user: User | null): UseEmployeesReturn {
  const [employees, setEmployees] = useState<Employee[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [selectedEmployee, setSelectedEmployee] = useState<Employee | null>(null)
  const [employeeFormData, setEmployeeFormData] = useState<EmployeeFormData>(initialFormData)
  const [showEmployeeModal, setShowEmployeeModal] = useState(false)
  const [importLoading, setImportLoading] = useState(false)
  const [importResult, setImportResult] = useState<any | null>(null)

  const fetchEmployees = useCallback(async () => {
    if (!user?.token || !user?.role) return
    setLoading(true)
    try {
      const res = await fetchWithAuth(`${API_BASE}/employees?active_only=false`, {
        token: user.token,
        role: user.role,
      })
      if (res.ok) {
        const data = await res.json()
        setEmployees(data)
      }
    } catch (err) {
      console.error('Failed to fetch employees:', err)
    } finally {
      setLoading(false)
    }
  }, [user?.token, user?.role])

  const openEmployeeModal = useCallback((emp: Employee) => {
    setSelectedEmployee(emp)
    setEmployeeFormData({
      name: emp.name || '',
      email: emp.email || '',
      department: emp.department || '',
      job_title: emp.job_title || '',
      location: emp.location || '',
      nationality: emp.nationality || '',
      gender: emp.gender || '',
      employment_status: emp.employment_status || '',
      visa_number: emp.visa_number || '',
      visa_issue_date: emp.visa_issue_date || '',
      visa_expiry_date: emp.visa_expiry_date || '',
      emirates_id_number: emp.emirates_id_number || '',
      emirates_id_expiry: emp.emirates_id_expiry || '',
      medical_fitness_date: emp.medical_fitness_date || '',
      medical_fitness_expiry: emp.medical_fitness_expiry || '',
      iloe_status: emp.iloe_status || '',
      iloe_expiry: emp.iloe_expiry || '',
      contract_type: emp.contract_type || '',
      contract_start_date: emp.contract_start_date || '',
      contract_end_date: emp.contract_end_date || '',
    })
    setShowEmployeeModal(true)
    setError(null)
  }, [])

  const closeEmployeeModal = useCallback(() => {
    setShowEmployeeModal(false)
    setSelectedEmployee(null)
    setError(null)
  }, [])

  const updateEmployee = useCallback(async (e: React.FormEvent) => {
    e.preventDefault()
    if (!selectedEmployee || !user) return

    setLoading(true)
    setError(null)

    try {
      const updateData: Record<string, string> = {}
      // Only send non-empty string fields
      Object.entries(employeeFormData).forEach(([key, value]) => {
        if (typeof value === 'string' && value.trim() !== '') {
          updateData[key] = value
        }
      })

      const res = await fetchWithAuth(
        `${API_BASE}/employees/${selectedEmployee.employee_id}`,
        {
          method: 'PUT',
          body: JSON.stringify(updateData),
          token: user.token,
          role: user.role,
        }
      )

      if (!res.ok) {
        const data = await res.json()
        throw new Error(data.detail || 'Failed to update employee')
      }

      // Refresh employees list
      await fetchEmployees()
      closeEmployeeModal()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update employee')
    } finally {
      setLoading(false)
    }
  }, [selectedEmployee, employeeFormData, user, fetchEmployees, closeEmployeeModal])

  const handleImportCSV = useCallback(async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file || !user) return

    setImportLoading(true)
    setImportResult(null)
    setError(null)

    try {
      const formData = new FormData()
      formData.append('file', file)

      const res = await fetchWithAuth(`${API_BASE}/employees/import`, {
        method: 'POST',
        body: formData,
        token: user.token,
        role: user.role,
      })

      if (!res.ok) {
        const data = await res.json()
        throw new Error(data.detail || 'Import failed')
      }

      const result = await res.json()
      setImportResult(result)

      // Refresh employees list
      await fetchEmployees()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to import employees')
    } finally {
      setImportLoading(false)
      // Reset file input
      e.target.value = ''
    }
  }, [user, fetchEmployees])

  const clearError = useCallback(() => {
    setError(null)
  }, [])

  return {
    employees,
    loading,
    error,
    selectedEmployee,
    employeeFormData,
    showEmployeeModal,
    importLoading,
    importResult,
    fetchEmployees,
    openEmployeeModal,
    closeEmployeeModal,
    updateEmployee,
    handleImportCSV,
    setEmployeeFormData,
    clearError,
  }
}
