/**
 * BEW Dynamic Form Rows — Alpine.js Component
 * 
 * Replaces ALL inline "add row / remove row" scripts across:
 * - work_order_form.html (parts)
 * - purchase_form.html (items)
 * - sale_form.html (items)
 * - buyer_form.html (contacts)
 * 
 * Usage:
 *   <div x-data="dynamicRows({ templateId: 'part-template', minRows: 1 })">
 *       <div x-ref="container">...existing rows...</div>
 *       <button type="button" @click="addRow()">Add</button>
 *   </div>
 */

document.addEventListener('alpine:init', () => {
    Alpine.data('dynamicRows', (config = {}) => ({
        templateId: config.templateId || '',
        containerRef: config.containerRef || 'container',
        minRows: config.minRows || 1,
        onChangeCallback: config.onChange || null,

        addRow() {
            const template = document.getElementById(this.templateId);
            if (!template) return;
            const clone = template.content.cloneNode(true);
            this.$refs[this.containerRef].appendChild(clone);
            this.reindex();
            this.notifyChange();
        },

        removeRow(event) {
            const row = event.target.closest('[data-row]');
            if (!row) return;
            const container = this.$refs[this.containerRef];

            if (container.querySelectorAll('[data-row]').length > this.minRows) {
                row.remove();
            } else {
                // Clear the last row instead of removing it
                row.querySelectorAll('input:not([type=hidden]):not([type=file])').forEach(
                    i => i.value = ''
                );
                row.querySelectorAll('input[type=file]').forEach(i => i.value = '');
                row.querySelectorAll('input[type=hidden]').forEach(i => i.value = '');
                row.querySelectorAll('select').forEach(s => s.selectedIndex = 0);
            }
            this.reindex();
            this.notifyChange();
        },

        reindex() {
            const rows = this.$refs[this.containerRef].querySelectorAll('[data-row]');
            rows.forEach((row, idx) => {
                row.querySelectorAll('input[type=file]').forEach(f => {
                    f.name = f.name.replace(/_\d+$/, `_${idx}`);
                });
            });
        },

        notifyChange() {
            if (typeof this.onChangeCallback === 'function') {
                this.onChangeCallback();
            }
        }
    }));
});

/**
 * BEW Cost Calculator — Alpine.js Component
 * Used by work_order_form to calculate material + labor costs.
 */
document.addEventListener('alpine:init', () => {
    Alpine.data('costCalculator', (initialData = {}) => ({
        laborCost: parseFloat(initialData.laborCost) || 0,
        materialCost: parseFloat(initialData.materialCost) || 0,

        get totalCost() {
            return this.laborCost + this.materialCost;
        },

        recalculate() {
            let sum = 0;
            this.$root.querySelectorAll('.js-part-price').forEach(input => {
                sum += parseFloat(input.value) || 0;
            });
            this.materialCost = sum;
        },

        formatCurrency(value) {
            return new Intl.NumberFormat('en-BD', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            }).format(value);
        }
    }));
});
