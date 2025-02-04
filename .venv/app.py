from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
import random
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(500), nullable=False)
    option_a = db.Column(db.String(200), nullable=False)
    option_b = db.Column(db.String(200), nullable=False)
    option_c = db.Column(db.String(200), nullable=False)
    option_d = db.Column(db.String(200), nullable=False)
    correct_answer = db.Column(db.String(1), nullable=False)

with app.app_context():
    db.create_all()
    
def initialize_questions():
    with app.app_context():
        db.session.query(Question).delete()  # Smazání starých dat
        # Načtení dat ze souboru
        try:
            with open(".venv/templates/questions.json", "r", encoding="utf-8") as f:
                questions_data = json.load(f)
        except FileNotFoundError:
            print("Soubor 'questions.json' nebyl nalezen.")
            return
        except json.JSONDecodeError:
            print("Chyba při čtení JSON souboru.")
            return

        for text, options, correct in questions_data:
            # Pokud jsou méně než 4 odpovědi, doplníme pomlčkami
            while len(options) < 4:
                options.append('---------------------')

            # Pokud je více než 4 odpovědi, odstraníme nadbytečné
            if len(options) > 4:
                options = options[:3] + [options[correct.index(correct)]]

            question = Question(
                text=text,
                option_a=options[0],
                option_b=options[1],
                option_c=options[2],
                option_d=options[3],
                correct_answer=correct
            )
            db.session.add(question)

        db.session.commit()
        print("Otázky úspěšně inicializovány.")

# Ruční vytvoření tabulek při spuštění aplikace
with app.app_context():
    initialize_questions()
    

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start_test')
def start_test():
    questions = Question.query.all()
    if not questions:
        return "Databáze neobsahuje žádné otázky. Přidejte otázky a zkuste to znovu.", 400

    # Vyberte buď 30 otázek, nebo všechny dostupné, pokud jich je méně než 30
    selected_questions = random.sample(questions, min(30, len(questions)))
    return render_template('test.html', question=selected_questions[0])

@app.route('/get_questions')
def get_questions():
    questions = Question.query.all()  # Získá všechny otázky z databáze
    if not questions:
        return jsonify({"error": "Databáze neobsahuje žádné otázky."}), 400

    # Vybere náhodně 30 otázek (nebo všechny, pokud jich je méně než 30)
    selected_questions = random.sample(questions, min(10, len(questions)))

    # Vrátí otázky ve formátu JSON
    return jsonify([{
        'id': q.id,
        'text': q.text,
        'option_a': q.option_a,
        'option_b': q.option_b,
        'option_c': q.option_c,
        'option_d': q.option_d,
        'correct_answer': q.correct_answer  # Přidáno pro ladění
    } for q in selected_questions])

@app.route('/get_question/<int:question_id>')
def get_question(question_id):
    question = Question.query.get_or_404(question_id)
    print(f"Fetching question: question_id={question_id}")  # Debugging
    return jsonify({
        'text': question.text,
        'option_a': question.option_a,
        'option_b': question.option_b,
        'option_c': question.option_c,
        'option_d': question.option_d
    })

@app.route('/check_answer/<int:question_id>/<answer>')
def check_answer(question_id, answer):
    question = Question.query.get_or_404(question_id)
    print(f"Checking answer: question_id={question_id}, answer={answer}, correct={question.correct_answer}")  # Debugging
    return jsonify({'correct': answer == question.correct_answer, 'answer': question.correct_answer})

@app.route('/results/<int:correct_answers>/<int:total_questions>')
def results(correct_answers, total_questions):
    return render_template('results.html', correct_answers=correct_answers, total_questions=total_questions)

@app.route('/show_questions')
def show_questions():
    questions = Question.query.all()
    return render_template('show_questions.html', questions=questions)

if __name__ == '__main__':
    app.run(debug=True)