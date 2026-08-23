/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'ui-sans-serif', 'system-ui', 'sans-serif'],
      },
      colors: {
        glass: {
          border: 'rgba(255, 255, 255, 0.10)',
          surface: 'rgba(15, 23, 42, 0.45)',
          surfaceHover: 'rgba(15, 23, 42, 0.55)',
        }
      },
      keyframes: {
        shimmer: {
          '0%': { transform: 'translateX(-100%)' },
          '100%': { transform: 'translateX(100%)' }
        },
        aurora: {
          '0%, 100%': { transform: 'translate(0, 0) scale(1)' },
          '33%': { transform: 'translate(30px, -50px) scale(1.1)' },
          '66%': { transform: 'translate(-20px, 20px) scale(0.9)' },
        }
      },
      animation: {
        shimmer: 'shimmer 2s infinite',
        aurora: 'aurora 20s ease-in-out infinite',
      }
    },
  },
  plugins: [],
}
