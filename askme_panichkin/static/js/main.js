function setupCentrifugo() {
    if (window.location.pathname.startsWith('/question/')) {
        const questionId = window.location.pathname.split('/')[2];
        const centrifuge = new Centrifuge(`${window.CENTRIFUGO_URL}/connection/websocket`, {
            token: window.CENTRIFUGO_TOKEN
        });

        centrifuge.subscribe(`questions:question_${questionId}`, function(message) {
            const answersList = document.querySelector('.answers-list');
            if (answersList) {
                answersList.insertAdjacentHTML('beforeend', message.data.html);
                setupAnswerLikes();
            }
        });

        centrifuge.connect();
    }
}

function setupQuestionLikes() {
    $('.like-question, .dislike-question').off('click').on('click', function(e) {
        e.preventDefault();
        const button = $(this);
        const questionId = button.data('question-id');
        const action = button.data('action');

        $.ajax({
            type: 'POST',
            url: `/question/${questionId}/${action}/`,
            data: {
                'csrfmiddlewaretoken': csrftoken
            },
            dataType: 'json',
            success: function(data) {
                if (data.success) {
                    $(`.like-question[data-question-id="${questionId}"] .like-count`).text(data.likes);
                    $(`.dislike-question[data-question-id="${questionId}"] .dislike-count`).text(data.dislikes);
                }
            }
        });
    });
}

function setupAnswerLikes() {
    $('.like-answer, .dislike-answer').off('click').on('click', function(e) {
        e.preventDefault();
        const button = $(this);
        const answerId = button.data('answer-id');
        const action = button.data('action');

        $.ajax({
            type: 'POST',
            url: `/answer/${answerId}/${action}/`,
            data: {
                'csrfmiddlewaretoken': csrftoken
            },
            dataType: 'json',
            success: function(data) {
                if (data.success) {
                    $(`.like-answer[data-answer-id="${answerId}"] .like-count`).text(data.likes);
                    $(`.dislike-answer[data-answer-id="${answerId}"] .dislike-count`).text(data.dislikes);
                }
            }
        });
    });
}

function setupHelpfulAnswers() {
    $('.mark-helpful').off('click').on('click', function(e) {
        e.preventDefault();
        const button = $(this);
        const answerId = button.data('answer-id');

        $.ajax({
            type: 'POST',
            url: `/answer/${answerId}/mark-helpful/`,
            data: {
                'csrfmiddlewaretoken': csrftoken
            },
            dataType: 'json',
            success: function(data) {
                if (data.success) {
                    button.toggleClass('btn-success btn-outline-secondary');
                    button.html('<i class="bi bi-check-circle"></i> ' +
                        (data.helpful ? 'Marked as Correct' : 'Mark as Correct'));
                }
            }
        });
    });
}

$(document).ready(function() {
    setupQuestionLikes();
    setupAnswerLikes();
    setupHelpfulAnswers();
});