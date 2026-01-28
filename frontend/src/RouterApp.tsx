import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { AuthProvider } from './contexts/AuthContext'
import App from './App'
import { HomePage } from './pages/HomePage'
import { ComplianceModule } from './pages/ComplianceModule'
import { AttendanceModule } from './pages/AttendanceModule'
import { RecruitmentModule } from './pages/RecruitmentModule'
import { OnboardingModule } from './pages/OnboardingModule'
import { AdminDashboard } from './pages/AdminDashboard'

/**
 * Router wrapper for the HR Portal - Phase 2 Complete
 * 
 * This component provides URL-based routing for the fully modularized HR Portal.
 * All major sections have been extracted into dedicated pages for better maintainability.
 * 
 * Navigation Structure (10 main sections):
 * 1. Home (/) - Portal landing page with role cards
 * 2. Admin (/admin) - Dashboard, employees, compliance, recruitment, settings
 * 3. Recruitment (/recruitment) - Job requests, candidates, pipeline
 * 4. Onboarding (/onboarding, /public-onboarding/:token) - HR + public forms
 * 5. Attendance (/attendance) - Clock in/out, tracking
 * 6. Compliance (/compliance) - Compliance alerts dashboard
 * 7. Employee Portal (handled by App.tsx fallback)
 * 8. Passes (handled by App.tsx fallback)
 * 9. Settings (/admin with settings tab)
 * 10. Public Forms (/public-onboarding/:token)
 * 
 * Auth Strategy:
 * - AuthContext provides centralized user state
 * - All pages access user via useAuthContext hook
 * - HomePage handles login modal
 * - Individual pages handle route protection
 */

export function RouterApp() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          {/* Home page - Portal landing */}
          <Route path="/" element={<HomePage />} />
          
          {/* Extracted modular pages */}
          <Route path="/admin" element={<AdminDashboard />} />
          <Route path="/compliance" element={<ComplianceModule />} />
          <Route path="/attendance" element={<AttendanceModule />} />
          <Route path="/recruitment" element={<RecruitmentModule />} />
          <Route path="/onboarding" element={<OnboardingModule />} />
          <Route path="/public-onboarding/:token?" element={<OnboardingModule />} />
          
          {/* Legacy App.tsx fallback for unmigrated sections */}
          <Route path="*" element={<App />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  )
}
