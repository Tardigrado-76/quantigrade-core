module.exports = {
    darkMode: 'class',
    content: ["./*.{html,js}"],
    theme: {
        extend: {
            colors: {
                qg: {
                    bg: '#0B0F19',
                    card: '#111827',
                    cardglass: 'rgba(17, 24, 39, 0.7)',
                    border: '#1F2937',
                    cyan: '#06B6D4',
                    green: '#10B981',
                    textmain: '#E5E7EB',
                    textmuted: '#9CA3AF'
                }
            },
            fontFamily: {
                sans: ['Inter', 'sans-serif'],
                mono: ['JetBrains Mono', 'monospace'],
            },
            animation: {
                'pulse-fast': 'pulse 1.5s cubic-bezier(0.4, 0, 0.6, 1) infinite',
            }
        }
    }
}
