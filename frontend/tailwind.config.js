/** @type {import('tailwindcss').Config} */
module.exports = {
    content: [
        './app/**/*.{js,ts,jsx,tsx,mdx}',
        './components/**/*.{js,ts,jsx,tsx,mdx}',
    ],
    darkMode: 'class',
    theme: {
        extend: {
            colors: {
                // GravityWork brand colors
                gravity: {
                    50: '#f0f4ff',
                    100: '#e0e8ff',
                    200: '#c7d4fe',
                    300: '#a3b8fc',
                    400: '#7a94f9',
                    500: '#5a6df4',
                    600: '#4a4de8',
                    700: '#3f3dcd',
                    800: '#3534a5',
                    900: '#303283',
                    950: '#1e1d4d',
                },
            },
            animation: {
                'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
                'fade-in': 'fadeIn 0.5s ease-out',
                'slide-up': 'slideUp 0.3s ease-out',
            },
            keyframes: {
                fadeIn: {
                    '0%': { opacity: '0' },
                    '100%': { opacity: '1' },
                },
                slideUp: {
                    '0%': { transform: 'translateY(10px)', opacity: '0' },
                    '100%': { transform: 'translateY(0)', opacity: '1' },
                },
            },
        },
    },
    plugins: [],
}
