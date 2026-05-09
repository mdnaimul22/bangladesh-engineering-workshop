// BEW Legacy Script — Retained behaviors only
// Sidebar toggle and theme switching are now handled by Alpine.js stores.

document.addEventListener('DOMContentLoaded', function () {

    // Search input focus effect
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('focus', function () {
            this.parentElement.classList.add('focused');
        });

        searchInput.addEventListener('blur', function () {
            this.parentElement.classList.remove('focused');
        });
    }

    // Add smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                e.preventDefault();
                target.scrollIntoView({ behavior: 'smooth' });
            }
        });
    });

    // Mobile phone link - add tel: prefix
    document.querySelectorAll('.mobile-link').forEach(link => {
        if (!link.href.startsWith('tel:')) {
            const phone = link.textContent.trim().replace(/[^\d]/g, '');
            if (phone) {
                link.href = 'tel:' + phone;
            }
        }
    });

    // Toggle New Category Input in Shop Form
    const categorySelect = document.getElementById('category_id');
    const newCategoryInput = document.getElementById('new_category_name');

    if (categorySelect && newCategoryInput) {
        categorySelect.addEventListener('change', function () {
            if (this.value === 'new') {
                newCategoryInput.style.display = 'block';
                newCategoryInput.required = true;
                newCategoryInput.focus();
            } else {
                newCategoryInput.style.display = 'none';
                newCategoryInput.required = false;
            }
        });

        // Run on load (in case of validation error return)
        if (categorySelect.value === 'new') {
            newCategoryInput.style.display = 'block';
            newCategoryInput.required = true;
        }
    }
});
