// 모달 정보
function openModal(title, careType, requestDate, visitDate, visitTime, careState, content, seniors, username, careId) {
    document.getElementById('modal').style.display = 'block';
    document.getElementById('modal-care-type').textContent = careType;
    document.getElementById('modal-request-date').textContent = requestDate;
    document.getElementById('modal-title').textContent = title;
    document.getElementById('modal-care-content').textContent = content.replace(/\\n/g, '\n');
    document.getElementById('modal-username').textContent = username;
    document.getElementById('modal-seniors').textContent = seniors;
    document.getElementById('modal-care-state').textContent = careState;

    const deleteForm = document.getElementById('delete-form');
    deleteForm.action = `/management/care/delete/${careId}/`;

    if (careState === '요청 승인 대기') {
        var editButton = document.getElementById('edit-button');
        var deleteButton = document.getElementById('delete-button');
        editButton.style.display = 'block';
        deleteButton.style.display = 'block';
        editButton.onclick = function() {
            window.location.href = '/management/care/update/' + careId + '/';
        };
        document.getElementById('modal-content').style.height = 'auto'; // 모달 크기 조정
    } else {
        document.getElementById('edit-button').style.display = 'none';
        document.getElementById('delete-button').style.display = 'none';
        document.getElementById('modal-content').style.height = '80%'; // 기본 모달 크기
    }
}

function closeModal() {
    document.getElementById('modal').style.display = 'none';
}

function openPhotoModal(imageUrl) {
    document.getElementById('photo-modal-content').innerHTML = `<img src="${imageUrl}" alt="Report Image">`;
    document.getElementById('photoModal').style.display = 'block';
}

function closePhotoModal() {
    document.getElementById('photoModal').style.display = 'none';
}