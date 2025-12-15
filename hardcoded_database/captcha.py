import csv
import os

def load_captcha_questions():
    questions = []
    csv_path = os.path.join(os.path.dirname(__file__), 'captcha.csv')
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['question'] and row['answer']:
                questions.append({
                    "question": row['question'],
                    "answer": row['answer']
                })
    return questions

CAPTCHA_QUESTIONS = load_captcha_questions()

def is_correct_answer(question_index: int, answer: str) -> bool:
    if question_index < 0 or question_index >= len(CAPTCHA_QUESTIONS):
        return False
    
    correct_answer = CAPTCHA_QUESTIONS[question_index]['answer']
    if not answer:
        return False
        
    return str(answer).strip().lower() == str(correct_answer).strip().lower()