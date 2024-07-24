document.getElementById('resetPasswordForm').addEventListener('submit', function(event) {
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
        var messageDiv = document.getElementById('message');
        if (data.success) {
            alert('비밀번호가 성공적으로 변경되었습니다.');
            window.location.href = '/user/login/';
        } else {
            messageDiv.textContent = data.message;
        }
    })
    .catch(error => console.error('Error:', error));
});