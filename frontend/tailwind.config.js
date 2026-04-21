/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        ocean: {
          900: '#0B192C',
          800: '#1A365D',
          700: '#2A4365',
          600: '#2C5282',
          500: '#3182CE',
        },
        neon: {
          turquoise: '#00F0FF',
          blue: '#0070FF'
        },
        dark: {
          bg: '#050B14',
          surface: '#0A1526',
          border: '#1E2D4A'
        }
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      }
    },
  },
  plugins: [],
}
