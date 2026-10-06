document.addEventListener('DOMContentLoaded', function() {
    const typeSelect = document.querySelector('#id_type');
    const percentageInput = document.querySelector('#id_rollout_percentage');

    if (!typeSelect || !percentageInput) return;

    const percentageFieldRow = percentageInput.closest('.form-row, .field-box, .form-group');
    if (!percentageFieldRow) return;

    function togglePercentageField() {
        const usesPercentage = typeSelect.value === 'random_rollout';
        percentageFieldRow.hidden = !usesPercentage;
        percentageInput.required = usesPercentage;

        if (!usesPercentage) percentageInput.value = '';
    }

    typeSelect.addEventListener('change', togglePercentageField);
    togglePercentageField();
});
