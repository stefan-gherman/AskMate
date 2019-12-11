import connection as connection
import util as util

QUESTIONS_FILE = 'data/questions.csv'
ANSWERS_FILE = 'data/answers.csv'


def add_question(title, message):
    questions_list = connection.read_questions(QUESTIONS_FILE)
    new_question = {'id': str(len(questions_list)),
                    'submission_time': util.today.strftime("%Y-%m-%d"),
                    'view_number': '0',
                    'vote_number': '0',
                    'title': title,
                    'message': message,
                    'image': ''
                    }

    new_question = util.make_compat_display([new_question], 'not_textarea')
    questions_list.append(new_question[0])
    connection.write_questions(QUESTIONS_FILE, questions_list)

def delete_question(question_id):
    questions_list = connection.read_questions(QUESTIONS_FILE)
    data = [element for element in questions_list if int(element['id']) != int(question_id)]
    # count = 0
    # for d in data:
    #     d['id'] = count
    #     count += 1
    connection.write_questions(QUESTIONS_FILE, data)
    return connection.read_questions('data/questions.csv')

def add_answer(question_id, message):
    answers_list = connection.read_answers(ANSWERS_FILE)
    if len(answers_list) == 0:
        id = 0
    else:
        id = int(answers_list[-1]['id']) + 1
    new_answer = {'id': id,
                  'submission_time': util.today.strftime("%Y-%m-%d"),
                  'vote_number': 0,
                  'question_id': question_id,
                  'message': message,
                  'image': ''}
    answers_list.append(new_answer)
    connection.write_answers(ANSWERS_FILE, answers_list)
    
def delete_answer(answer_id):
    answers = connection.read_answers(ANSWERS_FILE)
    data = [element for element in answers if int(element['id']) != int(answer_id)]
    count = 0
    for d in data:
        d['id'] = count
        count += 1
    connection.write_answers(ANSWERS_FILE, data)
    return connection.read_answers('data/answers.csv')


def vote_question(question_id, option):
    questions_list = connection.read_questions(QUESTIONS_FILE)
    vote_number = questions_list[int(question_id)]['vote_number']
    if option == 'vote_up':
        questions_list[int(question_id)]['vote_number'] = int(vote_number) + 1
        connection.write_questions(QUESTIONS_FILE, questions_list)
    elif option == 'vote_down':
        questions_list[int(question_id)]['vote_number'] = int(vote_number) - 1
        connection.write_questions(QUESTIONS_FILE, questions_list)


def vote_answer(answer_id, option):
    answers_list = connection.read_answers(ANSWERS_FILE)
    vote_number = answers_list[int(answer_id)]['vote_number']
    if option == 'vote_up':
        answers_list[int(answer_id)]['vote_number'] = int(vote_number) + 1
        connection.write_answers(ANSWERS_FILE, answers_list)
    elif option == 'vote_down':
        answers_list[int(answer_id)]['vote_number'] = int(vote_number) - 1
        connection.write_answers(ANSWERS_FILE, answers_list)


def edit_question(question_id):
    all_questions = connection.read_questions()

