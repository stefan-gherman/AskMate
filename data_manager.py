import connection as connection
import util as util
import os

QUESTIONS_FILE = 'data/questions.csv'
ANSWERS_FILE = 'data/answers.csv'
UPLOAD_FOLDER = 'static/img'
ALLOWED_EXTENSIONS = {'png', 'jpg'}


# questions_list = connection.read_questions(QUESTIONS_FILE)
# answers_list = connection.read_answers(ANSWERS_FILE)


def add_question(title, message, file):
    questions_list = connection.read_questions(QUESTIONS_FILE)
    questions_list = util.order_by_value(questions_list, 'id', 'asc')
    if len(questions_list) == 0:
        id = 0
    else:
        id = int(questions_list[-1]['id']) + 1
    print('id: ', id)
    new_question = {'id': str(id),
                    'submission_time': util.today.strftime("%Y-%m-%d"),
                    'view_number': '0',
                    'vote_number': '0',
                    'title': title,
                    'message': message,
                    'image': "../" + UPLOAD_FOLDER + "/" + str(file)
                    }

    new_question = util.make_compat_display([new_question], 'not_textarea')
    questions_list.append(new_question[0])
    connection.write_questions(QUESTIONS_FILE, questions_list)

def delete_question(question_id):
    answers_list = connection.read_answers(ANSWERS_FILE)
    questions_list = connection.read_questions(QUESTIONS_FILE)
    for question in questions_list:
        if '../static/img/' != question['image']:
            if int(question['id']) == int(question_id):
                image_path = question['image'][3:]
                os.remove(image_path)
    data = [element for element in questions_list if int(element['id']) != int(question_id)]
    count = 0
    for d in data:
        d['id'] = count
        count += 1
    connection.write_questions(QUESTIONS_FILE, data)
    data_answers = [element for element in answers_list if int(element['question_id']) != int(question_id)]
    for elem in data_answers:
        if int(elem['question_id']) > int(question_id):
            elem['question_id'] = int(elem['question_id']) - 1
    connection.write_answers(ANSWERS_FILE, data_answers)
    return connection.read_questions('data/questions.csv')

def add_answer(question_id, message):
    answers_list = connection.read_answers(ANSWERS_FILE)
    if len(answers_list) == 0:
        id = 0
    else:
        id = int(answers_list[-1]['id']) + 1
    new_answer = {'id': str(id),
                  'submission_time': util.today.strftime("%Y-%m-%d"),
                  'vote_number': '0',
                  'question_id': question_id,
                  'message': message,
                  'image': ''}
    new_answer = util.make_compat_display([new_answer], 'not_textarea')
    answers_list.append(new_answer[0])
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
    for elem in range(len(questions_list)):
        for key in questions_list[elem].keys():
            if str(questions_list[elem]['id']) == str(question_id):
                pos = elem
    vote_number = int(questions_list[pos]['vote_number'])
    if option == 'vote_up':
        questions_list[pos]['vote_number'] = str(vote_number + 1)
        connection.write_questions(QUESTIONS_FILE, questions_list)
    elif option == 'vote_down':
        questions_list[pos]['vote_number'] = str(vote_number - 1)
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


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def edit_question(question_id):
    all_questions = connection.read_questions()

