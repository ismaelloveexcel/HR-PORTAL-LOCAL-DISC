# Phase 2 Frontend Refactoring - Migration Guide

## Overview
This document tracks the incremental migration of the HR Portal frontend from a monolithic `App.tsx` (5,730 lines) to a modular, route-based architecture using React Router.

## Migration Strategy

### Phase 1: Infrastructure ✅
- Installed React Router DOM
- Created modular directory structure
- Extracted shared utilities and types
- Created custom hooks for state management

### Phase 2: Routing Layer ✅
- Created `RouterApp.tsx` as the new entry point
- Configured React Router with BrowserRouter
- Set up coexistence pattern (new routes + legacy App.tsx)

### Phase 3: Page Extraction (COMPLETED ✅)
Extracted pages from largest/most isolated first:

#### Completed:
- ✅ `ComplianceModule.tsx` (350 lines) - Available at `/compliance`
- ✅ `AttendanceModule.tsx` (338 lines) - Available at `/attendance`
- ✅ `RecruitmentModule.tsx` (517 lines) - Available at `/recruitment`
- ✅ `AdminDashboard.tsx` (552 lines) - Available at `/admin`
- ✅ `OnboardingModule.tsx` (753 lines) - Available at `/onboarding`
- ✅ `HomePage.tsx` (280 lines) - Available at `/`

## Current Architecture

```
frontend/src/
├── RouterApp.tsx          # NEW - Router entry point
├── App.tsx                # LEGACY - Monolithic app (still active)
├── main.tsx               # Updated to use RouterApp
├── pages/                 # NEW - Extracted page components
│   └── ComplianceModule.tsx
├── hooks/                 # NEW - Custom React hooks
│   ├── useAuth.ts
│   ├── useEmployees.ts
│   ├── useRecruitment.ts
│   └── useAttendance.ts
├── types/                 # EXPANDED - Shared TypeScript types
│   └── index.ts
└── utils/                 # EXPANDED - Shared utilities
    ├── api.ts             # NEW - fetchWithAuth helper
    └── exportToCSV.ts     # Existing
```

## Routing Coexistence Pattern

The migration uses a coexistence pattern where:
1. **New routes** (`/compliance`, etc.) render extracted page components
2. **Default route** (`*`) renders the existing `App.tsx`
3. Both can coexist during migration

This allows:
- ✅ Zero downtime migration
- ✅ Gradual feature extraction
- ✅ Easy rollback if needed
- ✅ Testing new architecture alongside old

## How to Add a New Page

1. **Extract the page component:**
   ```tsx
   // frontend/src/pages/MyNewPage.tsx
   import { User } from '../types'
   import { useNavigate } from 'react-router-dom'

   interface MyNewPageProps {
     user: User | null
   }

   export function MyNewPage({ user }: MyNewPageProps) {
     const navigate = useNavigate()
     // ... component logic
     return <div>My New Page</div>
   }
   ```

2. **Add route to RouterApp.tsx:**
   ```tsx
   <Route path="/my-new-page" element={<MyNewPage user={null} />} />
   ```

3. **Update App.tsx navigation** (temporary):
   ```tsx
   // Replace: setActiveSection('my-section')
   // With: window.location.href = '/my-new-page'
   ```

4. **Test the build:**
   ```bash
   cd frontend && npm run build
   ```

## Known Limitations

### Authentication
- Currently, the existing `App.tsx` manages auth state internally
- Extracted pages receive `user={null}` from RouterApp
- **Workaround:** Pages redirect to home if auth is required
- **Future:** Implement shared auth context or state management

### State Management
- Existing App.tsx uses 100+ useState calls
- Custom hooks reduce this but don't eliminate it
- **Future:** Consider React Context or Zustand for global state

### Navigation
- App.tsx uses `activeSection` state for navigation
- Extracted pages use React Router's `useNavigate`
- Both coexist during migration
- **Future:** Fully migrate to React Router navigation

## Testing Checklist

Before extracting a new page:
- [ ] Identify all state used by the section
- [ ] Create custom hooks for complex state logic
- [ ] Extract to page component
- [ ] Add route to RouterApp
- [ ] Test build: `npm run build`
- [ ] Test in browser (if dev server available)
- [ ] Update navigation in App.tsx

## Metrics

| Metric | Before Phase 2 | Current | Target |
|--------|---------------|---------|--------|
| App.tsx lines | 5,730 | 5,730* | <500 |
| Custom hooks | 1 | 5 | 8-10 |
| Page components | 0 | 1 | 8-12 |
| Router integrated | ❌ | ✅ | ✅ |

*App.tsx not yet reduced - extracted code lives in parallel during migration

## Next Steps

1. **Extract Attendance Module** - Self-contained, clear boundaries
2. **Extract Recruitment Module** - Large section, high value
3. **Create shared Auth Context** - Resolve auth state sharing
4. **Extract Admin Dashboard** - Complex but isolated
5. **Migrate remaining sections** - Incrementally over time

## References

- [React Router Docs](https://reactrouter.com/)
- [Phase 1 Summary](../PHASE1_COMPLETE.md)
- [Original App.tsx](./App.tsx) - 5,730 lines
