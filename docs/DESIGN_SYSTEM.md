# HR Portal Design System

> **Based on OSS Scout Research**  
> **Recommended Stack:** shadcn/ui + Lucide Icons + Tailwind CSS + TanStack Table

---

## Research Sources (GitHub Repositories)

| Repository | Stars | License | Best For |
|-----------|-------|---------|----------|
| [shadcn/ui](https://github.com/shadcn-ui/ui) | 105,449 | MIT | Components |
| [Flowbite](https://github.com/themesberg/flowbite) | 9,081 | MIT | Forms, modals |
| [SaaS-Boilerplate](https://github.com/ixartz/SaaS-Boilerplate) | 6,740 | MIT | Dashboard layouts |
| [Lucide Icons](https://github.com/lucide-icons/lucide) | 20,769 | ISC | Icons |
| [Data Table Filters](https://github.com/openstatusHQ/data-table-filters) | 1,822 | MIT | Tables |
| [TailAdmin](https://github.com/TailAdmin/free-react-tailwind-admin-dashboard) | 1,070 | MIT | Admin UI |
| [Windmill Dashboard](https://github.com/estevanmaito/windmill-dashboard-react) | 1,050 | MIT | Accessibility |

---

## Color Palette

### Primary Colors
| Name | Hex | Usage |
|------|-----|-------|
| White | `#FFFFFF` | Primary background |
| Dark Blue | `#1e3a5f` | Text, headers, navigation |
| Green | `#10b981` | Icons (outline), success states, accents |
| Gray | `#6b7280` | Secondary text, borders |

### Secondary/Accent Colors
| Name | Hex | Usage |
|------|-----|-------|
| Teal | `#0891b2` | Candidate Pass, interview stages, bulk actions, shortlisted status |
| Blue | `#3b82f6` | Manager Pass template, links |

### Alert Colors
| Name | Hex | Usage |
|------|-----|-------|
| Red | `#ef4444` | Errors, critical alerts, delete actions |
| Yellow/Amber | `#f59e0b` | Warnings, pending states |

### Neutral Colors
| Name | Hex | Usage |
|------|-----|-------|
| Light Gray | `#f8fafc` | Background alternates |
| Border Gray | `#e2e8f0` | Dividers, input borders |

> **Note:** Purple was replaced with Teal for a more corporate professional appearance. Teal provides excellent contrast, is distinct from our green accents, and conveys professionalism appropriate for HR/corporate contexts.

---

## Typography

| Element | Size | Weight | Color |
|---------|------|--------|-------|
| Page Title | 24px (text-2xl) | 600 (semibold) | Dark Blue |
| Section Header | 18px (text-lg) | 600 (semibold) | Dark Blue |
| Body Text | 14px (text-sm) | 400 (normal) | Dark Blue |
| Caption | 12px (text-xs) | 400 (normal) | Gray |
| Button | 14px (text-sm) | 500 (medium) | White/Dark Blue |

---

## Icons

### Style
- **Type:** Outline/stroke only (no filled icons)
- **Stroke Width:** 1.5px
- **Default Color:** Green (`#10b981`)
- **Size:** 20px (w-5 h-5) for inline, 24px (w-6 h-6) for standalone

### Library
- **Primary:** Lucide Icons (`lucide-react`)
- **Backup:** Heroicons (`@heroicons/react/24/outline`)

### Usage Example
```tsx
import { User, Calendar, AlertCircle } from 'lucide-react'

// Standard icon usage
<User className="w-5 h-5 text-accent-green" strokeWidth={1.5} />

// Alert icon (red)
<AlertCircle className="w-5 h-5 text-accent-red" strokeWidth={1.5} />
```

---

## Components

### Buttons

| Variant | Background | Text | Border | Usage |
|---------|------------|------|--------|-------|
| Primary | Green | White | None | Main actions (Save, Submit) |
| Secondary | White | Dark Blue | Gray | Secondary actions (Cancel, Back) |
| Ghost | Transparent | Dark Blue | None | Tertiary actions |
| Danger | Red | White | None | Delete, destructive actions |

### Input Fields

- **Background:** White
- **Border:** 1px solid Border Gray
- **Focus:** Green border + subtle green shadow
- **Border Radius:** 8px (rounded-lg)
- **Padding:** 12px horizontal, 8px vertical

### Cards

- **Background:** White
- **Border:** 1px solid Border Gray
- **Border Radius:** 12px (rounded-xl)
- **Shadow:** sm (subtle)
- **Padding:** 16-24px

### Tables

- **Header:** Light Gray background, Dark Blue text, semibold
- **Rows:** White background, alternate Light Gray
- **Borders:** Border Gray between rows
- **Hover:** Very light gray highlight

---

## Spacing Scale

| Name | Value | Usage |
|------|-------|-------|
| xs | 4px | Icon gaps, tight spacing |
| sm | 8px | Between related items |
| md | 16px | Standard gaps |
| lg | 24px | Section spacing |
| xl | 32px | Large section gaps |
| 2xl | 48px | Page sections |

---

## Implementation

### Tailwind Config
```js
// tailwind.config.ts
export default {
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#f8fafc',
          100: '#f1f5f9',
          200: '#e2e8f0',
          600: '#475569',
          700: '#334155',
          800: '#1e293b',
          900: '#0f172a',
        },
        accent: {
          green: '#10b981',
          red: '#ef4444',
          amber: '#f59e0b',
          gray: '#6b7280',
        }
      }
    }
  }
}
```

### Component Installation (shadcn/ui)
```bash
# Initialize shadcn/ui
npx shadcn@latest init

# Add core components
npx shadcn@latest add button input select table card dialog alert badge tabs
```

---

## Best Practices

### Do's
- ✅ Use white backgrounds predominantly
- ✅ Use green only for icons and success states
- ✅ Keep icons outline-style only
- ✅ Maintain generous whitespace
- ✅ Use subtle shadows (sm only)
- ✅ Keep border radius consistent (lg for inputs, xl for cards)

### Don'ts
- ❌ Don't use filled/solid icons
- ❌ Don't use bright colors for backgrounds
- ❌ Don't use heavy shadows
- ❌ Don't mix icon libraries in same view
- ❌ Don't use gradients
- ❌ Don't use more than 3 colors in one component

---

## File Structure

```
frontend/src/
├── components/
│   └── ui/              # shadcn/ui components
│       ├── button.tsx
│       ├── input.tsx
│       ├── select.tsx
│       ├── table.tsx
│       ├── card.tsx
│       ├── dialog.tsx
│       ├── alert.tsx
│       └── ...
├── lib/
│   └── utils.ts         # shadcn/ui utilities
└── styles/
    └── globals.css      # Global styles + Tailwind imports
```

---

## References

- [shadcn/ui Documentation](https://ui.shadcn.com/docs)
- [Lucide Icons](https://lucide.dev/icons/)
- [Tailwind CSS](https://tailwindcss.com/docs)
- [Heroicons](https://heroicons.com/)
- [TanStack Table](https://tanstack.com/table/latest)
- [React Hook Form](https://react-hook-form.com/)
- [Flowbite React](https://flowbite.com/docs/getting-started/react/)

---

## Dashboard Layout Pattern

**Structure:** Fixed Sidebar + Sticky Header + Scrollable Content

```tsx
<div className="flex h-screen bg-white">
  {/* Fixed Sidebar */}
  <aside className="w-64 bg-slate-50 border-r border-slate-200">
    <nav className="p-4 space-y-2">
      {/* Navigation items */}
    </nav>
  </aside>
  
  {/* Main Content Area */}
  <div className="flex-1 flex flex-col">
    {/* Sticky Header */}
    <header className="h-16 bg-white border-b border-slate-200 sticky top-0 z-10">
      {/* User menu, notifications */}
    </header>
    
    {/* Scrollable Content */}
    <main className="flex-1 overflow-y-auto p-6">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {/* Metric cards */}
      </div>
    </main>
  </div>
</div>
```

---

## Employee Profile Card Pattern

```tsx
<div className="bg-white rounded-lg shadow-sm border border-slate-200 overflow-hidden">
  {/* Header with subtle gradient */}
  <div className="bg-gradient-to-r from-blue-50 to-slate-50 p-6">
    <div className="flex items-center space-x-4">
      <img 
        src={employee.avatarUrl} 
        alt={employee.name}
        className="w-20 h-20 rounded-full border-4 border-white shadow-md"
      />
      <div>
        <h2 className="text-2xl font-semibold text-slate-900">{employee.name}</h2>
        <p className="text-slate-600">{employee.jobTitle}</p>
        <span className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full">
          {employee.status}
        </span>
      </div>
    </div>
  </div>
  
  {/* Tab Navigation */}
  <div className="border-b border-slate-200">
    <nav className="flex space-x-8 px-6">
      <button className="border-b-2 border-green-500 py-3 text-green-600 font-medium">
        Overview
      </button>
      <button className="py-3 text-slate-600 hover:text-slate-900">
        Personal
      </button>
    </nav>
  </div>
</div>
```

---

## Data Table Pattern (TanStack Table)

```tsx
<div className="space-y-4">
  {/* Filter Toolbar */}
  <div className="flex items-center justify-between gap-4">
    <div className="relative flex-1 max-w-sm">
      <SearchIcon className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
      <input
        type="text"
        placeholder="Search employees..."
        className="pl-10 pr-4 py-2 w-full border border-slate-300 rounded-lg 
                   focus:ring-2 focus:ring-green-500 focus:border-transparent"
      />
    </div>
    
    <select className="border border-slate-300 rounded-lg px-4 py-2 
                       focus:ring-2 focus:ring-green-500 focus:border-transparent">
      <option value="">All Departments</option>
      <option value="HR">HR</option>
    </select>
  </div>
  
  {/* Table */}
  <div className="border border-slate-200 rounded-lg overflow-hidden">
    <table className="w-full">
      <thead className="bg-slate-50">
        <tr>
          <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase">
            Name
          </th>
        </tr>
      </thead>
      <tbody className="bg-white divide-y divide-slate-200">
        <tr className="hover:bg-slate-50 cursor-pointer">
          <td className="px-6 py-4 whitespace-nowrap">Employee Name</td>
        </tr>
      </tbody>
    </table>
  </div>
</div>
```

---

## Dashboard Metric Cards Pattern

```tsx
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
  <div className="bg-white p-6 rounded-lg border border-slate-200 hover:shadow-md transition-shadow">
    <div className="flex items-center justify-between mb-4">
      <div>
        <p className="text-sm text-slate-600 mb-1">Total Employees</p>
        <h3 className="text-3xl font-bold text-slate-900">247</h3>
      </div>
      <div className="p-3 bg-green-100 rounded-full">
        <UsersIcon className="w-6 h-6 text-green-600" />
      </div>
    </div>
    <div className="flex items-center text-sm">
      <span className="text-green-600 font-medium">+5%</span>
      <span className="text-slate-600 ml-2">vs last month</span>
    </div>
  </div>
</div>
```

---

## Status Badge Pattern

```tsx
const StatusBadge = ({ status }) => {
  const variants = {
    approved: 'bg-green-100 text-green-800 border-green-200',
    pending: 'bg-amber-100 text-amber-800 border-amber-200',
    rejected: 'bg-red-100 text-red-800 border-red-200',
    active: 'bg-blue-100 text-blue-800 border-blue-200',
  }
  
  return (
    <span className={`inline-flex items-center px-3 py-1 rounded-full 
                      text-xs font-medium border ${variants[status]}`}>
      {status === 'active' && (
        <span className="w-2 h-2 bg-blue-500 rounded-full mr-2 animate-pulse" />
      )}
      {status.charAt(0).toUpperCase() + status.slice(1)}
    </span>
  )
}
```

---

## Form Section Pattern

```tsx
<form className="space-y-8">
  <div className="bg-white p-6 rounded-lg border border-slate-200">
    <h3 className="text-lg font-semibold text-slate-900 mb-4">Leave Details</h3>
    
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      <div>
        <label className="block text-sm font-medium text-slate-700 mb-2">
          Leave Type <span className="text-red-500">*</span>
        </label>
        <select className="w-full px-4 py-2 border border-slate-300 rounded-lg 
                          focus:ring-2 focus:ring-green-500 focus:border-transparent">
          <option value="">Select type...</option>
        </select>
      </div>
    </div>
  </div>
  
  <div className="flex justify-end gap-4">
    <button type="button" className="px-6 py-2 border border-slate-300 text-slate-700 
                                      rounded-lg hover:bg-slate-50">
      Cancel
    </button>
    <button type="submit" className="px-6 py-2 bg-green-500 text-white rounded-lg 
                                      hover:bg-green-600">
      Submit
    </button>
  </div>
</form>
```

---

## Acknowledgments

UI patterns inspired by:
- [SaaS-Boilerplate](https://github.com/ixartz/SaaS-Boilerplate) (MIT)
- [TailAdmin](https://github.com/TailAdmin/free-react-tailwind-admin-dashboard) (MIT)
- [Flowbite](https://github.com/themesberg/flowbite) (MIT)
- [Data Table Filters](https://github.com/openstatusHQ/data-table-filters) (MIT)
- [shadcn/ui](https://ui.shadcn.com/) (MIT)
- [Windmill Dashboard](https://github.com/estevanmaito/windmill-dashboard-react) (MIT)
