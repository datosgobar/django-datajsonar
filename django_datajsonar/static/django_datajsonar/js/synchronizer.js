window.onload = function() {
    const frequency = document.getElementById('id_frequency');
    frequency.addEventListener("change", hideWeekDays);
    hideWeekDays();
};

function hideWeekDays() {
    const frequency = document.getElementById('id_frequency');
    const weekDays = document.getElementById('id_week_days');
    const weekDaysDiv = weekDays.parentElement.parentElement;
    const option = frequency.options[frequency.selectedIndex].text;

    if (option === 'week days') {
        weekDaysDiv.style.display = "";
    }

    if (option === 'every day') {
        const options = weekDays.options;
        for (let i = 0; i < options.length; i++) {
            options[i].selected = false;
        }

        weekDaysDiv.style.display = "none";
    }
}