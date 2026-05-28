/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          dark: "#0b0f19",
          slate: "#1e293b",
          lightslate: "#334155",
          teal: "#0d9488",
          emerald: "#10b981",
          gold: "#f59e0b",
          rose: "#f43f5e",
          purple: "#8b5cf6"
        }
      },
      fontFamily: {
        sans: ["Outfit", "Inter", "sans-serif"]
      }
    },
  },
  plugins: [],
}
