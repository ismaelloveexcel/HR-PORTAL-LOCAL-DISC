import type { Config } from 'tailwindcss'

export default {
  content: ['./index.html', './src/**/*.{ts,tsx,jsx,js}'],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#f8fafc',   // Very light gray - backgrounds
          100: '#f1f5f9',  // Light gray - alternating rows
          200: '#e2e8f0',  // Border gray - dividers
          300: '#cbd5e1',  // Slightly darker for hover
          600: '#475569',  // Dark blue-gray - secondary text
          700: '#334155',  // Darker blue-gray
          800: '#1e293b',  // Very dark blue-gray - main text
          900: '#0f172a',  // Almost black - headers
        },
        accent: {
          green: '#10b981',    // Emerald for success/positive/icons
          red: '#ef4444',      // Red for errors/danger
          amber: '#f59e0b',    // Amber for warnings
          gray: '#6b7280',     // Gray for neutral/secondary
        },
      },
      fontFamily: {
        sans: ['Inter', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
      },
      borderRadius: {
        'input': '8px',   // For inputs
        'card': '12px',   // For cards
        'button': '8px',  // For buttons
      },
      boxShadow: {
        'card': '0 1px 3px rgba(0, 0, 0, 0.05)',
        'card-hover': '0 4px 6px rgba(0, 0, 0, 0.1)',
      },
    },
  },
  plugins: [],
} satisfies Config
