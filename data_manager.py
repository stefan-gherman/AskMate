import connection as connection
from server import request

QUESTIONS = 'data/questions.csv'
ANSWERS = 'data/answers.csv'

question_list = connection.read_questions(QUESTIONS)
answers_list = connection.read_answers(ANSWERS)


def add_question():
    title = request.form['title']
    message = request.form['message']
    new_question = {'id': len(question_list),
                    'submission_time': '',
                    'view_number': 0,
                    'vote_number': 0,
                    'title': title,
                    'message': message,
                    'image': ''
                    }

    question_list.append(new_question)
    connection.write_questions(QUESTIONS, question_list)
