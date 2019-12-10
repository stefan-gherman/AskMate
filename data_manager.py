import connection as connection

def delete_question(question_id):
    my_question_list = connection.read_questions('data/questions.csv')
    FILE = 'data/questions.csv'
    data = [element for element in my_question_list if int(element['id']) != int(question_id)]
    count = 0
    for d in data:
        d['id'] = count
        count += 1
    connection.write_questions(FILE, data)
    return connection.read_questions('data/questions.csv')

def delete_answer(answer_id):
    my_answers_list = connection.read_answers('data/answers.csv')
    FILE = 'data/answers.csv'
    data = [element for element in my_answers_list if int(element['id']) != int(answer_id)]
    count = 0
    for d in data:
        d['id'] = count
        count += 1
    connection.write_answers(FILE, data)
    return connection.read_answers('data/answers.csv')

print(delete_answer(0))
