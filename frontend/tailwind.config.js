/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        uknf: {
          blue: '#003DA5',
          'blue-light': '#0051C8',
          'blue-dark': '#002976',
        },
      },
    },
  },
  plugins: [],
}

