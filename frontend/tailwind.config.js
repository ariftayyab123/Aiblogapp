/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      fontFamily: {
        // Editorial pairing: Libre Bodoni for display, Public Sans for everything else.
        display: ['"Libre Bodoni"', 'Georgia', 'Cambria', 'serif'],
        sans: [
          '"Public Sans"',
          'ui-sans-serif',
          'system-ui',
          '-apple-system',
          '"Segoe UI"',
          'Roboto',
          'Helvetica',
          'Arial',
          'sans-serif',
        ],
      },
      colors: {
        // Editorial black — the primary surface/text scale.
        ink: {
          50: '#FAFAFA',
          100: '#F4F4F5',
          200: '#E4E4E7',
          300: '#D4D4D8',
          400: '#A1A1AA',
          500: '#71717A',
          600: '#52525B',
          700: '#3F3F46',
          800: '#27272A',
          900: '#18181B',
          950: '#09090B',
        },
        // Accent pink — emphasis marks, active states, CTA detail.
        accent: {
          50: '#FDF2F8',
          100: '#FCE7F3',
          200: '#FBCFE8',
          300: '#F9A8D4',
          400: '#F472B6',
          500: '#EC4899',
          600: '#DB2777',
          700: '#BE185D',
          800: '#9D174D',
          900: '#831843',
        },
        paper: {
          DEFAULT: '#FAFAFA',
          card: '#FFFFFF',
          muted: '#E8ECF0',
        },
      },
      maxWidth: {
        // Home / blog-list override: narrow, focused reading measure.
        measure: '800px',
        // Article body: 72 characters per line (spec asks for 65-75).
        article: '72ch',
        // Public share page frame.
        shared: '1200px',
        // Data-dense views (analytics, blog detail chrome).
        wide: '1400px',
      },
      zIndex: {
        // Explicit scale, per the blog-list page spec: no arbitrary values.
        dropdown: '10',
        sticky: '20',
        nav: '30',
        overlay: '50',
        // One step above the modal scrim so confirmations stay visible.
        toast: '60',
      },
      boxShadow: {
        'e-sm': '0 1px 2px rgba(0,0,0,0.05)',
        'e-md': '0 4px 6px rgba(0,0,0,0.1)',
        'e-lg': '0 10px 15px rgba(0,0,0,0.1)',
        'e-xl': '0 20px 25px rgba(0,0,0,0.15)',
      },
    },
  },
  plugins: [
    require('@tailwindcss/typography'),
  ],
}
