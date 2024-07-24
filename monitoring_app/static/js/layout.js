$(document).ready(function() {
    function handleSignal(username, seniorname, state, visit_date, visit_time) {
        if(state === 'APPROVED'){
            state = '요청 승인 완료';
        } else if(state === 'NOT_APPROVED'){
            state = '요청 승인 대기';
        } else if(state === 'COMPLETED'){
            state = '요청 처리 완료';
        } else{
            state = '알 수 없음';
        }

        // 시그널을 받았을 때 메시지를 표시할 HTML 요소 업데이트
        const message = seniorname + ' 어르신 서비스 요청이 ' + state + ' 되었습니다. 방문 예정 날짜는 ' + visit_date + ' ' + visit_time + ' 입니다.';
        var temp = document.getElementById("signal-message1").textContent;
        console.log(temp);
        if(temp === '알림이 없습니다.'){
            console.log('여기1:', temp); // Debug message
            $('#signal-message1').text(message);
            // 알림 아이콘 변경
            $('#notification-icon').text('notifications_unread');
        } else{
            console.log('여기2:', temp); // Debug message
            $('#signal-message2').text('');
            $('#notification-icon').text('notifications_unread');
        }
        localStorage.setItem('signalMessage', message);
        console.log('Signal handled and stored:', temp); // Debug message
    }
    function pollSignal() {
        $.ajax({
            url: '/monitoring/family_monitor/poll_signal/',
            type: 'GET',
            success: function(data) {
                if (data.signal_received && typeof data.username !== 'undefined') {
                    handleSignal(data.username, data.seniorname, data.state, data.visit_date, data.visit_time);
                }
            },
            error: function(jqXHR, textStatus, errorThrown) {
                console.log('Error polling for signal:', textStatus, errorThrown);
            },
            complete: function() {
                setTimeout(pollSignal, 10000);  // 10초마다 시그널 체크
            }
        });
    }

    pollSignal();

    // Display the message from localStorage if it exists
    const storedMessage = localStorage.getItem('signalMessage');
    if (storedMessage) {
        $('#signal-message1').text(storedMessage);
        $('#notification-icon').text('notifications_unread');
        console.log('Loaded message from localStorage:', storedMessage); // Debug message
    }

    // Clear the message on "X" button click
    $('.close-button').click(function() {
        $('#signal-message1').text('알림이 없습니다.');
        $('#signal-message2').text('');
        $('#notification-icon').text('notifications');
        localStorage.removeItem('signalMessage');
        console.log('Message cleared'); // Debug message
    });

    // Chatbot functionality
    const chatLink = document.getElementById('chat-link');
    const chatModal = document.getElementById('chatModal');
    const closeChat = document.getElementById('closeChat');
    const resetChat = document.getElementById('resetChat');
    const sendChat = document.getElementById('sendChat');
    const chatInput = document.getElementById('chatInput');
    const chatBody = document.getElementById('chatBody');

    chatModal.style.display = 'none';

    chatLink.addEventListener('click', () => {
        if (chatModal.style.display === 'flex') {
            chatModal.style.display = 'none';
        } else {
            chatModal.style.display = 'flex';
            appendMessage('bot', '안녕하세요 온새미 챗봇입니다. 궁금하신 것이 있다면 말씀해주세요');
            chatLink.disabled = true; // chat 버튼 비활성화
        }
    });
    closeChat.addEventListener('click', () => {
        chatModal.style.display = 'none';
        resetChatHistory(); // 대화 내용 초기화
        chatLink.disabled = false; // chat 버튼 활성화
    });

    sendChat.addEventListener('click', () => {
        sendMessage();
    });


    resetChat.addEventListener('click', () => {
        resetChatHistory();
    });

    sendChat.addEventListener('click', () => {
        sendMessage();
    });

    chatInput.addEventListener('keypress', (event) => {
        if (event.key === 'Enter') {
            sendMessage();
        }
    });

    function sendMessage() {
        const message = chatInput.value.trim();
        if (message !== '') {
            appendMessage('user', message);
            chatInput.value = '';

            fetch('{% url "qa:chatting" %}', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': '{{ csrf_token }}'
                },
                body: JSON.stringify({ question: message })
            })
            .then(response => response.json())
            .then(data => {
                appendMessage('bot', data.answer);
            })
            .catch(error => {
                console.error('Error:', error);
            });
        }
    }

    function appendMessage(sender, message) {
        const messageElement = document.createElement('div');
        messageElement.classList.add('chat-message', sender);
        messageElement.innerText = message;
        chatBody.appendChild(messageElement);
        chatBody.scrollTop = chatBody.scrollHeight;
    }

    function loadChatHistory() {
        fetch('{% url "qa:chatting" %}')
            .then(response => response.json())
            .then(data => {
                chatBody.innerHTML = '';
                data.conversation.forEach(item => {
                    appendMessage(item.sender, item.message);
                });
            });
    }

    function resetChatHistory() {
        fetch('{% url "qa:reset" %}', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': '{{ csrf_token }}'
            }
        })
        .then(() => {
            chatBody.innerHTML = '';
        })
        .catch(error => {
            console.error('Error:', error);
        });
    }
});

    function toggleSidebar() {
        const sidebar = document.querySelector('.sidebar');
        sidebar.classList.toggle('expanded');
        const dropdown = document.querySelector('.dropdown');
        dropdown.classList.toggle('expanded');
        const seniorPhoto = document.querySelector('.senior-photo img');
        if (sidebar.classList.contains('expanded')) {
            seniorPhoto.classList.remove('small-round-photo');
        } else {
            seniorPhoto.classList.add('small-round-photo');
        }
    }

    function toggleInfoBox() {
        const infoBox = document.getElementById('infoBox');
        infoBox.style.display = infoBox.style.display === 'block' ? 'none' : 'block';
    }

    document.addEventListener('click', function(event) {
        const infoBox = document.getElementById('infoBox');
        if (!infoBox.contains(event.target) && !event.target.matches('.user-profile, .user-profile *')) {
            infoBox.style.display = 'none';
        }
    });