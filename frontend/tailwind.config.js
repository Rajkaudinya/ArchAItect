/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  // CRITICAL: disable dark mode completely so Tailwind never injects dark: overrides
  darkMode: false,
  theme: {
    extend: {
      colors: {
        // Ocean Voltage palette — matches CSS variables
        cyan: {
          DEFAULT: '#00d4e8',
          deep:    '#00a8be',
          soft:    '#e0f9fc',
          mid:     '#b3f0f7',
        },
        coral: {
          DEFAULT: '#ff5c5c',
          deep:    '#e03e3e',
          soft:    '#fff0f0',
        },
        gold: {
          DEFAULT: '#f7b731',
          soft:    '#fff8e6',
        },
        violet: {
          DEFAULT: '#7c3aed',
          soft:    '#f3f0ff',
        },
        emerald: {
          DEFAULT: '#00c875',
          soft:    '#e6fff4',
        },
        ink: {
          DEFAULT: '#0a0f1e',
          mid:     '#1e293b',
          light:   '#334155',
        },
        surface: {
          base:    '#eef2f7',
          panel:   '#ffffff',
          raised:  '#f7fafc',
          deep:    '#e4eaf3',
        },
      },
      fontFamily: {
        display: ['Syne', 'sans-serif'],
        body:    ['DM Sans', 'sans-serif'],
        mono:    ['JetBrains Mono', 'monospace'],
      },
      boxShadow: {
        'cyan-glow':  '0 0 24px rgba(0,212,232,0.25)',
        'coral-glow': '0 0 20px rgba(255,92,92,0.2)',
        'panel':      '0 4px 24px rgba(0,0,0,0.07), 0 1px 4px rgba(0,0,0,0.04)',
        'panel-lg':   '0 8px 40px rgba(0,0,0,0.1), 0 2px 8px rgba(0,0,0,0.05)',
      },
      backgroundImage: {
        'ocean-gradient': 'linear-gradient(135deg, #eef2f7 0%, #f0f9ff 50%, #f5f0ff 100%)',
        'cyan-gradient':  'linear-gradient(135deg, #00d4e8 0%, #00b8d4 100%)',
        'coral-gradient': 'linear-gradient(135deg, #ff5c5c 0%, #e83e3e 100%)',
      },
    },
  },
  plugins: [],
}