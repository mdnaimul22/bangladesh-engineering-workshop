/**
 * BEW Theme Switcher — Alpine.js Store
 * 
 * Manages light/dark/matrix theme switching with localStorage persistence.
 * Loaded on every page via base.html.
 */

document.addEventListener('alpine:init', () => {
    Alpine.store('theme', {
        current: localStorage.getItem('bew-theme') || 'light',

        options: [
            'light', 'dark', 'matrix', 
            'pure-white', 'matte-white', 'cream', 
            'matte-black', 'black-brown', 'jam-black', 
            'jam-navy', 'block-white'
        ],

        init() {
            this.apply(this.current);
        },

        toggle() {
            const idx = this.options.indexOf(this.current);
            const next = this.options[(idx + 1) % this.options.length];
            this.apply(next);
        },

        apply(theme) {
            this.current = theme;
            document.documentElement.setAttribute('data-theme', theme);
            localStorage.setItem('bew-theme', theme);
        },

        get icon() {
            const icons = { 
                light: 'light_mode', 
                dark: 'dark_mode', 
                matrix: 'terminal',
                'pure-white': 'cloud',
                'matte-white': 'auto_awesome',
                'cream': 'local_cafe',
                'matte-black': 'developer_mode',
                'black-brown': 'bloodtype',
                'jam-black': 'space_dashboard',
                'jam-navy': 'waves',
                'block-white': 'category'
            };
            return icons[this.current] || 'palette';
        },

        get label() {
            const labels = { 
                light: 'Light', 
                dark: 'Dark', 
                matrix: 'Matrix',
                'pure-white': 'Pure White',
                'matte-white': 'Matte White',
                'cream': 'Cream',
                'matte-black': 'Matte Black',
                'black-brown': 'Black Brown',
                'jam-black': 'Jam Black',
                'jam-navy': 'Jam Navy',
                'block-white': 'Block White'
            };
            return labels[this.current] || 'Custom';
        }
    });
});
