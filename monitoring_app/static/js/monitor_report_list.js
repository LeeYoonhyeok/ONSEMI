document.addEventListener('DOMContentLoaded', function() {
    var startDatePicker = flatpickr("#start_date", {
        locale: "ko",
        dateFormat: "Y-m-d",
        onChange: function(selectedDates, dateStr, instance) {
            if (selectedDates.length > 0) {
                endDatePicker.set('minDate', selectedDates[0]);
            }
        }
    });

    var endDatePicker = flatpickr("#end_date", {
        locale: "ko",
        dateFormat: "Y-m-d",
        onChange: function(selectedDates, dateStr, instance) {
            if (selectedDates.length > 0) {
                startDatePicker.set('maxDate', selectedDates[0]);
            }
        }
    });

    // Modal handling
    var modal = document.getElementById("reportModal");
    var span = document.getElementsByClassName("close")[0];

    document.querySelectorAll('.clickable-row').forEach(function(row) {
        row.addEventListener('click', function() {
            // Populate modal with data from data attributes
            var careType = this.dataset.careType;
            document.getElementById('reportType').textContent = careType;
            document.getElementById('reportTime').textContent = this.dataset.datetime;
            document.getElementById('visitTime').textContent = this.dataset.visit_date;
            document.getElementById('reportTitle').textContent = this.dataset.title;
            document.getElementById('reportContent').textContent = this.dataset.content;
            document.getElementById('reportAddress').textContent = this.dataset.address;

            var issues = '';
            if (this.dataset.noIssue === 'True') {
                issues = '특이사항 없음';
            } else {
                if (this.dataset.eye === 'True') issues += '눈 ';
                if (this.dataset.teeth === 'True') issues += '치아 ';
                if (this.dataset.skin === 'True') issues += '피부 ';
                if (this.dataset.back === 'True') issues += '허리 ';
                if (issues != '') issues += '진찰 필요';
                if (this.dataset.other === 'True') issues += "<br> + 기타 사항: " + this.dataset.otherText;
            }
            if (issues === '') issues = '특이사항 없음';
            document.getElementById('reportIssues').innerHTML = issues;

            var imagesDiv = document.getElementById('reportImages');
            imagesDiv.innerHTML = '';
            var images = this.dataset.images.split(',');
            images.forEach(function(imageUrl) {
                if (imageUrl) {
                    var imgElement = document.createElement('img');
                    imgElement.src = imageUrl;
                    imgElement.alt = 'Report Image';
                    imgElement.className = 'report-image';  // 클래스 추가
                    imagesDiv.appendChild(imgElement);
                }
            });

            var parkinsonDiagnosis = this.dataset.parkinsonDiagnosis === 'True';
            if (parkinsonDiagnosis) {
                document.getElementById('parkinsonDiv').style.display = 'block';
                document.getElementById('reportParkinson').textContent = this.dataset.audioTestResult;
            } else {
                document.getElementById('parkinsonDiv').style.display = 'none';
            }
                                
            if (careType === '방문') {
                document.getElementById('doctorOpinionDiv').style.display = 'none';
                document.getElementById('reportDoctorOpinion').style.display = 'none';
            } else {  
                var doctorOpinion = this.dataset.doctorOpinion;     
                document.getElementById('doctorOpinionDiv').style.display = 'inline';                 
                if (doctorOpinion === 'None' || doctorOpinion == '') {
                    document.getElementById('reportDoctorOpinion').textContent = '의사소견 없음';
                } else {
                    document.getElementById('reportDoctorOpinion').textContent = doctorOpinion;
                }
            }

            var userRequest = this.dataset.userRequest;
            if (userRequest === 'None' || userRequest == '') {
                document.getElementById('reportUserRequest').textContent = '전달사항 없음';
            } else {
                document.getElementById('reportUserRequest').textContent = userRequest;
            }

            // Show modal
            modal.style.display = "block";
            document.body.classList.add('modal-open');
        });
    });

    span.onclick = function() {
        modal.style.display = "none";
        document.body.classList.remove('modal-open');
    }

    window.onclick = function(event) {
        if (event.target == modal) {
            modal.style.display = "none";
            document.body.classList.remove('modal-open');
        }
    }

    window.closeModal = function() {
        modal.style.display = "none";
        document.body.classList.remove('modal-open');
    }
});