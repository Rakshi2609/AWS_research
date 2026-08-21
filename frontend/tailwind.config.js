/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        healthy: {
          light: '#dcfce7',
          DEFAULT: '#16a34a',
          dark: '#14532d'
        },
        water: {
          light: '#fee2e2',
          DEFAULT: '#dc2626',
          dark: '#7f1d1d'
        },
        nutrient: {
          light: '#fef9c3',
          DEFAULT: '#ca8a04',
          dark: '#713f12'
        },
        disease: {
          light: '#f3e8ff',
          DEFAULT: '#9333ea',
          dark: '#581c87'
        }
      }
    },
  },
  plugins: [],
}
