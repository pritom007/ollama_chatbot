
    function appendMessage(who, text) {
        var avatar = who === 'user' ? 'U' : 'C';
        var messageClass = who === 'user' ? 'user-message' : 'bot-message';
        $('#chatbox').append(`
            <div class="message ${messageClass}">
                <span class="avatar">${avatar}</span>
                <div class="text">${text}</div>
            </div>
        `);
        $('#chatbox').scrollTop($('#chatbox')[0].scrollHeight); // Scroll to the bottom
    }

    function sendMessage() {
        var text = $('#userInput').val();
        $('#userInput').val(''); // Clear the input after sending
        if (text.trim() !== '') {
            appendMessage('user', text);
            $.post('/ask', {text: text}, function(data) {
                appendMessage('bot', data.response);
            });
        }
    }

    function sendFile() {
        var file = $('#fileInput').prop('files')[0];
        var formData = new FormData();
        formData.append('file', file);

        $.ajax({
            url: '/upload',
            type: 'POST',
            data: formData,
            contentType: false,
            processData: false,
            success: function(data) {
                appendMessage('user', 'Uploaded a file');
                appendMessage('bot', data.response);
            }
        });
    }

    // Trigger send message on enter
    $('#userInput').on('keypress',function(e) {
        if(e.which == 13) {
            sendMessage();
        }
    });
