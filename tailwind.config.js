/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./templates/**/*.html",
    "./apps/**/templates/**/*.html",
    "./static/**/*.js",
    "./apps/**/static/**/*.js",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#f0f4ff',
          100: '#e0e9ff',
          200: '#c7d7fe',
          300: '#a5b8fc',
          400: '#8194f8',
          500: '#6370f0',
          600: '#4f57e4',
          700: '#3e47c9',
          800: '#2d3ba3',
          900: '#1E3A8A',
        },
        accent: {
          50: '#ecfdf5',
          100: '#d1fae5',
          200: '#a7f3d0',
          300: '#6ee7b7',
          400: '#34d399',
          500: '#10B981',
          600: '#059669',
          700: '#047857',
          800: '#065f46',
          900: '#064e3b',
        },
        success: {
          500: '#10b981',
          600: '#059669'
        },
        warning: {
          500: '#f59e0b',
          600: '#d97706'
        },
        danger: {
          500: '#ef4444',
          600: '#dc2626'
        }
      },
      fontFamily: {
        sans: ['-apple-system', 'BlinkMacSystemFont', '"Segoe UI"', 'Roboto', '"Helvetica Neue"', 'Arial', 'sans-serif'],
      },
      boxShadow: {
        'brand': '0 4px 20px 0 rgba(30, 58, 138, 0.15)',
        'brand-lg': '0 10px 35px -3px rgba(30, 58, 138, 0.2)',
        'glow': '0 0 20px rgba(16, 185, 129, 0.15)',
        'soft': '0 2px 15px -3px rgba(0, 0, 0, 0.07), 0 10px 20px -2px rgba(0, 0, 0, 0.04)',
        'soft-lg': '0 10px 40px -3px rgba(0, 0, 0, 0.1), 0 20px 30px -10px rgba(0, 0, 0, 0.05)',
      },
      animation: {
        'fade-in-up': 'fadeInUp 0.6s ease-out',
        'scale-in': 'scaleIn 0.3s ease-out',
      },
      keyframes: {
        fadeInUp: {
          '0%': { opacity: '0', transform: 'translateY(20px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        scaleIn: {
          '0%': { opacity: '0', transform: 'scale(0.95)' },
          '100%': { opacity: '1', transform: 'scale(1)' },
        },
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
  ],
}
