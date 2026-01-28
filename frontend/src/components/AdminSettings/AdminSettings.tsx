import { useState, useEffect } from 'react'

/**
 * AdminSettings Component
 * 
 * Provides a toggle-based configuration interface for non-technical HR admins.
 * 
 * Backend Integration:
 * - GET /api/admin/settings - Load saved settings
 * - PUT /api/admin/settings - Persist settings to database
 * 
 * Settings are stored in the system_settings table and synced across users.
 */

interface FieldConfig {
  id: string
  name: string
  category: string
  required: boolean
  visible: boolean
  description: string
}

interface WorkflowConfig {
  id: string
  name: string
  enabled: boolean
  description: string
  category: string
}

interface ModuleConfig {
  id: string
  name: string
  enabled: boolean
  description: string
}

interface AdminSettingsProps {
  onClose: () => void
  token?: string
}

// Default configurations (used as fallback if API fails)
const DEFAULT_FIELDS: FieldConfig[] = [
  // Employee Basic Fields
  { id: 'name', name: 'Employee Name', category: 'Basic Info', required: true, visible: true, description: 'Full name of the employee' },
  { id: 'email', name: 'Email Address', category: 'Basic Info', required: true, visible: true, description: 'Work email address' },
  { id: 'department', name: 'Department', category: 'Basic Info', required: true, visible: true, description: 'Department assignment' },
  { id: 'job_title', name: 'Job Title', category: 'Basic Info', required: true, visible: true, description: 'Position title' },
  { id: 'location', name: 'Work Location', category: 'Basic Info', required: false, visible: true, description: 'Office location' },
  { id: 'line_manager', name: 'Line Manager', category: 'Basic Info', required: false, visible: true, description: 'Reporting manager' },
  // UAE Compliance Fields
  { id: 'visa_number', name: 'Visa Number', category: 'UAE Compliance', required: true, visible: true, description: 'UAE residence visa number' },
  { id: 'visa_expiry', name: 'Visa Expiry Date', category: 'UAE Compliance', required: true, visible: true, description: 'Visa expiration date' },
  { id: 'emirates_id', name: 'Emirates ID', category: 'UAE Compliance', required: true, visible: true, description: 'Emirates ID number' },
  { id: 'emirates_id_expiry', name: 'Emirates ID Expiry', category: 'UAE Compliance', required: true, visible: true, description: 'Emirates ID expiration' },
  { id: 'medical_fitness', name: 'Medical Fitness', category: 'UAE Compliance', required: false, visible: true, description: 'Medical fitness certificate date' },
  { id: 'iloe_status', name: 'ILOE Status', category: 'UAE Compliance', required: false, visible: true, description: 'Insurance status' },
  // Contract Fields
  { id: 'contract_type', name: 'Contract Type', category: 'Contract', required: true, visible: true, description: 'Employment contract type' },
  { id: 'contract_start', name: 'Contract Start Date', category: 'Contract', required: true, visible: true, description: 'Contract start date' },
  { id: 'contract_end', name: 'Contract End Date', category: 'Contract', required: false, visible: true, description: 'Contract end date' },
  { id: 'probation_end', name: 'Probation End Date', category: 'Contract', required: false, visible: true, description: 'Probation end date' },
  // Personal Fields
  { id: 'date_of_birth', name: 'Date of Birth', category: 'Personal', required: true, visible: true, description: 'Employee date of birth' },
  { id: 'nationality', name: 'Nationality', category: 'Personal', required: false, visible: true, description: 'Employee nationality' },
  { id: 'passport_number', name: 'Passport Number', category: 'Personal', required: false, visible: true, description: 'Passport number' },
  { id: 'emergency_contact', name: 'Emergency Contact', category: 'Personal', required: false, visible: true, description: 'Emergency contact' },
]

const DEFAULT_WORKFLOWS: WorkflowConfig[] = [
  { id: 'onboarding', name: 'Employee Onboarding', enabled: true, description: 'New employee onboarding workflow', category: 'Onboarding' },
  { id: 'offboarding', name: 'Employee Offboarding', enabled: true, description: 'Employee exit workflow', category: 'Offboarding' },
  { id: 'contract_renewal', name: 'Contract Renewal', enabled: true, description: 'Contract renewal reminders', category: 'Compliance' },
  { id: 'visa_renewal', name: 'Visa Renewal Alerts', enabled: true, description: 'Visa expiry notifications', category: 'Compliance' },
  { id: 'medical_renewal', name: 'Medical Fitness Renewal', enabled: true, description: 'Medical certificate renewal', category: 'Compliance' },
  { id: 'probation_review', name: 'Probation Review', enabled: true, description: 'Probation completion workflow', category: 'HR' },
  { id: 'leave_approval', name: 'Leave Approval', enabled: true, description: 'Leave request approval', category: 'HR' },
  { id: 'timesheet_approval', name: 'Timesheet Approval', enabled: false, description: 'Weekly timesheet approval', category: 'HR' },
  { id: 'recruitment_pipeline', name: 'Recruitment Pipeline', enabled: true, description: 'Candidate tracking', category: 'Recruitment' },
  { id: 'interview_scheduling', name: 'Interview Scheduling', enabled: true, description: 'Interview automation', category: 'Recruitment' },
]

const DEFAULT_MODULES: ModuleConfig[] = [
  { id: 'employees', name: 'Employee Management', enabled: true, description: 'Core employee records' },
  { id: 'renewals', name: 'Contract Renewals', enabled: true, description: 'Contract renewal tracking' },
  { id: 'compliance', name: 'UAE Compliance', enabled: true, description: 'Visa, EID, medical tracking' },
  { id: 'attendance', name: 'Attendance Tracking', enabled: true, description: 'Time and attendance' },
  { id: 'leave', name: 'Leave Management', enabled: true, description: 'Leave requests and balances' },
  { id: 'recruitment', name: 'Recruitment', enabled: true, description: 'Candidate management' },
  { id: 'documents', name: 'Document Generation', enabled: true, description: 'Employment letters' },
  { id: 'reports', name: 'Reports & Analytics', enabled: false, description: 'HR reports and dashboards' },
]

export const AdminSettings = ({ onClose, token }: AdminSettingsProps) => {
  const [activeTab, setActiveTab] = useState<'fields' | 'workflows' | 'modules' | 'appearance'>('fields')
  const [searchQuery, setSearchQuery] = useState('')
  const [isSaving, setIsSaving] = useState(false)
  const [isLoading, setIsLoading] = useState(true)
  const [saveMessage, setSaveMessage] = useState('')

  // Field configurations
  const [fieldConfigs, setFieldConfigs] = useState<FieldConfig[]>(DEFAULT_FIELDS)

  // Workflow configurations
  const [workflowConfigs, setWorkflowConfigs] = useState<WorkflowConfig[]>(DEFAULT_WORKFLOWS)

  // Module configurations
  const [moduleConfigs, setModuleConfigs] = useState<ModuleConfig[]>(DEFAULT_MODULES)

  // Load settings from backend on mount
  useEffect(() => {
    const loadSettings = async () => {
      try {
        const authToken = token || localStorage.getItem('token')
        if (!authToken) {
          setIsLoading(false)
          return
        }

        const response = await fetch('/api/admin/settings', {
          headers: {
            'Authorization': `Bearer ${authToken}`,
            'Content-Type': 'application/json',
          },
        })

        if (response.ok) {
          const data = await response.json()
          if (data.fields?.length) setFieldConfigs(data.fields)
          if (data.workflows?.length) setWorkflowConfigs(data.workflows)
          if (data.modules?.length) setModuleConfigs(data.modules)
        }
      } catch (error) {
        console.error('Failed to load admin settings:', error)
        // Use defaults on error
      } finally {
        setIsLoading(false)
      }
    }

    loadSettings()
  }, [token])

  // Filter fields by search and category
  const categories = [...new Set(fieldConfigs.map(f => f.category))]
  const [selectedCategory, setSelectedCategory] = useState<string>('all')

  const filteredFields = fieldConfigs.filter(field => {
    const matchesSearch = field.name.toLowerCase().includes(searchQuery.toLowerCase())
    const matchesCategory = selectedCategory === 'all' || field.category === selectedCategory
    return matchesSearch && matchesCategory
  })

  const workflowCategories = [...new Set(workflowConfigs.map(w => w.category))]
  const [selectedWorkflowCategory, setSelectedWorkflowCategory] = useState<string>('all')

  const filteredWorkflows = workflowConfigs.filter(workflow => {
    const matchesSearch = workflow.name.toLowerCase().includes(searchQuery.toLowerCase())
    const matchesCategory = selectedWorkflowCategory === 'all' || workflow.category === selectedWorkflowCategory
    return matchesSearch && matchesCategory
  })

  const handleFieldToggle = (fieldId: string, property: 'required' | 'visible') => {
    setFieldConfigs(prev => prev.map(field => 
      field.id === fieldId 
        ? { ...field, [property]: !field[property] }
        : field
    ))
  }

  const handleWorkflowToggle = (workflowId: string) => {
    setWorkflowConfigs(prev => prev.map(workflow => 
      workflow.id === workflowId 
        ? { ...workflow, enabled: !workflow.enabled }
        : workflow
    ))
  }

  const handleModuleToggle = (moduleId: string) => {
    setModuleConfigs(prev => prev.map(module => 
      module.id === moduleId 
        ? { ...module, enabled: !module.enabled }
        : module
    ))
  }

  const handleSave = async () => {
    setIsSaving(true)
    setSaveMessage('')
    try {
      const authToken = token || localStorage.getItem('token')
      if (!authToken) {
        setSaveMessage('Authentication required')
        setIsSaving(false)
        return
      }

      const response = await fetch('/api/admin/settings', {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${authToken}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          fields: fieldConfigs,
          workflows: workflowConfigs,
          modules: moduleConfigs,
        }),
      })

      if (response.ok) {
        setSaveMessage('Settings saved successfully!')
      } else {
        const errorData = await response.json().catch(() => ({}))
        setSaveMessage(errorData.detail || 'Failed to save settings')
      }
      setTimeout(() => setSaveMessage(''), 3000)
    } catch {
      setSaveMessage('Failed to save settings')
    } finally {
      setIsSaving(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl shadow-xl max-w-4xl w-full max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="bg-primary-50 px-6 py-4 border-b border-primary-200 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-accent-green/10 flex items-center justify-center">
              <svg className="w-6 h-6 text-accent-green" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
            </div>
            <div>
              <h2 className="text-lg font-semibold text-primary-800">Admin Settings</h2>
              <p className="text-sm text-primary-500">Configure fields, workflows, and modules</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-primary-100 rounded-lg transition-colors"
          >
            <svg className="w-5 h-5 text-primary-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Tabs */}
        <div className="border-b border-primary-200 px-6">
          <div className="flex gap-6">
            {[
              { id: 'fields', label: 'Fields', icon: 'M4 6h16M4 12h16M4 18h7' },
              { id: 'workflows', label: 'Workflows', icon: 'M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01' },
              { id: 'modules', label: 'Modules', icon: 'M4 5a1 1 0 011-1h14a1 1 0 011 1v2a1 1 0 01-1 1H5a1 1 0 01-1-1V5zM4 13a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H5a1 1 0 01-1-1v-6zM16 13a1 1 0 011-1h2a1 1 0 011 1v6a1 1 0 01-1 1h-2a1 1 0 01-1-1v-6z' },
              { id: 'appearance', label: 'Appearance', icon: 'M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zm0 0h12a2 2 0 002-2v-4a2 2 0 00-2-2h-2.343M11 7.343l1.657-1.657a2 2 0 012.828 0l2.829 2.829a2 2 0 010 2.828l-8.486 8.485M7 17h.01' },
            ].map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as typeof activeTab)}
                className={`flex items-center gap-2 py-3 px-1 border-b-2 transition-colors ${
                  activeTab === tab.id
                    ? 'border-accent-green text-accent-green font-medium'
                    : 'border-transparent text-primary-500 hover:text-primary-700'
                }`}
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d={tab.icon} />
                </svg>
                {tab.label}
              </button>
            ))}
          </div>
        </div>

        {/* Search Bar */}
        <div className="px-6 py-4 border-b border-primary-100">
          <div className="relative">
            <svg className="w-5 h-5 text-primary-400 absolute left-3 top-1/2 -translate-y-1/2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            <input
              type="text"
              placeholder="Search settings..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-primary-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-accent-green/30 focus:border-accent-green"
            />
          </div>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto max-h-[50vh]">
          {/* Fields Tab */}
          {activeTab === 'fields' && (
            <div>
              {/* Category Filter */}
              <div className="flex gap-2 mb-4 flex-wrap">
                <button
                  onClick={() => setSelectedCategory('all')}
                  className={`px-3 py-1 rounded-full text-sm transition-colors ${
                    selectedCategory === 'all'
                      ? 'bg-accent-green text-white'
                      : 'bg-primary-100 text-primary-600 hover:bg-primary-200'
                  }`}
                >
                  All
                </button>
                {categories.map(category => (
                  <button
                    key={category}
                    onClick={() => setSelectedCategory(category)}
                    className={`px-3 py-1 rounded-full text-sm transition-colors ${
                      selectedCategory === category
                        ? 'bg-accent-green text-white'
                        : 'bg-primary-100 text-primary-600 hover:bg-primary-200'
                    }`}
                  >
                    {category}
                  </button>
                ))}
              </div>

              {/* Fields List */}
              <div className="space-y-3">
                {filteredFields.map(field => (
                  <div
                    key={field.id}
                    className="flex items-center justify-between p-4 bg-primary-50 rounded-lg border border-primary-100"
                  >
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <span className="font-medium text-primary-800">{field.name}</span>
                        <span className="text-xs px-2 py-0.5 bg-primary-200 text-primary-600 rounded-full">{field.category}</span>
                      </div>
                      <p className="text-sm text-primary-500 mt-1">{field.description}</p>
                    </div>
                    <div className="flex items-center gap-4">
                      {/* Required Toggle */}
                      <div className="flex items-center gap-2">
                        <span className="text-xs text-primary-500">Required</span>
                        <button
                          onClick={() => handleFieldToggle(field.id, 'required')}
                          className={`w-10 h-6 rounded-full transition-colors ${
                            field.required ? 'bg-accent-green' : 'bg-primary-200'
                          }`}
                        >
                          <div className={`w-4 h-4 rounded-full bg-white shadow transition-transform mx-1 ${
                            field.required ? 'translate-x-4' : ''
                          }`} />
                        </button>
                      </div>
                      {/* Visible Toggle */}
                      <div className="flex items-center gap-2">
                        <span className="text-xs text-primary-500">Visible</span>
                        <button
                          onClick={() => handleFieldToggle(field.id, 'visible')}
                          className={`w-10 h-6 rounded-full transition-colors ${
                            field.visible ? 'bg-accent-green' : 'bg-primary-200'
                          }`}
                        >
                          <div className={`w-4 h-4 rounded-full bg-white shadow transition-transform mx-1 ${
                            field.visible ? 'translate-x-4' : ''
                          }`} />
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Workflows Tab */}
          {activeTab === 'workflows' && (
            <div>
              {/* Category Filter */}
              <div className="flex gap-2 mb-4 flex-wrap">
                <button
                  onClick={() => setSelectedWorkflowCategory('all')}
                  className={`px-3 py-1 rounded-full text-sm transition-colors ${
                    selectedWorkflowCategory === 'all'
                      ? 'bg-accent-green text-white'
                      : 'bg-primary-100 text-primary-600 hover:bg-primary-200'
                  }`}
                >
                  All
                </button>
                {workflowCategories.map(category => (
                  <button
                    key={category}
                    onClick={() => setSelectedWorkflowCategory(category)}
                    className={`px-3 py-1 rounded-full text-sm transition-colors ${
                      selectedWorkflowCategory === category
                        ? 'bg-accent-green text-white'
                        : 'bg-primary-100 text-primary-600 hover:bg-primary-200'
                    }`}
                  >
                    {category}
                  </button>
                ))}
              </div>

              {/* Workflows List */}
              <div className="space-y-3">
                {filteredWorkflows.map(workflow => (
                  <div
                    key={workflow.id}
                    className="flex items-center justify-between p-4 bg-primary-50 rounded-lg border border-primary-100"
                  >
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <span className="font-medium text-primary-800">{workflow.name}</span>
                        <span className="text-xs px-2 py-0.5 bg-primary-200 text-primary-600 rounded-full">{workflow.category}</span>
                      </div>
                      <p className="text-sm text-primary-500 mt-1">{workflow.description}</p>
                    </div>
                    <button
                      onClick={() => handleWorkflowToggle(workflow.id)}
                      className={`w-12 h-7 rounded-full transition-colors ${
                        workflow.enabled ? 'bg-accent-green' : 'bg-primary-200'
                      }`}
                    >
                      <div className={`w-5 h-5 rounded-full bg-white shadow transition-transform mx-1 ${
                        workflow.enabled ? 'translate-x-5' : ''
                      }`} />
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Modules Tab */}
          {activeTab === 'modules' && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {moduleConfigs.map(module => (
                <div
                  key={module.id}
                  className={`p-4 rounded-xl border-2 transition-all ${
                    module.enabled
                      ? 'border-accent-green bg-accent-green/5'
                      : 'border-primary-200 bg-primary-50'
                  }`}
                >
                  <div className="flex items-start justify-between">
                    <div>
                      <h3 className="font-semibold text-primary-800">{module.name}</h3>
                      <p className="text-sm text-primary-500 mt-1">{module.description}</p>
                    </div>
                    <button
                      onClick={() => handleModuleToggle(module.id)}
                      className={`w-12 h-7 rounded-full transition-colors flex-shrink-0 ${
                        module.enabled ? 'bg-accent-green' : 'bg-primary-300'
                      }`}
                    >
                      <div className={`w-5 h-5 rounded-full bg-white shadow transition-transform mx-1 ${
                        module.enabled ? 'translate-x-5' : ''
                      }`} />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Appearance Tab */}
          {activeTab === 'appearance' && (
            <div className="space-y-6">
              <div className="p-4 bg-primary-50 rounded-lg border border-primary-100">
                <h3 className="font-semibold text-primary-800 mb-3">Color Theme</h3>
                <div className="flex gap-4">
                  <div className="text-center">
                    <div className="w-12 h-12 rounded-lg bg-white border-2 border-accent-green mb-2"></div>
                    <span className="text-xs text-primary-500">Background</span>
                  </div>
                  <div className="text-center">
                    <div className="w-12 h-12 rounded-lg bg-primary-800 mb-2"></div>
                    <span className="text-xs text-primary-500">Text</span>
                  </div>
                  <div className="text-center">
                    <div className="w-12 h-12 rounded-lg bg-accent-green mb-2"></div>
                    <span className="text-xs text-primary-500">Accent</span>
                  </div>
                  <div className="text-center">
                    <div className="w-12 h-12 rounded-lg bg-accent-amber mb-2"></div>
                    <span className="text-xs text-primary-500">Warning</span>
                  </div>
                  <div className="text-center">
                    <div className="w-12 h-12 rounded-lg bg-accent-red mb-2"></div>
                    <span className="text-xs text-primary-500">Error</span>
                  </div>
                </div>
              </div>

              <div className="p-4 bg-primary-50 rounded-lg border border-primary-100">
                <h3 className="font-semibold text-primary-800 mb-3">Display Options</h3>
                <div className="space-y-3">
                  <label className="flex items-center justify-between">
                    <span className="text-primary-600">Compact Mode</span>
                    <button className="w-10 h-6 rounded-full bg-primary-200">
                      <div className="w-4 h-4 rounded-full bg-white shadow mx-1" />
                    </button>
                  </label>
                  <label className="flex items-center justify-between">
                    <span className="text-primary-600">Show Tooltips</span>
                    <button className="w-10 h-6 rounded-full bg-accent-green">
                      <div className="w-4 h-4 rounded-full bg-white shadow mx-1 translate-x-4" />
                    </button>
                  </label>
                  <label className="flex items-center justify-between">
                    <span className="text-primary-600">Animation Effects</span>
                    <button className="w-10 h-6 rounded-full bg-accent-green">
                      <div className="w-4 h-4 rounded-full bg-white shadow mx-1 translate-x-4" />
                    </button>
                  </label>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-4 border-t border-primary-200 bg-primary-50 flex items-center justify-between">
          <div>
            {saveMessage && (
              <span className={`text-sm ${saveMessage.includes('success') ? 'text-accent-green' : 'text-accent-red'}`}>
                {saveMessage}
              </span>
            )}
          </div>
          <div className="flex gap-3">
            <button
              onClick={onClose}
              className="px-4 py-2 text-primary-600 hover:bg-primary-100 rounded-lg transition-colors"
            >
              Cancel
            </button>
            <button
              onClick={handleSave}
              disabled={isSaving}
              className="px-6 py-2 bg-accent-green text-white rounded-lg hover:bg-accent-green/90 transition-colors disabled:opacity-50 flex items-center gap-2"
            >
              {isSaving ? (
                <>
                  <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                  Saving...
                </>
              ) : (
                'Save Changes'
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
