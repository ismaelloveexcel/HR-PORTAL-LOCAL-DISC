import { useState, useEffect } from 'react'
import { useRecruitment } from '../hooks/useRecruitment'
import { useAuthContext } from '../contexts/AuthContext'
import { exportCandidatesToCSV, exportRecruitmentRequestsToCSV } from '../utils/exportToCSV'
import { fetchWithAuth, API_BASE } from '../utils/api'

/**
 * RecruitmentModule - Comprehensive recruitment management interface
 * 
 * Features:
 * - Stats dashboard (positions, candidates, interview, hired)
 * - Open positions list with CSV export
 * - Kanban pipeline (Applied → Screening → Interview → Offer → Hired)
 * - Candidate screening table with filters & search
 * - New recruitment request modal
 * - Integration with CandidatePass and ManagerPass
 */
export function RecruitmentModule() {
  const { user } = useAuthContext()
  const {
    recruitmentStats,
    recruitmentRequests,
    pipelineCounts,
    candidatesList,
    candidateSearchQuery,
    candidateStatusFilter,
    candidateSourceFilter,
    loading,
    fetchRecruitmentData,
    fetchRecruitmentCandidates,
    setCandidateSearchQuery,
    setCandidateStatusFilter,
    setCandidateSourceFilter,
  } = useRecruitment(user)

  const [showNewRequestModal, setShowNewRequestModal] = useState(false)
  const [newRequestForm, setNewRequestForm] = useState({
    position_title: '',
    department: 'Engineering / R&D',
    employment_type: 'Full-time',
    salary_range_min: '',
    salary_range_max: '',
    headcount: '1',
    job_description: '',
    requirements: ''
  })

  useEffect(() => {
    if (user && (user.role === 'admin' || user.role === 'hr')) {
      fetchRecruitmentData()
      fetchRecruitmentCandidates()
    }
  }, [user, fetchRecruitmentData, fetchRecruitmentCandidates])

  const handleCreateRecruitmentRequest = async () => {
    if (!user) return
    try {
      const payload = {
        position_title: newRequestForm.position_title,
        department: newRequestForm.department,
        employment_type: newRequestForm.employment_type,
        salary_range_min: newRequestForm.salary_range_min ? parseFloat(newRequestForm.salary_range_min) : null,
        salary_range_max: newRequestForm.salary_range_max ? parseFloat(newRequestForm.salary_range_max) : null,
        headcount: parseInt(newRequestForm.headcount) || 1,
        job_description: newRequestForm.job_description || null,
        requirements: newRequestForm.requirements || null
      }
      const res = await fetchWithAuth(`${API_BASE}/recruitment/requests`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
        token: user.token,
        role: user.role
      })
      if (res.ok) {
        setShowNewRequestModal(false)
        setNewRequestForm({
          position_title: '',
          department: 'Engineering / R&D',
          employment_type: 'Full-time',
          salary_range_min: '',
          salary_range_max: '',
          headcount: '1',
          job_description: '',
          requirements: ''
        })
        await fetchRecruitmentData()
      }
    } catch (err) {
      console.error('Failed to create recruitment request:', err)
    }
  }

  // Handle navigation to ManagerPass (simplified for extracted module)
  const handleViewManagerPass = (positionId: number, managerId: string) => {
    // TODO: Integrate with ManagerPass navigation when routing is ready
    alert(`Manager Pass for Position ${positionId}, Manager ${managerId}`)
  }

  if (!user || (user.role !== 'admin' && user.role !== 'hr')) {
    return (
      <div className="min-h-screen bg-primary-50 flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-primary-800 mb-2">Access Restricted</h2>
          <p className="text-primary-600">This module is only available to HR and Admin users.</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-primary-50 p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="bg-white rounded-xl shadow p-6 border border-primary-200">
          <h1 className="text-2xl font-bold text-primary-800">Recruitment Management</h1>
          <p className="text-primary-600 mt-1">Manage positions, candidates, and hiring pipeline</p>
        </div>

        {/* Stats Dashboard */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-white rounded-xl shadow p-6 border border-primary-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-primary-600">Active Positions</p>
                <p className="text-3xl font-semibold text-primary-800">
                  {recruitmentStats?.active_positions ?? recruitmentRequests.length}
                </p>
              </div>
              <div className="p-3 bg-primary-50 rounded-full">
                <svg className="w-6 h-6 text-accent-green" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                </svg>
              </div>
            </div>
          </div>
          
          <div className="bg-white rounded-xl shadow p-6 border border-primary-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-primary-600">Total Candidates</p>
                <p className="text-3xl font-semibold text-primary-800">
                  {recruitmentStats?.total_candidates ?? 0}
                </p>
              </div>
              <div className="p-3 bg-primary-50 rounded-full">
                <svg className="w-6 h-6 text-accent-green" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
              </div>
            </div>
          </div>
          
          <div className="bg-white rounded-xl shadow p-6 border border-primary-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-primary-600">In Interview</p>
                <p className="text-3xl font-semibold text-primary-800">
                  {recruitmentStats?.in_interview ?? pipelineCounts?.interview ?? 0}
                </p>
              </div>
              <div className="p-3 bg-primary-50 rounded-full">
                <svg className="w-6 h-6 text-accent-green" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
              </div>
            </div>
          </div>
          
          <div className="bg-white rounded-xl shadow p-6 border border-primary-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-primary-600">Hired (30 days)</p>
                <p className="text-3xl font-semibold text-primary-800">
                  {recruitmentStats?.hired_30_days ?? pipelineCounts?.hired ?? 0}
                </p>
              </div>
              <div className="p-3 bg-primary-50 rounded-full">
                <svg className="w-6 h-6 text-accent-green" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
            </div>
          </div>
        </div>

        {/* Open Positions */}
        {recruitmentRequests.length > 0 && (
          <div className="bg-white rounded-card shadow-card p-6 border border-primary-200">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-primary-800 flex items-center gap-2">
                <svg className="w-5 h-5 text-accent-green" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                </svg>
                Open Positions ({recruitmentRequests.length})
              </h2>
              <button
                onClick={() => exportRecruitmentRequestsToCSV(recruitmentRequests)}
                className="px-3 py-1.5 bg-accent-green text-white text-sm rounded-lg hover:bg-accent-green/90 transition-colors flex items-center gap-2"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                Export
              </button>
            </div>
            <div className="grid gap-4">
              {recruitmentRequests.map((req: any) => (
                <div key={req.id} className="border border-primary-200 rounded-lg p-4 hover:border-accent-green transition-colors bg-white">
                  <div className="flex items-start justify-between">
                    <div>
                      <h3 className="font-semibold text-primary-800">{req.position_title}</h3>
                      <p className="text-sm text-primary-600">{req.department} • {req.employment_type}</p>
                      <div className="flex items-center gap-2 mt-2">
                        <span className={`px-2 py-1 text-xs rounded-full border ${
                          req.status === 'open' ? 'border-accent-green text-accent-green bg-accent-green/5' :
                          req.status === 'pending_approval' ? 'border-amber-400 text-amber-600 bg-amber-50' :
                          'border-primary-300 text-primary-600 bg-primary-50'
                        }`}>
                          {req.status?.replace('_', ' ')}
                        </span>
                        <span className="text-xs text-primary-500">{req.request_number}</span>
                      </div>
                    </div>
                    <div className="text-right flex flex-col items-end gap-2">
                      <div>
                        <p className="text-sm font-medium text-primary-700">Headcount: {req.headcount || 1}</p>
                        {req.salary_range_min && req.salary_range_max && (
                          <p className="text-xs text-primary-500">
                            AED {req.salary_range_min.toLocaleString()} - {req.salary_range_max.toLocaleString()}
                          </p>
                        )}
                      </div>
                      <button
                        onClick={() => handleViewManagerPass(req.id, req.hiring_manager_id || user.employee_id)}
                        className="px-3 py-1.5 bg-accent-green text-white text-xs font-medium rounded-lg hover:bg-accent-green/90 transition-colors flex items-center gap-1"
                      >
                        <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 5v2m0 4v2m0 4v2M5 5a2 2 0 00-2 2v3a2 2 0 110 4v3a2 2 0 002 2h14a2 2 0 002-2v-3a2 2 0 110-4V7a2 2 0 00-2-2H5z" />
                        </svg>
                        Manager Pass
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Kanban Pipeline */}
        <div className="bg-white rounded-card shadow-card p-6 border border-primary-200">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-primary-800 flex items-center gap-2">
              <svg className="w-5 h-5 text-accent-green" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
              </svg>
              Candidate Pipeline
            </h2>
            <button
              onClick={() => exportCandidatesToCSV(candidatesList)}
              className="px-3 py-1.5 bg-accent-green text-white text-sm rounded-lg hover:bg-accent-green/90 transition-colors flex items-center gap-2"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              Export
            </button>
          </div>
          
          {/* Pipeline Stages */}
          <div className="grid grid-cols-5 gap-4">
            {[
              { key: 'applied', label: 'Applied' },
              { key: 'screening', label: 'Screening' },
              { key: 'interview', label: 'Interview' },
              { key: 'offer', label: 'Offer' },
              { key: 'hired', label: 'Hired' }
            ].map((stage) => (
              <div key={stage.key} className="bg-primary-50 rounded-lg p-4 min-h-[200px] border border-primary-200">
                <div className="flex items-center justify-between mb-3">
                  <h3 className="font-medium text-primary-700">{stage.label}</h3>
                  <span className="bg-primary-100 text-primary-800 text-xs px-2 py-1 rounded-full border border-primary-300">
                    {pipelineCounts?.[stage.key as keyof typeof pipelineCounts] ?? 0}
                  </span>
                </div>
                <div className="space-y-2">
                  {(pipelineCounts?.[stage.key as keyof typeof pipelineCounts] ?? 0) === 0 && (
                    <div className="text-center py-8 text-primary-500 text-sm">
                      <p>No candidates</p>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Candidates Screening Table */}
        {candidatesList.length > 0 && (
          <div className="bg-white rounded-2xl shadow-card overflow-hidden border border-primary-200">
            {/* Header with Search and Filters */}
            <div className="px-8 py-6 border-b border-primary-200 bg-primary-50">
              <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
                <div>
                  <h2 className="text-xl font-bold text-primary-800">Candidate Screening</h2>
                  <p className="text-sm text-primary-600 mt-1">{candidatesList.length} candidates in pipeline</p>
                </div>
                <div className="flex flex-wrap items-center gap-3">
                  <div className="relative">
                    <svg className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-primary-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                    </svg>
                    <input
                      type="text"
                      placeholder="Search candidates..."
                      value={candidateSearchQuery}
                      onChange={(e) => setCandidateSearchQuery(e.target.value)}
                      className="w-64 pl-10 pr-4 py-2.5 bg-white border border-primary-300 rounded-xl text-sm focus:ring-2 focus:ring-accent-green focus:border-accent-green shadow-sm"
                    />
                  </div>
                  <select 
                    value={candidateStatusFilter}
                    onChange={(e) => setCandidateStatusFilter(e.target.value)}
                    className="px-4 py-2.5 bg-white border border-primary-300 rounded-xl text-sm text-primary-700 focus:ring-2 focus:ring-accent-green shadow-sm"
                  >
                    <option value="">All Stages</option>
                    <option value="applied">Applied</option>
                    <option value="screening">Screening</option>
                    <option value="interview">Interview</option>
                    <option value="offer">Offer</option>
                    <option value="hired">Hired</option>
                  </select>
                  <select 
                    value={candidateSourceFilter}
                    onChange={(e) => setCandidateSourceFilter(e.target.value)}
                    className="px-4 py-2.5 bg-white border border-primary-300 rounded-xl text-sm text-primary-700 focus:ring-2 focus:ring-accent-green shadow-sm"
                  >
                    <option value="">All Sources</option>
                    <option value="LinkedIn">LinkedIn</option>
                    <option value="Indeed">Indeed</option>
                    <option value="Referral">Referral</option>
                    <option value="Direct">Direct Application</option>
                    <option value="Agency">Agency</option>
                  </select>
                </div>
              </div>
            </div>

            {/* Candidate Table - Simplified for Phase 2 */}
            <div className="p-6">
              <p className="text-sm text-primary-600 text-center py-8">
                Full candidate screening table will be integrated in next phase.
                <br />
                Currently showing {candidatesList.filter((c: any) => {
                  const searchLower = candidateSearchQuery.toLowerCase()
                  const matchesSearch = !candidateSearchQuery || 
                    c.full_name?.toLowerCase().includes(searchLower) ||
                    c.email?.toLowerCase().includes(searchLower)
                  const matchesStatus = !candidateStatusFilter || c.stage === candidateStatusFilter
                  const matchesSource = !candidateSourceFilter || c.source === candidateSourceFilter
                  return matchesSearch && matchesStatus && matchesSource
                }).length} filtered candidates.
              </p>
            </div>
          </div>
        )}

        {/* Quick Actions */}
        <div className="bg-white rounded-card shadow-card p-6 border border-primary-200">
          <h2 className="text-lg font-semibold text-primary-800 mb-4">Quick Actions</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <button 
              onClick={() => setShowNewRequestModal(true)} 
              className="flex items-center gap-3 p-4 bg-primary-50 hover:bg-accent-green/10 rounded-lg transition-colors border border-primary-200"
            >
              <div className="p-2 bg-accent-green/10 rounded-lg">
                <svg className="w-5 h-5 text-accent-green" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                </svg>
              </div>
              <span className="font-medium text-primary-700">New Position</span>
            </button>
          </div>
        </div>

        {/* New Request Modal */}
        {showNewRequestModal && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-card shadow-card p-8 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-semibold text-primary-800">Create New Position</h2>
                <button onClick={() => setShowNewRequestModal(false)} className="text-primary-300 hover:text-primary-600">
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
              <form onSubmit={(e) => { e.preventDefault(); handleCreateRecruitmentRequest(); }} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-primary-700 mb-1">Position Title *</label>
                  <input
                    type="text"
                    value={newRequestForm.position_title}
                    onChange={(e) => setNewRequestForm(prev => ({ ...prev, position_title: e.target.value }))}
                    className="w-full px-4 py-2 border border-primary-200 rounded-lg focus:ring-2 focus:ring-accent-green focus:border-accent-green"
                    placeholder="e.g., Thermodynamics Engineer"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-primary-700 mb-1">Department *</label>
                  <input
                    type="text"
                    value={newRequestForm.department}
                    onChange={(e) => setNewRequestForm(prev => ({ ...prev, department: e.target.value }))}
                    className="w-full px-4 py-2 border border-primary-200 rounded-lg focus:ring-2 focus:ring-accent-green focus:border-accent-green"
                    placeholder="e.g., Engineering / R&D"
                    required
                  />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-primary-700 mb-1">Employment Type</label>
                    <select
                      value={newRequestForm.employment_type}
                      onChange={(e) => setNewRequestForm(prev => ({ ...prev, employment_type: e.target.value }))}
                      className="w-full px-4 py-2 border border-primary-200 rounded-lg focus:ring-2 focus:ring-accent-green focus:border-accent-green"
                    >
                      <option value="Full-time">Full-time</option>
                      <option value="Part-time">Part-time</option>
                      <option value="Contract">Contract</option>
                      <option value="Internship">Internship</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-primary-700 mb-1">Headcount</label>
                    <input
                      type="number"
                      value={newRequestForm.headcount}
                      onChange={(e) => setNewRequestForm(prev => ({ ...prev, headcount: e.target.value }))}
                      className="w-full px-4 py-2 border border-primary-200 rounded-lg focus:ring-2 focus:ring-accent-green focus:border-accent-green"
                      min="1"
                    />
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-primary-700 mb-1">Salary Range Min (AED)</label>
                    <input
                      type="number"
                      value={newRequestForm.salary_range_min}
                      onChange={(e) => setNewRequestForm(prev => ({ ...prev, salary_range_min: e.target.value }))}
                      className="w-full px-4 py-2 border border-primary-200 rounded-lg focus:ring-2 focus:ring-accent-green focus:border-accent-green"
                      placeholder="e.g., 15000"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-primary-700 mb-1">Salary Range Max (AED)</label>
                    <input
                      type="number"
                      value={newRequestForm.salary_range_max}
                      onChange={(e) => setNewRequestForm(prev => ({ ...prev, salary_range_max: e.target.value }))}
                      className="w-full px-4 py-2 border border-primary-200 rounded-lg focus:ring-2 focus:ring-accent-green focus:border-accent-green"
                      placeholder="e.g., 25000"
                    />
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-primary-700 mb-1">Job Description</label>
                  <textarea
                    value={newRequestForm.job_description}
                    onChange={(e) => setNewRequestForm(prev => ({ ...prev, job_description: e.target.value }))}
                    className="w-full px-4 py-2 border border-primary-200 rounded-lg focus:ring-2 focus:ring-accent-green focus:border-accent-green min-h-[100px]"
                    placeholder="Enter job description..."
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-primary-700 mb-1">Requirements</label>
                  <textarea
                    value={newRequestForm.requirements}
                    onChange={(e) => setNewRequestForm(prev => ({ ...prev, requirements: e.target.value }))}
                    className="w-full px-4 py-2 border border-primary-200 rounded-lg focus:ring-2 focus:ring-accent-green focus:border-accent-green min-h-[100px]"
                    placeholder="Enter requirements..."
                  />
                </div>
                <div className="flex justify-end gap-3 pt-4">
                  <button 
                    type="button" 
                    onClick={() => setShowNewRequestModal(false)} 
                    className="px-6 py-2 border border-primary-200 text-primary-700 rounded-lg hover:bg-primary-50"
                  >
                    Cancel
                  </button>
                  <button 
                    type="submit" 
                    disabled={loading || !newRequestForm.position_title} 
                    className="px-6 py-2 bg-accent-green text-white rounded-lg hover:bg-accent-green/90 disabled:opacity-50"
                  >
                    {loading ? 'Creating...' : 'Create Position'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
