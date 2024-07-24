document.getElementById('findIdForm').addEventListener('submit', function(event) {
    event.preventDefault();
    var form = event.target;
    var formData = new FormData(form);

    fetch(form.action, {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': '{{ csrf_token }}' // CSRF 토큰을 헤더에 추가
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('당신의 아이디는: ' + data.username);
            window.location.href = '/user/login/';
        } else {
            alert('이메일을 다시 확인해주세요.');
        }
    })
    .catch(error => console.error('Error:', error));
});