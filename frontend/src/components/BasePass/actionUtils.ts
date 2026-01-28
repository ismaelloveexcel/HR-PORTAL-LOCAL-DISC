/**
 * Recruitment Workflow Configuration
 * 
 * GOVERNING LOGIC (NON-NEGOTIABLE):
 * - Statuses do not do work — Actions do
 * - Each status maps to ONE primary Next Action
 * - Action Owner is singular (no shared accountability)
 * - Candidate Pass = visibility only
 * - HR / System triggers stage movement
 * - Manager actions are decision-gated
 * - HR is the superuser and only HR can manually revise passes
 */

// Action Owners - defines who can perform actions
export type ActionOwner = 'HR' | 'Candidate' | 'Manager' | 'System'

export interface ActionConfig {
  label: string
  description?: string
  actionType: string
  actionOwner?: ActionOwner
}

export interface StatusConfig {
  key: string
  label: string
  nextAction: string
  actionOwner: ActionOwner
  internalOnly?: boolean  // If true, this status is never shown to candidates
}

export interface Stage {
  key: string
  label: string
  candidateLabel?: string
  managerLabel?: string
  icon: string
}

export const UNIFIED_STAGES: Stage[] = [
  { 
    key: 'application', 
    label: 'Application',
    candidateLabel: 'Application',
    managerLabel: 'Request',
    icon: 'M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z' 
  },
  { 
    key: 'screening', 
    label: 'Assessment',
    candidateLabel: 'Shortlist',
    managerLabel: 'Screening',
    icon: 'M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4' 
  },
  { 
    key: 'interview', 
    label: 'Interview',
    candidateLabel: 'Interview',
    managerLabel: 'Interview',
    icon: 'M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z' 
  },
  { 
    key: 'offer', 
    label: 'Offer',
    candidateLabel: 'Offer',
    managerLabel: 'Decision',
    icon: 'M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z' 
  },
  { 
    key: 'onboarding', 
    label: 'Onboarding',
    candidateLabel: 'Onboard',
    managerLabel: 'Onboard',
    icon: 'M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z' 
  }
]

export const CANDIDATE_STAGES = UNIFIED_STAGES
export const MANAGER_STAGES = UNIFIED_STAGES

// Helper function to normalize stage keys (maps legacy 'decision' to 'offer')
export function normalizeStageKey(stage: string): string {
  const stageLower = stage.toLowerCase()
  return stageLower === 'decision' ? 'offer' : stageLower
}

// Helper function to normalize status keys (converts spaces and hyphens to underscores)
export function normalizeStatusKey(status: string): string {
  return status.toLowerCase().replace(/[\s-]/g, '_')
}

/**
 * STAGE 1 — APPLICATION / REQUEST
 * Candidate: Application | Manager: Request
 */
export const CANDIDATE_STATUSES: Record<string, StatusConfig[]> = {
  application: [
    { key: 'submitted', label: 'Submitted', nextAction: 'Validate application completeness', actionOwner: 'HR' },
    { key: 'incomplete', label: 'Incomplete', nextAction: 'Submit missing information', actionOwner: 'Candidate' },
    { key: 'validated', label: 'Application Validated', nextAction: 'Initiate screening', actionOwner: 'HR' },
    { key: 'withdrawn', label: 'Withdrawn', nextAction: 'Close application', actionOwner: 'System' }
  ],
  /**
   * STAGE 2 — SHORTLIST / SCREENING
   * Candidate: Shortlist
   * ASSESSMENT OVERLAY STATUSES (sub-status flags, not stage drivers)
   */
  screening: [
    { key: 'under_review', label: 'Under Review', nextAction: 'Complete screening', actionOwner: 'HR' },
    { key: 'shortlisted', label: 'Shortlisted', nextAction: 'Prepare interview', actionOwner: 'HR' },
    { key: 'not_shortlisted', label: 'Not Shortlisted', nextAction: 'Close candidate record', actionOwner: 'System' },
    { key: 'on_hold', label: 'On Hold', nextAction: 'Await decision', actionOwner: 'HR' },
    // Assessment overlay statuses (LOCKED - sub-status flags)
    { key: 'assessment_required', label: 'Assessment Required', nextAction: 'Complete assessment', actionOwner: 'Candidate' },
    { key: 'assessment_sent', label: 'Assessment Sent', nextAction: 'Complete assessment', actionOwner: 'Candidate' },
    { key: 'assessment_completed', label: 'Assessment Completed', nextAction: 'Review results', actionOwner: 'HR' },
    { key: 'assessment_failed', label: 'Assessment Failed', nextAction: 'Review for rejection', actionOwner: 'HR' },
    // Note: assessment_waived is INTERNAL ONLY - never shown to candidates
    { key: 'assessment_waived', label: 'Assessment Waived', nextAction: 'Proceed to interview', actionOwner: 'HR', internalOnly: true }
  ],
  /**
   * STAGE 3 — INTERVIEW
   * Candidate: Interview
   * ASSESSMENT OVERLAY STATUSES (for late-stage assessments)
   */
  interview: [
    { key: 'pending', label: 'Interview Pending', nextAction: 'Schedule interview', actionOwner: 'HR' },
    { key: 'slots_available', label: 'Slots Available', nextAction: 'Select interview slot', actionOwner: 'Candidate' },
    { key: 'scheduled', label: 'Interview Scheduled', nextAction: 'Confirm attendance', actionOwner: 'Candidate' },
    { key: 'confirmed', label: 'Interview Confirmed', nextAction: 'Attend interview', actionOwner: 'Candidate' },
    { key: 'completed', label: 'Interview Completed', nextAction: 'Await feedback', actionOwner: 'HR' },
    { key: 'cancelled', label: 'Interview Cancelled', nextAction: 'Reschedule interview', actionOwner: 'HR' },
    { key: 'no_show', label: 'Interview No-Show', nextAction: 'Close or reschedule', actionOwner: 'HR' },
    // Assessment overlay statuses (for late-stage technical assessments)
    { key: 'assessment_required', label: 'Assessment Required', nextAction: 'Complete assessment', actionOwner: 'Candidate' },
    { key: 'assessment_sent', label: 'Assessment Sent', nextAction: 'Complete assessment', actionOwner: 'Candidate' },
    { key: 'assessment_completed', label: 'Assessment Completed', nextAction: 'Review results', actionOwner: 'Manager' }
  ],
  /**
   * STAGE 4 — OFFER
   * Candidate: Offer
   */
  offer: [
    { key: 'in_preparation', label: 'Offer In Preparation', nextAction: 'Await offer', actionOwner: 'HR' },
    { key: 'released', label: 'Offer Released', nextAction: 'Review and respond to offer', actionOwner: 'Candidate' },
    { key: 'accepted', label: 'Offer Accepted', nextAction: 'Initiate onboarding', actionOwner: 'HR' },
    { key: 'declined', label: 'Offer Declined', nextAction: 'Close candidate', actionOwner: 'System' },
    { key: 'negotiating', label: 'Negotiating', nextAction: 'Review revised terms', actionOwner: 'Candidate' },
    { key: 'expired', label: 'Offer Expired', nextAction: 'Close or re-offer', actionOwner: 'HR' },
    { key: 'withdrawn', label: 'Offer Withdrawn', nextAction: 'Close candidate', actionOwner: 'System' }
  ],
  /**
   * STAGE 5 — ONBOARDING
   * Candidate: Onboard
   */
  onboarding: [
    { key: 'initiated', label: 'Onboarding Initiated', nextAction: 'Submit onboarding documents', actionOwner: 'Candidate' },
    { key: 'documents_pending', label: 'Documents Pending', nextAction: 'Upload required documents', actionOwner: 'Candidate' },
    { key: 'documents_submitted', label: 'Documents Submitted', nextAction: 'Verify documents', actionOwner: 'HR' },
    { key: 'pre_joining', label: 'Pre-Joining In Progress', nextAction: 'Complete pre-joining tasks', actionOwner: 'Candidate' },
    { key: 'joining_confirmed', label: 'Joining Confirmed', nextAction: 'Prepare for Day 1', actionOwner: 'HR' },
    { key: 'completed', label: 'Onboarding Completed', nextAction: 'Convert to employee', actionOwner: 'HR' },
    { key: 'no_show', label: 'No Show', nextAction: 'Close candidate', actionOwner: 'System' }
  ]
}

/**
 * Manager Statuses with Next Actions and Action Owners
 */
export const MANAGER_STATUSES: Record<string, StatusConfig[]> = {
  /**
   * STAGE 1 — REQUEST
   */
  application: [
    { key: 'raised', label: 'Request Raised', nextAction: 'Review & approve request', actionOwner: 'Manager' },
    { key: 'approved', label: 'Request Approved', nextAction: 'Open application intake', actionOwner: 'HR' },
    { key: 'on_hold', label: 'Request On Hold', nextAction: 'Monitor / await decision', actionOwner: 'Manager' },
    { key: 'cancelled', label: 'Request Cancelled', nextAction: 'Close request', actionOwner: 'System' }
  ],
  /**
   * STAGE 2 — SCREENING
   */
  screening: [
    { key: 'in_progress', label: 'Screening In Progress', nextAction: 'Review candidate profile', actionOwner: 'Manager' },
    { key: 'shortlisted', label: 'Shortlisted', nextAction: 'Confirm interview intent', actionOwner: 'Manager' },
    { key: 'rejected', label: 'Rejected at Screening', nextAction: 'Close candidate', actionOwner: 'HR' },
    { key: 'on_hold', label: 'Screening On Hold', nextAction: 'Reassess later', actionOwner: 'Manager' }
  ],
  /**
   * STAGE 3 — INTERVIEW
   */
  interview: [
    { key: 'pending', label: 'Interview Pending', nextAction: 'Provide availability', actionOwner: 'Manager' },
    { key: 'slots_provided', label: 'Slots Provided', nextAction: 'Await candidate selection', actionOwner: 'System' },
    { key: 'scheduled', label: 'Interview Scheduled', nextAction: 'Conduct interview', actionOwner: 'Manager' },
    { key: 'completed', label: 'Interview Completed', nextAction: 'Submit feedback', actionOwner: 'Manager' },
    { key: 'feedback_pending', label: 'Feedback Pending', nextAction: 'Submit evaluation', actionOwner: 'Manager' },
    { key: 'additional_required', label: 'Additional Interview Required', nextAction: 'Schedule next round', actionOwner: 'HR' },
    { key: 'cancelled', label: 'Interview Cancelled', nextAction: 'Reschedule or close', actionOwner: 'HR' }
  ],
  /**
   * STAGE 4 — DECISION
   */
  offer: [
    { key: 'pending', label: 'Decision Pending', nextAction: 'Make hire/no-hire decision', actionOwner: 'Manager' },
    { key: 'approved', label: 'Approved for Offer', nextAction: 'Prepare offer letter', actionOwner: 'HR' },
    { key: 'not_approved', label: 'Not Approved', nextAction: 'Close candidate', actionOwner: 'HR' },
    { key: 'released', label: 'Offer Released', nextAction: 'Await candidate response', actionOwner: 'System' },
    { key: 'accepted', label: 'Offer Accepted', nextAction: 'Initiate onboarding', actionOwner: 'HR' },
    { key: 'declined', label: 'Offer Declined by Candidate', nextAction: 'Review pipeline', actionOwner: 'Manager' }
  ],
  /**
   * STAGE 5 — ONBOARDING
   */
  onboarding: [
    { key: 'initiated', label: 'Onboarding Initiated', nextAction: 'Monitor progress', actionOwner: 'Manager' },
    { key: 'documentation', label: 'Documentation In Progress', nextAction: 'Await completion', actionOwner: 'System' },
    { key: 'joining_confirmed', label: 'Joining Confirmed', nextAction: 'Prepare workspace', actionOwner: 'Manager' },
    { key: 'completed', label: 'Onboarding Completed', nextAction: 'Close recruitment pass', actionOwner: 'HR' },
    { key: 'failed', label: 'Onboarding Failed', nextAction: 'Review and close', actionOwner: 'HR' }
  ]
}

/**
 * Get the candidate's action required based on current stage and status
 * Actions are derived from the status configuration
 */
export function getCandidateActionRequired(
  stage: string, 
  status: string
): ActionConfig | null {
  const normalizedStage = normalizeStageKey(stage)
  const normalizedStatus = normalizeStatusKey(status)
  
  // Get status config with next action
  const stageStatuses = CANDIDATE_STATUSES[normalizedStage]
  if (!stageStatuses) return null
  
  const statusConfig = stageStatuses.find(s => s.key === normalizedStatus)
  if (!statusConfig) return null
  
  // Only return action if candidate is the action owner
  if (statusConfig.actionOwner !== 'Candidate') {
    return null
  }
  
  // Map status to action type
  const actionTypeMap: Record<string, string> = {
    'Submit missing information': 'complete_profile',
    'Select interview slot': 'select_slot',
    'Confirm attendance': 'confirm_interview',
    'Attend interview': 'attend_interview',
    'Review and respond to offer': 'review_offer',
    'Submit onboarding documents': 'upload_onboarding_docs',
    'Upload required documents': 'upload_onboarding_docs',
    'Complete pre-joining tasks': 'complete_onboarding'
  }
  
  return {
    label: statusConfig.nextAction,
    description: `Action required by ${statusConfig.actionOwner}`,
    actionType: actionTypeMap[statusConfig.nextAction] || 'none',
    actionOwner: statusConfig.actionOwner
  }
}

/**
 * Get the manager's action required based on current state
 * Used for determining what action the manager needs to take
 */
export function getManagerActionRequired(
  stage: string,
  status: string,
  hasAvailableSlots: boolean = false,
  pendingEvaluations: number = 0
): ActionConfig | null {
  const normalizedStage = normalizeStageKey(stage)
  const normalizedStatus = normalizeStatusKey(status)
  
  // Get status config with next action
  const stageStatuses = MANAGER_STATUSES[normalizedStage]
  if (!stageStatuses) return null
  
  const statusConfig = stageStatuses.find(s => s.key === normalizedStatus)
  if (!statusConfig) return null
  
  // Only return action if Manager is the action owner
  if (statusConfig.actionOwner !== 'Manager') {
    return null
  }
  
  // Special handling for interview stage - provide slots
  if (normalizedStage === 'interview' && normalizedStatus === 'pending') {
    return {
      label: 'Provide Availability',
      description: 'Add available interview time slots',
      actionType: 'add_slots',
      actionOwner: 'Manager'
    }
  }
  
  // Special handling for feedback pending
  if (normalizedStage === 'interview' && normalizedStatus === 'feedback_pending') {
    return {
      label: `Submit Evaluation${pendingEvaluations > 1 ? 's' : ''}`,
      description: `${pendingEvaluations} evaluation${pendingEvaluations > 1 ? 's' : ''} pending`,
      actionType: 'submit_evaluation',
      actionOwner: 'Manager'
    }
  }
  
  return {
    label: statusConfig.nextAction,
    description: `Action required by ${statusConfig.actionOwner}`,
    actionType: 'manager_action',
    actionOwner: statusConfig.actionOwner
  }
}

/**
 * Get the next action info for a given stage and status
 */
export function getNextActionInfo(
  stage: string,
  status: string,
  viewType: 'candidate' | 'manager'
): { nextAction: string; actionOwner: ActionOwner } | null {
  const normalizedStage = normalizeStageKey(stage)
  const normalizedStatus = normalizeStatusKey(status)
  
  const statuses = viewType === 'candidate' ? CANDIDATE_STATUSES : MANAGER_STATUSES
  const stageStatuses = statuses[normalizedStage]
  
  if (!stageStatuses) return null
  
  const statusConfig = stageStatuses.find(s => s.key === normalizedStatus)
  if (!statusConfig) return null
  
  return {
    nextAction: statusConfig.nextAction,
    actionOwner: statusConfig.actionOwner
  }
}

/**
 * Get the action owner label with appropriate styling class
 */
export function getActionOwnerStyle(actionOwner: ActionOwner): { bgClass: string; textClass: string } {
  switch (actionOwner) {
    case 'HR':
      return { bgClass: 'bg-teal-100', textClass: 'text-teal-700' }
    case 'Candidate':
      return { bgClass: 'bg-blue-100', textClass: 'text-blue-700' }
    case 'Manager':
      return { bgClass: 'bg-amber-100', textClass: 'text-amber-700' }
    case 'System':
      return { bgClass: 'bg-slate-100', textClass: 'text-slate-500' }
    default:
      return { bgClass: 'bg-slate-100', textClass: 'text-slate-500' }
  }
}

export function getStageIndex(stages: { key: string }[], currentStage: string): number {
  const normalizedStage = normalizeStageKey(currentStage)
  const index = stages.findIndex(s => s.key === normalizedStage)
  if (index >= 0) return index
  return 0
}

export function getStageLabel(stage: string, viewType: 'candidate' | 'manager'): string {
  const normalizedStage = normalizeStageKey(stage)
  const stageObj = UNIFIED_STAGES.find(s => s.key === normalizedStage)
  if (!stageObj) return stage
  return viewType === 'candidate' ? (stageObj.candidateLabel || stageObj.label) : (stageObj.managerLabel || stageObj.label)
}

export function getStatusLabel(stage: string, status: string, viewType: 'candidate' | 'manager' = 'candidate'): string {
  const normalizedStage = normalizeStageKey(stage)
  const normalizedStatus = normalizeStatusKey(status)
  
  const statuses = viewType === 'candidate' ? CANDIDATE_STATUSES : MANAGER_STATUSES
  const stageStatuses = statuses[normalizedStage]
  
  if (stageStatuses) {
    const found = stageStatuses.find(s => s.key === normalizedStatus)
    if (found) {
      // LOCKED: If this is an internal-only status and we're in candidate view, return a generic label
      if (viewType === 'candidate' && found.internalOnly) {
        return 'In Progress'  // Generic status shown instead of "Waived"
      }
      return found.label
    }
  }
  
  return status.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
}

/**
 * Check if a status is internal-only and should not be shown to candidates
 * Used to filter out internal statuses like 'waived' from candidate pass
 */
export function isInternalOnlyStatus(stage: string, status: string): boolean {
  const normalizedStage = normalizeStageKey(stage)
  const normalizedStatus = normalizeStatusKey(status)
  
  const stageStatuses = CANDIDATE_STATUSES[normalizedStage]
  if (!stageStatuses) return false
  
  const found = stageStatuses.find(s => s.key === normalizedStatus)
  return found?.internalOnly === true
}
