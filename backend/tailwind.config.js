module.exports = {
    content: [
        "./templates/**/*.{html,js}",
        "./static/js/**/*.{js,ts}",
        "./static/css/**/*.css",
        "./node_modules/flowbite/**/*.js"
    ],
    safelist: [],
    mode: 'jit',
    theme: {
        extend: {
            colors: {
                primary: {
                    50: '#e3f2fd',    // Lightest shade
                    100: '#bbdefb',
                    200: '#90caf9',
                    300: '#64b5f6',
                    400: '#42a5f5',
                    500: '#2196f3',   // Base color
                    600: '#1e88e5',
                    700: '#1976d2',
                    800: '#1565c0',
                    900: '#0d47a1',    // Darkest shade
                },
                secondary: {
                    50: '#f5f7fa',
                    100: '#e1e6ed',
                    200: '#c0c9d6',
                    300: '#9aa3bb',
                    400: '#7b8b9e',
                    500: '#5a6a7e',
                    600: '#475364',
                    700: '#3c4654',
                    800: '#2e3643',
                    900: '#212933',
                },
                success: {
                    50: '#e8f5e9',
                    100: '#c8e6c9',
                    200: '#a5d6a7',
                    300: '#81c784',
                    400: '#66bb6a',
                    500: '#4caf50',    // Base color
                    600: '#43a047',
                    700: '#388e3c',
                    800: '#2c6e2f',
                    900: '#1b5e20',
                },
                info: {
                    50: '#e0f7fa',
                    100: '#b2ebf2',
                    200: '#80deea',
                    300: '#4dd0e1',
                    400: '#26c6da',
                    500: '#00bcd4',
                    600: '#00acc1',
                    700: '#0097a7',
                    800: '#00838f',
                    900: '#006064',
                },
                warning: {
                    50: '#fff3e0',
                    100: '#ffe0b2',
                    200: '#ffcc80',
                    300: '#ffb74d',
                    400: '#ffa726',
                    500: '#ff9800',
                    600: '#fb8c00',
                    700: '#f57c00',
                    800: '#ef6c00',
                    900: '#e65100',
                },
                danger: {
                    50: '#ffebee',
                    100: '#ffcdd2',
                    200: '#ef9a9a',
                    300: '#e57373',
                    400: '#ef5350',
                    500: '#f44336',    // Base color
                    600: '#e53935',
                    700: '#d32f2f',
                    800: '#c62828',
                    900: '#b71c1c',
                },
            },
        },
        container: {
            padding: {
                DEFAULT: '1rem',
                sm: '2rem',
                lg: '4rem',
                xl: '5rem',
                '2xl': '6rem',
            },
        },

    },
    variants: {},
    plugins: [
        require('tailwindcss'),
        require('autoprefixer'),
        require('flowbite/plugin')
    ],
}
