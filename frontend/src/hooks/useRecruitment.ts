import { useState, useCallback } from 'react'
import { User, RecruitmentStats, PipelineCounts, Candidate, RecruitmentRequest } from '../types'
import { API_BASE, fetchWithAuth } from '../utils/api'

interface UseRecruitmentReturn {
  recruitmentStats: RecruitmentStats | null
  recruitmentRequests: RecruitmentRequest[]
  pipelineCounts: PipelineCounts | null
  candidatesList: Candidate[]
  selectedCandidate: Candidate | null
  candidateSearchQuery: string
  candidateStatusFilter: string
  candidateSourceFilter: string
  showCandidateProfileModal: boolean
  loading: boolean
  fetchRecruitmentData: () => Promise<void>
  fetchRecruitmentCandidates: (searchTerm?: string) => Promise<void>
  setSelectedCandidate: (candidate: Candidate | null) => void
  setCandidateSearchQuery: (query: string) => void
  setCandidateStatusFilter: (filter: string) => void
  setCandidateSourceFilter: (filter: string) => void
  setShowCandidateProfileModal: (show: boolean) => void
}

export function useRecruitment(user: User | null): UseRecruitmentReturn {
  const [recruitmentStats, setRecruitmentStats] = useState<RecruitmentStats | null>(null)
  const [recruitmentRequests, setRecruitmentRequests] = useState<RecruitmentRequest[]>([])
  const [pipelineCounts, setPipelineCounts] = useState<PipelineCounts | null>(null)
  const [candidatesList, setCandidatesList] = useState<Candidate[]>([])
  const [selectedCandidate, setSelectedCandidate] = useState<Candidate | null>(null)
  const [candidateSearchQuery, setCandidateSearchQuery] = useState('')
  const [candidateStatusFilter, setCandidateStatusFilter] = useState('')
  const [candidateSourceFilter, setCandidateSourceFilter] = useState('')
  const [showCandidateProfileModal, setShowCandidateProfileModal] = useState(false)
  const [loading, setLoading] = useState(false)

  const fetchRecruitmentData = useCallback(async () => {
    if (!user || (user.role !== 'admin' && user.role !== 'hr')) return
    
    setLoading(true)
    try {
      const [statsRes, requestsRes, pipelineRes] = await Promise.all([
        fetchWithAuth(`${API_BASE}/recruitment/stats`, { token: user.token, role: user.role }),
        fetchWithAuth(`${API_BASE}/recruitment/requests`, { token: user.token, role: user.role }),
        fetchWithAuth(`${API_BASE}/recruitment/pipeline`, { token: user.token, role: user.role })
      ])
      
      if (statsRes.ok) setRecruitmentStats(await statsRes.json())
      if (requestsRes.ok) setRecruitmentRequests(await requestsRes.json())
      if (pipelineRes.ok) setPipelineCounts(await pipelineRes.json())
    } catch (err) {
      console.error('Failed to fetch recruitment data:', err)
    } finally {
      setLoading(false)
    }
  }, [user])

  const fetchRecruitmentCandidates = useCallback(async (searchTerm: string = '') => {
    if (!user || (user.role !== 'admin' && user.role !== 'hr')) return
    
    try {
      const url = searchTerm
        ? `${API_BASE}/recruitment/candidates?search=${encodeURIComponent(searchTerm)}`
        : `${API_BASE}/recruitment/candidates`
      
      const res = await fetchWithAuth(url, { token: user.token, role: user.role })
      
      if (res.ok) {
        setCandidatesList(await res.json())
      }
    } catch (err) {
      console.error('Failed to fetch recruitment candidates:', err)
    }
  }, [user])

  return {
    recruitmentStats,
    recruitmentRequests,
    pipelineCounts,
    candidatesList,
    selectedCandidate,
    candidateSearchQuery,
    candidateStatusFilter,
    candidateSourceFilter,
    showCandidateProfileModal,
    loading,
    fetchRecruitmentData,
    fetchRecruitmentCandidates,
    setSelectedCandidate,
    setCandidateSearchQuery,
    setCandidateStatusFilter,
    setCandidateSourceFilter,
    setShowCandidateProfileModal,
  }
}
