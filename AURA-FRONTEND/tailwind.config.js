/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        bg: '#040712',
        surface: '#0a1022',
        surface2: '#0e162e',
        sidebar: '#070c1a',
        border: '#1e2a50',
        'border-accent': 'rgba(108, 63, 229, 0.4)',
        purple: '#6c3fed',
        'purple-l': '#8b5cf6',
        blue: '#3b82f6',
        cyan: '#22d3ee',
        green: '#10b981',
        amber: '#f59e0b',
        text: '#f1f5f9',
        'text-m': '#94a3b8',
        'text-d': '#475569',
      },
      backgroundColor: {
        DEFAULT: '#040712',
      },
      textColor: {
        DEFAULT: '#f1f5f9',
      },
      borderColor: {
        DEFAULT: '#1e2a50',
      },
      fontFamily: {
        sans: ['Inter', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'sans-serif'],
        mono: ['"Courier New"', 'monospace'],
      },
      boxShadow: {
        'aura-sm': '0 2px 8px rgba(0, 0, 0, 0.4)',
        'aura': '0 4px 16px rgba(0, 0, 0, 0.4)',
        'aura-lg': '0 8px 24px rgba(0, 0, 0, 0.4)',
        'aura-xl': '0 16px 32px rgba(0, 0, 0, 0.4)',
      },
      borderRadius: {
        'aura': '14px',
      },
    },
  },
  plugins: [],
};
