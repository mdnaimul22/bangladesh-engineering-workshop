/**
 * BEW Alpine.js Global Stores
 * 
 * Loaded on every page via base.html.
 * Individual page components are in alpine-components/*.js
 */

document.addEventListener('alpine:init', () => {

    // ── Sidebar Store ─────────────────────────────────────
    Alpine.store('sidebar', {
        open: false,
        toggle() { this.open = !this.open; },
        close()  { this.open = false; }
    });

    // ── Confirm Dialog Store ──────────────────────────────
    Alpine.store('confirm', {
        open: false,
        message: '',
        action: null,

        show(message, action) {
            this.message = message;
            this.action = action;
            this.open = true;
        },

        accept() {
            if (this.action) this.action();
            this.reset();
        },

        cancel() { this.reset(); },

        reset() {
            this.open = false;
            this.message = '';
            this.action = null;
        }
    });
});
