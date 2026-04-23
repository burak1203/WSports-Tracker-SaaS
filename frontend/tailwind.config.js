/** @type {import('tailwindcss').Config} */
module.exports = {
  // İşte eksik olan hayat kurtarıcı satır burası:
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
