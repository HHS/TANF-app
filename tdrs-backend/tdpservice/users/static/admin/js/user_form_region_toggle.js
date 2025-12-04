document.addEventListener('DOMContentLoaded', function() {
    const groupSelect = document.querySelector('#id_groups');
    const regionFieldRow = document.querySelector('#id_regions').closest('.form-row, .field-box, .form-group');

    function toggleRegionField() {
        if (!groupSelect || !regionFieldRow) return;

        const selectedOptions = Array.from(groupSelect.selectedOptions).map(opt => opt.textContent.trim());
        const regionalRoles = ["OFA Regional Staff", "Developer"];

        const hasRegionalRole = selectedOptions.some(role => regionalRoles.includes(role));

        regionFieldRow.style.pointerEvents = hasRegionalRole ? 'auto' : 'none';
        regionFieldRow.style.opacity = hasRegionalRole ? '1.0' : '0.3';
    }

    if (groupSelect) {
        groupSelect.addEventListener('change', toggleRegionField);
        toggleRegionField(); // run on page load
    }
});