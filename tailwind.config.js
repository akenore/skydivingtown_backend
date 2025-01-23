/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class',
  content: [
    './templates/**/*.html',
    './templates/event/**/*.html',
    './templates/secure/**/*.html',
    './templates/contract/**/*.html',
    './node_modules/flowbite/**/*.js',
    './config/**/*.py',
    './contract/**/*.py',
    './public/**/*.py',
    './event/**/*.py',
    './secure/**/*.py',
  ],
  theme: {
    extend: {},
  },
  plugins: [require('flowbite/plugin')],
}

