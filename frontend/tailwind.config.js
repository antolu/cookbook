/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx,css}'],
  safelist: [
    // Specific utilities
    'bg-white',
    'bg-black',
    'text-white',
    'text-black',
    'border-white',

    // Common named colors and primitives (covered by patterns below as well)
    'bg-primary-600',
    'hover:bg-primary-700',

    // Broader patterns to cover utilities used only via @apply
    { pattern: /^(bg|text|from|to|border)-/ },
    { pattern: /^(p|px|py|pt|pr|pb|pl|m|mx|my|mt|mr|mb|ml)-/ },
    { pattern: /^rounded/ },
    { pattern: /^font-/ },
    { pattern: /^gap-/ },
    { pattern: /^w-/ },
    { pattern: /^h-/ },
    { pattern: /^min-w-/ },
    { pattern: /^max-w-/ },
    { pattern: /^text-/ },
    { pattern: /^hover:/ },
    { pattern: /^focus:/ },
    { pattern: /^transition/ },
    { pattern: /^duration-/ },
    { pattern: /^animate-/ },
    { pattern: /^line-clamp-/ },
    // Explicit utilities used via @apply in src/index.css
    'px-4',
    'py-2',
    'px-3',
    'py-1.5',
    'px-6',
    'py-3',
    'px-8',
    'py-4',
    'p-4',
    'px-2.5',
    'py-0.5',
    'rounded-md',
    'rounded-lg',
    'rounded-full',
    'font-medium',
    'font-semibold',
    'w-full',
    'border',
    'shadow-sm',
    'transition-colors',
    'duration-200',
    'focus:outline-none',
    'focus:ring-2',
    'focus:ring-offset-2',
    'focus:ring-primary-500',
    'focus:ring-primary-500',
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        serif: ['Playfair Display', 'Georgia', 'serif'],
      },
      colors: {
        primary: {
          50: '#f0f9ff',
          100: '#e0f2fe',
          200: '#bae6fd',
          300: '#7dd3fc',
          400: '#38bdf8',
          500: '#0ea5e9',
          600: '#0284c7',
          700: '#0369a1',
          800: '#075985',
          900: '#0c4a6e',
        },
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-in-out',
        'slide-in': 'slideIn 0.3s ease-out',
        'zoom-in': 'zoomIn 0.2s ease-out',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideIn: {
          '0%': { transform: 'translateY(10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        zoomIn: {
          '0%': { transform: 'scale(0.95)', opacity: '0' },
          '100%': { transform: 'scale(1)', opacity: '1' },
        },
      },
    },
  },
  plugins: [],
};
