let currentQuestionIndex = 0;
let correctAnswers = 0;
let questions = [];

function checkAnswer() {
    console.log("checkAnswer called"); // Debugging
    const selectedAnswer = document.querySelector('input[name="answer"]:checked');
    if (selectedAnswer) {
        console.log("Selected answer:", selectedAnswer.value); // Debugging
        fetch(`/check_answer/${questions[currentQuestionIndex].id}/${selectedAnswer.value}`)
            .then(response => response.json())
            .then(data => {
                console.log("Server response:", data); // Debugging
                document.getElementById('result').innerText = data.correct ? 'Správně!' : 'Špatně!';
                if (data.correct) {
                    correctAnswers++;
                }
            });
    } else {
        console.log("No answer selected"); // Debugging
    }
}

function nextQuestion() {
    console.log("nextQuestion called"); // Debugging
    currentQuestionIndex++;
    if (currentQuestionIndex < questions.length) {
        fetch(`/get_question/${questions[currentQuestionIndex].id}`)
            .then(response => response.json())
            .then(data => {
                console.log("Next question data:", data); // Debugging
                document.getElementById('question-text').innerText = data.text;
                document.querySelector('label:nth-child(1)').innerText = data.option_a;
                document.querySelector('label:nth-child(2)').innerText = data.option_b;
                document.querySelector('label:nth-child(3)').innerText = data.option_c;
                document.querySelector('label:nth-child(4)').innerText = data.option_d;
                document.getElementById('result').innerText = '';
            });
    } else {
        console.log("End of test"); // Debugging
        window.location.href = `/results/${correctAnswers}/${questions.length}`;
    }
}

window.onload = function() {
    fetch('/get_questions')
        .then(response => {
            if (!response.ok) {
                throw new Error('Nepodařilo se načíst otázky.');
            }
            return response.json();
        })
        .then(data => {
            if (data.error) {
                alert(data.error);  // Zobrazí chybu, pokud nejsou k dispozici žádné otázky
                return;
            }

            questions = data;  // Uloží otázky do globální proměnné
            if (questions.length > 0) {
                displayQuestion(questions[currentQuestionIndex]);  // Zobrazí první otázku
            } else {
                alert('Žádné otázky nebyly nalezeny.');
            }
        })
        .catch(error => {
            console.error('Chyba:', error);
            alert('Nepodařilo se načíst otázky.');
        });
};

function displayQuestion(question) {
    // Zobrazí text otázky
    document.getElementById('question-text').innerText = question.text;

    // Zobrazí možnosti odpovědí
    document.getElementById('option_a').innerText = question.option_a;
    document.getElementById('option_b').innerText = question.option_b;
    document.getElementById('option_c').innerText = question.option_c;
    document.getElementById('option_d').innerText = question.option_d;

    // Resetuje výběr odpovědi
    const radioButtons = document.querySelectorAll('input[name="answer"]');
    radioButtons.forEach(radio => radio.checked = false);

    // Resetuje výsledek
    document.getElementById('result').innerText = '';
}

function checkAnswer() {
    const selectedAnswer = document.querySelector('input[name="answer"]:checked');
    if (selectedAnswer) {
        const answer = selectedAnswer.value;
        fetch(`/check_answer/${questions[currentQuestionIndex].id}/${answer}`)
            .then(response => response.json())
            .then(data => {
                document.getElementById('result').innerText = data.correct ? 'Správně!' : 'Špatně! Správná odpoveď je:' + data.answer ;
                if (data.correct) {
                    correctAnswers++;
                }
            });
    } else {
        alert('Vyberte odpověď!');  // Upozornění, pokud uživatel nevybral odpověď
    }
}

function nextQuestion() {
    currentQuestionIndex++;
    if (currentQuestionIndex < questions.length) {
        displayQuestion(questions[currentQuestionIndex]);  // Zobrazí další otázku
    } else {
        // Přesměruje na stránku s výsledky
        window.location.href = `/results/${correctAnswers}/${questions.length}`;
    }
}