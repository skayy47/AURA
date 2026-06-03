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
        bg: '#030712',
        'bg-2': '#050816',
        'bg-3': '#0a0b0f',
        surface: '#070d1c',
        surface2: '#0b1426',
        sidebar: '#050a16',
        border: '#16233f',
        'border-accent': 'rgba(0, 229, 255, 0.32)',
        purple: '#8b5cf6',
        'purple-l': '#a78bfa',
        blue: '#3b82f6',
        cyan: '#00e5ff',
        mint: '#00ffb2',
        green: '#00ffb2',
        amber: '#f59e0b',
        text: '#f8fafc',
        'text-m': '#94a3b8',
        'text-d': '#4a5878',
        aurora: {
          purple: '#8b5cf6',
          cyan: '#00e5ff',
          blue: '#3b82f6',
          pink: '#00ffb2',
        },
      },
      backgroundColor: {
        DEFAULT: '#030712',
      },
      textColor: {
        DEFAULT: '#f8fafc',
      },
      borderColor: {
        DEFAULT: '#16233f',
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
        'neon-purple': '0 0 24px rgba(108, 63, 237, 0.55)',
        'neon-cyan': '0 0 24px rgba(34, 211, 238, 0.55)',
        'neon-mix': '0 0 20px rgba(108, 63, 237, 0.45), 0 0 40px rgba(34, 211, 238, 0.25)',
      },
      borderRadius: {
        'aura': '14px',
      },
      keyframes: {
        'aurora-shift': {
          '0%, 100%': { transform: 'translate3d(0, 0, 0) rotate(0deg)' },
          '50%': { transform: 'translate3d(-4%, 3%, 0) rotate(4deg)' },
        },
        'wave-slide': {
          from: { transform: 'translateX(0)' },
          to: { transform: 'translateX(-50%)' },
        },
        'squiggle-dance': {
          to: { 'stroke-dashoffset': '-40' },
        },
        'road-flow': {
          to: { 'stroke-dashoffset': '0' },
        },
        'node-pulse': {
          '0%, 100%': { transform: 'scale(1)', opacity: '0.65' },
          '50%': { transform: 'scale(1.4)', opacity: '0' },
        },
        'loader-dash': {
          '0%': { 'stroke-dashoffset': '500' },
          '100%': { 'stroke-dashoffset': '0' },
        },
        'vehicle-travel': {
          '0%': { offsetDistance: '0%' },
          '100%': { offsetDistance: '100%' },
        },
      },
      animation: {
        aurora: 'aurora-shift 40s ease-in-out infinite',
        'wave-slow': 'wave-slide 28s linear infinite',
        'wave-mid': 'wave-slide 22s linear infinite',
        'wave-fast': 'wave-slide 18s linear infinite',
        squiggle: 'squiggle-dance 3s linear infinite',
        road: 'road-flow 800ms ease-out forwards',
        'pulse-ring': 'node-pulse 2.2s ease-out infinite',
        'loader-dash': 'loader-dash 2.5s ease-in-out infinite',
      },
    },
  },
  plugins: [],
};
