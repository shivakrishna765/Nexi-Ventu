/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx,ts,tsx}'],
  theme: {
    extend: {
      colors: {
        nx: {
          bg: '#05040b',
          panel: '#0d1222',
          panel2: '#15192f',
          accent: '#8b5cf6',
          cyan: '#22d3ee'
        }
      },
      boxShadow: {
        glow: '0 0 35px rgba(139,92,246,0.25)',
        card: '0 8px 30px rgba(2, 6, 23, 0.6)'
      },
      backdropBlur: {
        xs: '2px'
      }
    }
  },
  plugins: []
};
