import connection as connection

QUESTIONS = 'data/questions.csv'
ANSWERS = 'data/answers.csv'

question_list = connection.read_questions(QUESTIONS)
answers_list = connection.read_answers(ANSWERS)


def add_question(title, message):
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
    return 3


def add_answer(question_id, message):
    new_answer = {'id': len(answers_list),
                  'submission_time': 0,
                  'vote_number': 0,
                  'question_id': question_id,
                  'message': message,
                  'image': ''}
    answers_list.append(new_answer)
    connection.write_answers(ANSWERS, answers_list)


def vote_question(question_id, param):
    vote_number = question_list[question_id]['vote_number']
    if param == 'vote-up':
        question_list[question_id]['vote_number'] = int(vote_number) + 1
        connection.write_questions(QUESTIONS,question_list)
    elif param == 'vote-down':
        question_list[question_id]['vote_number'] = int(vote_number) - 1
        connection.write_questions(QUESTIONS,question_list)

    print(question_list)