import React, { useState, useEffect } from 'react'

interface PerformanceCycle {
  id: number
  name: string
  cycle_type: string
  start_date: string
  end_date: string
  self_assessment_deadline: string | null
  manager_review_deadline: string | null
  status: string
  created_at: string
  review_count: number
}

interface PerformanceReview {
  id: number
  cycle_id: number
  cycle_name: string
  employee_id: number
  employee_name: string
  reviewer_id: number | null
  reviewer_name: string | null
  status: string
  self_assessment_submitted: boolean
  manager_review_submitted: boolean
  overall_rating: number | null
  rating_label: string | null
  ratings: CompetencyRating[]
}

interface CompetencyRating {
  id: number
  competency_name: string
  competency_category: string
  weight: number
  self_rating: number | null
  self_comments: string | null
  manager_rating: number | null
  manager_comments: string | null
}

interface PerformanceStats {
  total_reviews: number
  completed_reviews: number
  pending_self_assessment: number
  pending_manager_review: number
  completion_rate: number
}

interface PerformanceProps {
  user: { employee_id: string; name: string; role: string; token: string }
  fetchWithAuth: (url: string, options?: RequestInit) => Promise<Response>
}

const API_BASE = '/api'

const RATING_LABELS: Record<number, string> = {
  5: 'Outstanding',
  4: 'Exceeds Expectations',
  3: 'Meets Expectations',
  2: 'Developing',
  1: 'Needs Improvement'
}

const CYCLE_TYPES = ['Annual', 'Mid-Year', 'Quarterly', 'Probation']
const STATUS_COLORS: Record<string, string> = {
  draft: 'bg-slate-100 text-slate-600',
  active: 'bg-emerald-100 text-emerald-700',
  completed: 'bg-blue-100 text-blue-700',
  pending: 'bg-amber-100 text-amber-700',
  in_progress: 'bg-blue-100 text-blue-700',
  closed: 'bg-slate-200 text-slate-600'
}

export function Performance({ user, fetchWithAuth }: PerformanceProps) {
  const [activeTab, setActiveTab] = useState<'cycles' | 'my-reviews' | 'team-reviews'>('cycles')
  const [cycles, setCycles] = useState<PerformanceCycle[]>([])
  const [reviews, setReviews] = useState<PerformanceReview[]>([])
  const [myReviews, setMyReviews] = useState<PerformanceReview[]>([])
  const [teamReviews, setTeamReviews] = useState<PerformanceReview[]>([])
  const [stats, setStats] = useState<PerformanceStats | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  
  const [showCycleModal, setShowCycleModal] = useState(false)
  const [editingCycle, setEditingCycle] = useState<PerformanceCycle | null>(null)
  const [cycleForm, setCycleForm] = useState({
    name: '',
    cycle_type: 'Annual',
    start_date: '',
    end_date: '',
    self_assessment_deadline: '',
    manager_review_deadline: ''
  })
  
  const [showReviewModal, setShowReviewModal] = useState(false)
  const [selectedReview, setSelectedReview] = useState<PerformanceReview | null>(null)
  const [assessmentForm, setAssessmentForm] = useState({
    achievements: '',
    challenges: '',
    goals_next_period: '',
    training_needs: '',
    overall_comments: '',
    ratings: {} as Record<string, { rating: number; comments: string }>
  })
  
  const [managerForm, setManagerForm] = useState({
    achievements: '',
    areas_improvement: '',
    recommendations: '',
    overall_comments: '',
    ratings: {} as Record<string, { rating: number; comments: string }>
  })

  const [selectedCycle, setSelectedCycle] = useState<PerformanceCycle | null>(null)
  const [showBulkCreateModal, setShowBulkCreateModal] = useState(false)
  const [bulkEmployeeIds, setBulkEmployeeIds] = useState<string>('')

  const isAdmin = user.role === 'admin' || user.role === 'hr'

  useEffect(() => {
    if (activeTab === 'cycles') {
      fetchCycles()
    } else if (activeTab === 'my-reviews') {
      fetchMyReviews()
    } else if (activeTab === 'team-reviews') {
      fetchTeamReviews()
    }
  }, [activeTab])

  const fetchCycles = async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await fetchWithAuth(`${API_BASE}/performance/cycles`)
      if (!res.ok) throw new Error('Failed to fetch cycles')
      const data = await res.json()
      setCycles(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch cycles')
    } finally {
      setLoading(false)
    }
  }

  const fetchMyReviews = async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await fetchWithAuth(`${API_BASE}/performance/my-reviews`)
      if (!res.ok) throw new Error('Failed to fetch reviews')
      const data = await res.json()
      setMyReviews(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch reviews')
    } finally {
      setLoading(false)
    }
  }

  const fetchTeamReviews = async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await fetchWithAuth(`${API_BASE}/performance/team-reviews`)
      if (!res.ok) throw new Error('Failed to fetch team reviews')
      const data = await res.json()
      setTeamReviews(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch team reviews')
    } finally {
      setLoading(false)
    }
  }

  const fetchCycleStats = async (cycleId: number) => {
    try {
      const res = await fetchWithAuth(`${API_BASE}/performance/cycles/${cycleId}/stats`)
      if (res.ok) {
        const data = await res.json()
        setStats(data)
      }
    } catch (err) {
      console.error('Failed to fetch stats:', err)
    }
  }

  const openCycleModal = (cycle?: PerformanceCycle) => {
    if (cycle) {
      setEditingCycle(cycle)
      setCycleForm({
        name: cycle.name,
        cycle_type: cycle.cycle_type,
        start_date: cycle.start_date,
        end_date: cycle.end_date,
        self_assessment_deadline: cycle.self_assessment_deadline || '',
        manager_review_deadline: cycle.manager_review_deadline || ''
      })
    } else {
      setEditingCycle(null)
      setCycleForm({
        name: '',
        cycle_type: 'Annual',
        start_date: '',
        end_date: '',
        self_assessment_deadline: '',
        manager_review_deadline: ''
      })
    }
    setShowCycleModal(true)
  }

  const handleSaveCycle = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    
    try {
      const payload = {
        ...cycleForm,
        self_assessment_deadline: cycleForm.self_assessment_deadline || null,
        manager_review_deadline: cycleForm.manager_review_deadline || null
      }
      
      const url = editingCycle 
        ? `${API_BASE}/performance/cycles/${editingCycle.id}`
        : `${API_BASE}/performance/cycles`
      const method = editingCycle ? 'PUT' : 'POST'
      
      const res = await fetchWithAuth(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      })
      
      if (!res.ok) {
        const data = await res.json()
        throw new Error(data.detail || 'Failed to save cycle')
      }
      
      setShowCycleModal(false)
      fetchCycles()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save cycle')
    } finally {
      setLoading(false)
    }
  }

  const openReviewModal = async (review: PerformanceReview) => {
    setSelectedReview(review)
    
    const ratingsMap: Record<string, { rating: number; comments: string }> = {}
    review.ratings.forEach(r => {
      ratingsMap[r.competency_name] = {
        rating: r.self_rating || 3,
        comments: r.self_comments || ''
      }
    })
    
    setAssessmentForm({
      achievements: '',
      challenges: '',
      goals_next_period: '',
      training_needs: '',
      overall_comments: '',
      ratings: ratingsMap
    })
    
    const managerRatingsMap: Record<string, { rating: number; comments: string }> = {}
    review.ratings.forEach(r => {
      managerRatingsMap[r.competency_name] = {
        rating: r.manager_rating || 3,
        comments: r.manager_comments || ''
      }
    })
    
    setManagerForm({
      achievements: '',
      areas_improvement: '',
      recommendations: '',
      overall_comments: '',
      ratings: managerRatingsMap
    })
    
    setShowReviewModal(true)
  }

  const handleSubmitSelfAssessment = async () => {
    if (!selectedReview) return
    setLoading(true)
    setError(null)
    
    try {
      const payload = {
        self_achievements: assessmentForm.achievements,
        self_challenges: assessmentForm.challenges,
        self_goals_next_period: assessmentForm.goals_next_period,
        self_training_needs: assessmentForm.training_needs,
        self_overall_comments: assessmentForm.overall_comments,
        ratings: Object.entries(assessmentForm.ratings).map(([name, data]) => ({
          competency_name: name,
          self_rating: (data as { rating: number; comments: string }).rating,
          self_comments: (data as { rating: number; comments: string }).comments
        }))
      }
      
      const res = await fetchWithAuth(`${API_BASE}/performance/reviews/${selectedReview.id}/self-assessment`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      })
      
      if (!res.ok) {
        const data = await res.json()
        throw new Error(data.detail || 'Failed to submit assessment')
      }
      
      setShowReviewModal(false)
      fetchMyReviews()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to submit assessment')
    } finally {
      setLoading(false)
    }
  }

  const handleSubmitManagerReview = async () => {
    if (!selectedReview) return
    setLoading(true)
    setError(null)
    
    try {
      const payload = {
        manager_achievements: managerForm.achievements,
        manager_areas_improvement: managerForm.areas_improvement,
        manager_recommendations: managerForm.recommendations,
        manager_overall_comments: managerForm.overall_comments,
        ratings: Object.entries(managerForm.ratings).map(([name, data]) => ({
          competency_name: name,
          manager_rating: (data as { rating: number; comments: string }).rating,
          manager_comments: (data as { rating: number; comments: string }).comments
        }))
      }
      
      const res = await fetchWithAuth(`${API_BASE}/performance/reviews/${selectedReview.id}/manager-review`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      })
      
      if (!res.ok) {
        const data = await res.json()
        throw new Error(data.detail || 'Failed to submit review')
      }
      
      setShowReviewModal(false)
      fetchTeamReviews()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to submit review')
    } finally {
      setLoading(false)
    }
  }

  const handleBulkCreateReviews = async () => {
    if (!selectedCycle) return
    setLoading(true)
    setError(null)
    
    try {
      const employeeIds = bulkEmployeeIds.split(',').map(id => parseInt(id.trim())).filter(id => !isNaN(id))
      
      const res = await fetchWithAuth(`${API_BASE}/performance/reviews/bulk`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          cycle_id: selectedCycle.id,
          employee_ids: employeeIds
        })
      })
      
      if (!res.ok) {
        const data = await res.json()
        throw new Error(data.detail || 'Failed to create reviews')
      }
      
      const result = await res.json()
      setShowBulkCreateModal(false)
      setBulkEmployeeIds('')
      alert(`Created ${result.created} reviews`)
      fetchCycles()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create reviews')
    } finally {
      setLoading(false)
    }
  }

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString('en-GB', {
      day: '2-digit',
      month: 'short',
      year: 'numeric'
    })
  }

  const renderRatingStars = (rating: number, onChange?: (value: number) => void) => {
    return (
      <div className="flex gap-1">
        {[1, 2, 3, 4, 5].map((star) => (
          <button
            key={star}
            type="button"
            onClick={() => onChange?.(star)}
            disabled={!onChange}
            className={`text-xl transition-colors ${
              star <= rating 
                ? 'text-amber-400' 
                : 'text-slate-300'
            } ${onChange ? 'hover:text-amber-500 cursor-pointer' : 'cursor-default'}`}
          >
            ★
          </button>
        ))}
        <span className="ml-2 text-sm text-slate-500">
          {RATING_LABELS[rating] || ''}
        </span>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-slate-100 p-6">
      <div className="max-w-7xl mx-auto">
        <div className="bg-white/80 backdrop-blur-md rounded-3xl shadow-lg shadow-slate-200/50 border border-white/60 p-8 mb-6">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h1 className="text-2xl font-semibold text-slate-800">Growth & Appraisals</h1>
              <p className="text-slate-500 mt-1">Manage review cycles, self-assessments, and team evaluations</p>
            </div>
            {isAdmin && (
              <button
                onClick={() => openCycleModal()}
                className="px-5 py-2.5 bg-emerald-500 text-white rounded-xl hover:bg-emerald-600 transition-colors font-medium flex items-center gap-2 shadow-sm"
              >
                <span className="text-lg">+</span>
                New Cycle
              </button>
            )}
          </div>

          <div className="flex gap-2 border-b border-slate-200">
            <button
              onClick={() => setActiveTab('cycles')}
              className={`px-4 py-3 font-medium transition-colors relative ${
                activeTab === 'cycles'
                  ? 'text-emerald-600'
                  : 'text-slate-500 hover:text-slate-700'
              }`}
            >
              Review Cycles
              {activeTab === 'cycles' && (
                <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-emerald-500 rounded-full" />
              )}
            </button>
            <button
              onClick={() => setActiveTab('my-reviews')}
              className={`px-4 py-3 font-medium transition-colors relative ${
                activeTab === 'my-reviews'
                  ? 'text-emerald-600'
                  : 'text-slate-500 hover:text-slate-700'
              }`}
            >
              My Reviews
              {activeTab === 'my-reviews' && (
                <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-emerald-500 rounded-full" />
              )}
            </button>
            <button
              onClick={() => setActiveTab('team-reviews')}
              className={`px-4 py-3 font-medium transition-colors relative ${
                activeTab === 'team-reviews'
                  ? 'text-emerald-600'
                  : 'text-slate-500 hover:text-slate-700'
              }`}
            >
              Team Reviews
              {activeTab === 'team-reviews' && (
                <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-emerald-500 rounded-full" />
              )}
            </button>
          </div>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-xl mb-6">
            {error}
          </div>
        )}

        {loading && (
          <div className="flex justify-center py-12">
            <div className="w-8 h-8 border-3 border-emerald-500 border-t-transparent rounded-full animate-spin" />
          </div>
        )}

        {!loading && activeTab === 'cycles' && (
          <div className="grid gap-4">
            {cycles.length === 0 ? (
              <div className="bg-white/80 backdrop-blur-md rounded-3xl shadow-lg shadow-slate-200/50 border border-white/60 p-12 text-center">
                <div className="text-4xl mb-4">📋</div>
                <h3 className="text-lg font-medium text-slate-700 mb-2">No Review Cycles</h3>
                <p className="text-slate-500">Create a new performance review cycle to get started.</p>
              </div>
            ) : (
              cycles.map((cycle) => (
                <div
                  key={cycle.id}
                  className="bg-white/80 backdrop-blur-md rounded-2xl shadow-md shadow-slate-200/50 border border-white/60 p-6 hover:shadow-lg transition-shadow"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <h3 className="text-lg font-semibold text-slate-800">{cycle.name}</h3>
                        <span className={`px-2.5 py-1 rounded-full text-xs font-medium ${STATUS_COLORS[cycle.status] || 'bg-slate-100 text-slate-600'}`}>
                          {cycle.status.charAt(0).toUpperCase() + cycle.status.slice(1)}
                        </span>
                        <span className="px-2.5 py-1 bg-slate-100 rounded-full text-xs font-medium text-slate-600">
                          {cycle.cycle_type}
                        </span>
                      </div>
                      <div className="flex flex-wrap gap-4 text-sm text-slate-500">
                        <div className="flex items-center gap-1.5">
                          <span>📅</span>
                          <span>{formatDate(cycle.start_date)} - {formatDate(cycle.end_date)}</span>
                        </div>
                        {cycle.self_assessment_deadline && (
                          <div className="flex items-center gap-1.5">
                            <span>✍️</span>
                            <span>Self-assessment by {formatDate(cycle.self_assessment_deadline)}</span>
                          </div>
                        )}
                        {cycle.manager_review_deadline && (
                          <div className="flex items-center gap-1.5">
                            <span>👔</span>
                            <span>Manager review by {formatDate(cycle.manager_review_deadline)}</span>
                          </div>
                        )}
                        <div className="flex items-center gap-1.5">
                          <span>👥</span>
                          <span>{cycle.review_count} reviews</span>
                        </div>
                      </div>
                    </div>
                    {isAdmin && (
                      <div className="flex gap-2">
                        <button
                          onClick={() => {
                            setSelectedCycle(cycle)
                            setShowBulkCreateModal(true)
                          }}
                          className="px-3 py-2 text-sm bg-blue-50 text-blue-600 rounded-lg hover:bg-blue-100 transition-colors"
                        >
                          Add Reviews
                        </button>
                        <button
                          onClick={() => openCycleModal(cycle)}
                          className="px-3 py-2 text-sm bg-slate-100 text-slate-600 rounded-lg hover:bg-slate-200 transition-colors"
                        >
                          Edit
                        </button>
                      </div>
                    )}
                  </div>
                </div>
              ))
            )}
          </div>
        )}

        {!loading && activeTab === 'my-reviews' && (
          <div className="grid gap-4">
            {myReviews.length === 0 ? (
              <div className="bg-white/80 backdrop-blur-md rounded-3xl shadow-lg shadow-slate-200/50 border border-white/60 p-12 text-center">
                <div className="text-4xl mb-4">📝</div>
                <h3 className="text-lg font-medium text-slate-700 mb-2">No Reviews Assigned</h3>
                <p className="text-slate-500">You don't have any performance reviews to complete at this time.</p>
              </div>
            ) : (
              myReviews.map((review) => (
                <div
                  key={review.id}
                  className="bg-white/80 backdrop-blur-md rounded-2xl shadow-md shadow-slate-200/50 border border-white/60 p-6"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <h3 className="text-lg font-semibold text-slate-800">{review.cycle_name}</h3>
                        <span className={`px-2.5 py-1 rounded-full text-xs font-medium ${STATUS_COLORS[review.status] || 'bg-slate-100 text-slate-600'}`}>
                          {review.status.replace('_', ' ').charAt(0).toUpperCase() + review.status.replace('_', ' ').slice(1)}
                        </span>
                      </div>
                      <div className="flex flex-wrap gap-4 text-sm text-slate-500">
                        {review.reviewer_name && (
                          <div className="flex items-center gap-1.5">
                            <span>👔</span>
                            <span>Reviewer: {review.reviewer_name}</span>
                          </div>
                        )}
                        <div className="flex items-center gap-1.5">
                          <span>✍️</span>
                          <span>Self-assessment: {review.self_assessment_submitted ? '✅ Submitted' : '⏳ Pending'}</span>
                        </div>
                        {review.overall_rating && (
                          <div className="flex items-center gap-1.5">
                            <span>⭐</span>
                            <span>Rating: {review.overall_rating.toFixed(1)} - {review.rating_label}</span>
                          </div>
                        )}
                      </div>
                    </div>
                    {!review.self_assessment_submitted && (
                      <button
                        onClick={() => openReviewModal(review)}
                        className="px-4 py-2 bg-emerald-500 text-white rounded-lg hover:bg-emerald-600 transition-colors font-medium"
                      >
                        Complete Self-Assessment
                      </button>
                    )}
                  </div>
                </div>
              ))
            )}
          </div>
        )}

        {!loading && activeTab === 'team-reviews' && (
          <div className="grid gap-4">
            {teamReviews.length === 0 ? (
              <div className="bg-white/80 backdrop-blur-md rounded-3xl shadow-lg shadow-slate-200/50 border border-white/60 p-12 text-center">
                <div className="text-4xl mb-4">👥</div>
                <h3 className="text-lg font-medium text-slate-700 mb-2">No Team Reviews</h3>
                <p className="text-slate-500">You don't have any team member reviews to complete.</p>
              </div>
            ) : (
              teamReviews.map((review) => (
                <div
                  key={review.id}
                  className="bg-white/80 backdrop-blur-md rounded-2xl shadow-md shadow-slate-200/50 border border-white/60 p-6"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <h3 className="text-lg font-semibold text-slate-800">{review.employee_name}</h3>
                        <span className="text-slate-400">•</span>
                        <span className="text-slate-600">{review.cycle_name}</span>
                        <span className={`px-2.5 py-1 rounded-full text-xs font-medium ${STATUS_COLORS[review.status] || 'bg-slate-100 text-slate-600'}`}>
                          {review.status.replace('_', ' ').charAt(0).toUpperCase() + review.status.replace('_', ' ').slice(1)}
                        </span>
                      </div>
                      <div className="flex flex-wrap gap-4 text-sm text-slate-500">
                        <div className="flex items-center gap-1.5">
                          <span>✍️</span>
                          <span>Self-assessment: {review.self_assessment_submitted ? '✅ Submitted' : '⏳ Pending'}</span>
                        </div>
                        <div className="flex items-center gap-1.5">
                          <span>👔</span>
                          <span>Manager review: {review.manager_review_submitted ? '✅ Completed' : '⏳ Pending'}</span>
                        </div>
                        {review.overall_rating && (
                          <div className="flex items-center gap-1.5">
                            <span>⭐</span>
                            <span>Rating: {review.overall_rating.toFixed(1)} - {review.rating_label}</span>
                          </div>
                        )}
                      </div>
                    </div>
                    {review.self_assessment_submitted && !review.manager_review_submitted && (
                      <button
                        onClick={() => openReviewModal(review)}
                        className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors font-medium"
                      >
                        Complete Manager Review
                      </button>
                    )}
                  </div>
                </div>
              ))
            )}
          </div>
        )}
      </div>

      {showCycleModal && (
        <div className="fixed inset-0 bg-black/40 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="bg-white/95 backdrop-blur-md rounded-3xl shadow-2xl max-w-lg w-full p-8 border border-white/60">
            <h2 className="text-xl font-semibold text-slate-800 mb-6">
              {editingCycle ? 'Edit Review Cycle' : 'Create Review Cycle'}
            </h2>
            <form onSubmit={handleSaveCycle} className="space-y-5">
              <div>
                <label className="block text-sm font-medium text-slate-600 mb-1.5">Cycle Name</label>
                <input
                  type="text"
                  value={cycleForm.name}
                  onChange={(e) => setCycleForm({ ...cycleForm, name: e.target.value })}
                  className="w-full px-4 py-3 bg-white/80 border border-slate-200 rounded-xl focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-400 outline-none transition-all"
                  placeholder="e.g., 2026 Annual Review"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-600 mb-1.5">Cycle Type</label>
                <select
                  value={cycleForm.cycle_type}
                  onChange={(e) => setCycleForm({ ...cycleForm, cycle_type: e.target.value })}
                  className="w-full px-4 py-3 bg-white/80 border border-slate-200 rounded-xl focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-400 outline-none transition-all"
                >
                  {CYCLE_TYPES.map((type) => (
                    <option key={type} value={type}>{type}</option>
                  ))}
                </select>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-slate-600 mb-1.5">Start Date</label>
                  <input
                    type="date"
                    value={cycleForm.start_date}
                    onChange={(e) => setCycleForm({ ...cycleForm, start_date: e.target.value })}
                    className="w-full px-4 py-3 bg-white/80 border border-slate-200 rounded-xl focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-400 outline-none transition-all"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-600 mb-1.5">End Date</label>
                  <input
                    type="date"
                    value={cycleForm.end_date}
                    onChange={(e) => setCycleForm({ ...cycleForm, end_date: e.target.value })}
                    className="w-full px-4 py-3 bg-white/80 border border-slate-200 rounded-xl focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-400 outline-none transition-all"
                    required
                  />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-slate-600 mb-1.5">Self-Assessment Deadline</label>
                  <input
                    type="date"
                    value={cycleForm.self_assessment_deadline}
                    onChange={(e) => setCycleForm({ ...cycleForm, self_assessment_deadline: e.target.value })}
                    className="w-full px-4 py-3 bg-white/80 border border-slate-200 rounded-xl focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-400 outline-none transition-all"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-600 mb-1.5">Manager Review Deadline</label>
                  <input
                    type="date"
                    value={cycleForm.manager_review_deadline}
                    onChange={(e) => setCycleForm({ ...cycleForm, manager_review_deadline: e.target.value })}
                    className="w-full px-4 py-3 bg-white/80 border border-slate-200 rounded-xl focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-400 outline-none transition-all"
                  />
                </div>
              </div>
              <div className="flex gap-3 pt-4">
                <button
                  type="button"
                  onClick={() => setShowCycleModal(false)}
                  className="flex-1 px-4 py-3 bg-slate-100 text-slate-600 rounded-xl hover:bg-slate-200 transition-colors font-medium"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={loading}
                  className="flex-1 px-4 py-3 bg-emerald-500 text-white rounded-xl hover:bg-emerald-600 transition-colors font-medium disabled:opacity-50"
                >
                  {loading ? 'Saving...' : (editingCycle ? 'Update Cycle' : 'Create Cycle')}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {showBulkCreateModal && selectedCycle && (
        <div className="fixed inset-0 bg-black/40 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="bg-white/95 backdrop-blur-md rounded-3xl shadow-2xl max-w-lg w-full p-8 border border-white/60">
            <h2 className="text-xl font-semibold text-slate-800 mb-2">Add Reviews to {selectedCycle.name}</h2>
            <p className="text-slate-500 text-sm mb-6">Enter employee IDs (comma-separated) to create reviews</p>
            <div className="space-y-5">
              <div>
                <label className="block text-sm font-medium text-slate-600 mb-1.5">Employee IDs</label>
                <textarea
                  value={bulkEmployeeIds}
                  onChange={(e) => setBulkEmployeeIds(e.target.value)}
                  className="w-full px-4 py-3 bg-white/80 border border-slate-200 rounded-xl focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-400 outline-none transition-all"
                  placeholder="e.g., 1, 2, 3, 4, 5"
                  rows={3}
                />
              </div>
              <div className="flex gap-3">
                <button
                  type="button"
                  onClick={() => {
                    setShowBulkCreateModal(false)
                    setBulkEmployeeIds('')
                  }}
                  className="flex-1 px-4 py-3 bg-slate-100 text-slate-600 rounded-xl hover:bg-slate-200 transition-colors font-medium"
                >
                  Cancel
                </button>
                <button
                  type="button"
                  onClick={handleBulkCreateReviews}
                  disabled={loading || !bulkEmployeeIds.trim()}
                  className="flex-1 px-4 py-3 bg-blue-500 text-white rounded-xl hover:bg-blue-600 transition-colors font-medium disabled:opacity-50"
                >
                  {loading ? 'Creating...' : 'Create Reviews'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {showReviewModal && selectedReview && (
        <div className="fixed inset-0 bg-black/40 backdrop-blur-sm flex items-center justify-center z-50 p-4 overflow-y-auto">
          <div className="bg-white/95 backdrop-blur-md rounded-3xl shadow-2xl max-w-2xl w-full p-8 border border-white/60 my-8">
            <h2 className="text-xl font-semibold text-slate-800 mb-2">
              {selectedReview.employee_name !== user.name ? `Review for ${selectedReview.employee_name}` : 'Self-Assessment'}
            </h2>
            <p className="text-slate-500 text-sm mb-6">{selectedReview.cycle_name}</p>

            {selectedReview.employee_name === user.name && !selectedReview.self_assessment_submitted ? (
              <div className="space-y-6">
                <div>
                  <h3 className="text-sm font-semibold text-slate-700 mb-4">Competency Ratings</h3>
                  <div className="space-y-4">
                    {selectedReview.ratings.map((rating) => (
                      <div key={rating.competency_name} className="p-4 bg-slate-50 rounded-xl">
                        <div className="flex items-center justify-between mb-2">
                          <span className="font-medium text-slate-700">{rating.competency_name}</span>
                          <span className="text-xs text-slate-400">{rating.weight}%</span>
                        </div>
                        {renderRatingStars(
                          assessmentForm.ratings[rating.competency_name]?.rating || 3,
                          (value) => setAssessmentForm({
                            ...assessmentForm,
                            ratings: {
                              ...assessmentForm.ratings,
                              [rating.competency_name]: {
                                ...assessmentForm.ratings[rating.competency_name],
                                rating: value
                              }
                            }
                          })
                        )}
                        <textarea
                          value={assessmentForm.ratings[rating.competency_name]?.comments || ''}
                          onChange={(e) => setAssessmentForm({
                            ...assessmentForm,
                            ratings: {
                              ...assessmentForm.ratings,
                              [rating.competency_name]: {
                                ...assessmentForm.ratings[rating.competency_name],
                                comments: e.target.value
                              }
                            }
                          })}
                          className="w-full mt-2 px-3 py-2 text-sm bg-white border border-slate-200 rounded-lg focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-400 outline-none"
                          placeholder="Add comments..."
                          rows={2}
                        />
                      </div>
                    ))}
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-600 mb-1.5">Key Achievements</label>
                  <textarea
                    value={assessmentForm.achievements}
                    onChange={(e) => setAssessmentForm({ ...assessmentForm, achievements: e.target.value })}
                    className="w-full px-4 py-3 bg-white/80 border border-slate-200 rounded-xl focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-400 outline-none transition-all"
                    placeholder="Describe your key achievements during this period..."
                    rows={3}
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-600 mb-1.5">Challenges Faced</label>
                  <textarea
                    value={assessmentForm.challenges}
                    onChange={(e) => setAssessmentForm({ ...assessmentForm, challenges: e.target.value })}
                    className="w-full px-4 py-3 bg-white/80 border border-slate-200 rounded-xl focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-400 outline-none transition-all"
                    placeholder="What challenges did you face?"
                    rows={3}
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-600 mb-1.5">Goals for Next Period</label>
                  <textarea
                    value={assessmentForm.goals_next_period}
                    onChange={(e) => setAssessmentForm({ ...assessmentForm, goals_next_period: e.target.value })}
                    className="w-full px-4 py-3 bg-white/80 border border-slate-200 rounded-xl focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-400 outline-none transition-all"
                    placeholder="What are your goals for the next period?"
                    rows={3}
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-600 mb-1.5">Training & Development Needs</label>
                  <textarea
                    value={assessmentForm.training_needs}
                    onChange={(e) => setAssessmentForm({ ...assessmentForm, training_needs: e.target.value })}
                    className="w-full px-4 py-3 bg-white/80 border border-slate-200 rounded-xl focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-400 outline-none transition-all"
                    placeholder="What training or development would help you?"
                    rows={2}
                  />
                </div>

                <div className="flex gap-3 pt-4">
                  <button
                    type="button"
                    onClick={() => setShowReviewModal(false)}
                    className="flex-1 px-4 py-3 bg-slate-100 text-slate-600 rounded-xl hover:bg-slate-200 transition-colors font-medium"
                  >
                    Cancel
                  </button>
                  <button
                    type="button"
                    onClick={handleSubmitSelfAssessment}
                    disabled={loading}
                    className="flex-1 px-4 py-3 bg-emerald-500 text-white rounded-xl hover:bg-emerald-600 transition-colors font-medium disabled:opacity-50"
                  >
                    {loading ? 'Submitting...' : 'Submit Self-Assessment'}
                  </button>
                </div>
              </div>
            ) : (
              <div className="space-y-6">
                <div>
                  <h3 className="text-sm font-semibold text-slate-700 mb-4">Competency Ratings</h3>
                  <div className="space-y-4">
                    {selectedReview.ratings.map((rating) => (
                      <div key={rating.competency_name} className="p-4 bg-slate-50 rounded-xl">
                        <div className="flex items-center justify-between mb-2">
                          <span className="font-medium text-slate-700">{rating.competency_name}</span>
                          <span className="text-xs text-slate-400">{rating.weight}%</span>
                        </div>
                        {rating.self_rating && (
                          <div className="mb-2 text-sm text-slate-500">
                            Employee self-rating: {renderRatingStars(rating.self_rating)}
                            {rating.self_comments && (
                              <p className="mt-1 italic">{rating.self_comments}</p>
                            )}
                          </div>
                        )}
                        <div className="mt-2">
                          <span className="text-sm text-slate-600">Your rating:</span>
                          {renderRatingStars(
                            managerForm.ratings[rating.competency_name]?.rating || 3,
                            (value) => setManagerForm({
                              ...managerForm,
                              ratings: {
                                ...managerForm.ratings,
                                [rating.competency_name]: {
                                  ...managerForm.ratings[rating.competency_name],
                                  rating: value
                                }
                              }
                            })
                          )}
                        </div>
                        <textarea
                          value={managerForm.ratings[rating.competency_name]?.comments || ''}
                          onChange={(e) => setManagerForm({
                            ...managerForm,
                            ratings: {
                              ...managerForm.ratings,
                              [rating.competency_name]: {
                                ...managerForm.ratings[rating.competency_name],
                                comments: e.target.value
                              }
                            }
                          })}
                          className="w-full mt-2 px-3 py-2 text-sm bg-white border border-slate-200 rounded-lg focus:ring-2 focus:ring-blue-500/20 focus:border-blue-400 outline-none"
                          placeholder="Add your comments..."
                          rows={2}
                        />
                      </div>
                    ))}
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-600 mb-1.5">Key Achievements Observed</label>
                  <textarea
                    value={managerForm.achievements}
                    onChange={(e) => setManagerForm({ ...managerForm, achievements: e.target.value })}
                    className="w-full px-4 py-3 bg-white/80 border border-slate-200 rounded-xl focus:ring-2 focus:ring-blue-500/20 focus:border-blue-400 outline-none transition-all"
                    placeholder="What achievements did you observe?"
                    rows={3}
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-600 mb-1.5">Areas for Improvement</label>
                  <textarea
                    value={managerForm.areas_improvement}
                    onChange={(e) => setManagerForm({ ...managerForm, areas_improvement: e.target.value })}
                    className="w-full px-4 py-3 bg-white/80 border border-slate-200 rounded-xl focus:ring-2 focus:ring-blue-500/20 focus:border-blue-400 outline-none transition-all"
                    placeholder="What areas need improvement?"
                    rows={3}
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-600 mb-1.5">Recommendations</label>
                  <textarea
                    value={managerForm.recommendations}
                    onChange={(e) => setManagerForm({ ...managerForm, recommendations: e.target.value })}
                    className="w-full px-4 py-3 bg-white/80 border border-slate-200 rounded-xl focus:ring-2 focus:ring-blue-500/20 focus:border-blue-400 outline-none transition-all"
                    placeholder="Training, development, or other recommendations..."
                    rows={3}
                  />
                </div>

                <div className="flex gap-3 pt-4">
                  <button
                    type="button"
                    onClick={() => setShowReviewModal(false)}
                    className="flex-1 px-4 py-3 bg-slate-100 text-slate-600 rounded-xl hover:bg-slate-200 transition-colors font-medium"
                  >
                    Cancel
                  </button>
                  <button
                    type="button"
                    onClick={handleSubmitManagerReview}
                    disabled={loading}
                    className="flex-1 px-4 py-3 bg-blue-500 text-white rounded-xl hover:bg-blue-600 transition-colors font-medium disabled:opacity-50"
                  >
                    {loading ? 'Submitting...' : 'Complete Review'}
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
