document.addEventListener('DOMContentLoaded', function() {
    const startDatePicker = flatpickr("#id_start_date", {
        dateFormat: "Y-m-d",
        locale: "ko", // Set locale to Korean
        clickOpens: false,
        onChange: function(selectedDates, dateStr, instance) {
            endDatePicker.set('minDate', dateStr);
        }
    });

    const endDatePicker = flatpickr("#id_end_date", {
        dateFormat: "Y-m-d",
        locale: "ko", // Set locale to Korean
        clickOpens: false,
        onChange: function(selectedDates, dateStr, instance) {
            const startDate = document.getElementById('id_start_date').value;
            if (selectedDates.length > 0 && new Date(dateStr) < new Date(startDate)) {
                alert("종료 날짜는 시작 날짜 이후여야 합니다. 다시 선택해주세요.");
                this.clear();
            }
        }
    });

    document.getElementById('id_start_date').addEventListener('click', function () {
        startDatePicker.open();
    });

    document.getElementById('id_end_date').addEventListener('click', function () {
        endDatePicker.open();
    });
});