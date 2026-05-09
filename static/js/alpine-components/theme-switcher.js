/**
 * BEW Theme Switcher — Alpine.js Store
 * 
 * Manages light/dark/matrix theme switching with localStorage persistence.
 * Loaded on every page via base.html.
 */

document.addEventListener('alpine:init', () => {
    Alpine.store('theme', {
        current: localStorage.getItem('bew-theme') || 'light',

        options: ['light', 'dark', 'matrix'],

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
            const icons = { light: 'light_mode', dark: 'dark_mode', matrix: 'terminal' };
            return icons[this.current] || 'light_mode';
        },

        get label() {
            const labels = { light: 'Light', dark: 'Dark', matrix: 'Matrix' };
            return labels[this.current] || 'Light';
        }
    });
});
