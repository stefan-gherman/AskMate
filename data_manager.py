import connection as connection
import util as util
import os
import psycopg2
import psycopg2.extras
from psycopg2 import sql

QUESTIONS_FILE = 'data/questions.csv'
ANSWERS_FILE = 'data/answers.csv'
UPLOAD_FOLDER = 'static/img'
ALLOWED_EXTENSIONS = {'png', 'jpg'}


@connection.connection_handler
def add_question(cursor, title, message, file):
    date = util.datetime.today()
    submission_time = date.now().strftime("%Y-%m-%d %H:%M:%S")
    image = "../" + UPLOAD_FOLDER + "/" + str(file)
    cursor.execute(
        """
        INSERT INTO question (submission_time, view_number, vote_number, title, message, image) 
        VALUES ('{submission_time}','0','0', '{title}', '{message}', '{image}');
        """.format(submission_time=submission_time,
                   title=title,
                   message=message,
                   image=image))


@connection.connection_handler
def add_answer(cursor, question_id, message, file):
    date = util.datetime.today()
    submission_time = date.now().strftime("%Y-%m-%d %H:%M:%S")
    answers_list = util.read_answers_sql()
    image = "../" + UPLOAD_FOLDER + "/" + str(file)
    cursor.execute(
        """
        INSERT INTO answer (submission_time, vote_number, question_id, message, image) 
        VALUES ('{submission_time}', '0', '{question_id}', '{message}', '{image}' )
        """.format(submission_time=submission_time,
                   question_id=question_id,
                   message=message,
                   image=image

                   )
    )



# def delete_question(question_id):
#     answers_list = connection.read_answers(ANSWERS_FILE)
#     questions_list = connection.read_questions(QUESTIONS_FILE)
#
#     for question in questions_list:
#         if '../static/img/' != question['image']:
#             if int(question['id']) == int(question_id):
#                 image_path = question['image'][3:]
#                 os.remove(image_path)
#
#     for answers in answers_list:
#         if '../static/img/' != answers['image']:
#             if int(answers['question_id']) == int(question_id):
#                 image_path = answers['image'][3:]
#                 os.remove(image_path)
#
#     data = [element for element in questions_list if int(element['id']) != int(question_id)]
#     count = 0
#     for d in data:
#         d['id'] = count
#         count += 1
#
#     connection.write_questions(QUESTIONS_FILE, data)
#     data_answers = [element for element in answers_list if int(element['question_id']) != int(question_id)]
#     for elem in data_answers:
#         if int(elem['question_id']) > int(question_id):
#             elem['question_id'] = int(elem['question_id']) - 1
#     connection.write_answers(ANSWERS_FILE, data_answers)
#     return connection.read_questions('data/questions.csv')


# def delete_answer(answer_id):
#     answers = connection.read_answers(ANSWERS_FILE)
#     data = [element for element in answers if int(element['id']) != int(answer_id)]
#     count = 0
#     for answer in answers:
#         if '../static/img/' != answer['image']:
#             if int(answer['id']) == int(answer_id):
#                 image_path = answer['image'][3:]
#                 os.remove(image_path)
#     for d in data:
#         d['id'] = count
#         count += 1
#     connection.write_answers(ANSWERS_FILE, data)
#     return connection.read_answers('data/answers.csv')




def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@connection.connection_handler
def sort_questions(cursor, parameter, order):
    if order == 'asc':
        cursor.execute(
            sql.SQL("SELECT * FROM {table} ORDER BY {col1} ASC;")
                .format(table=sql.Identifier('question'), col1=sql.Identifier(parameter), order=sql.Identifier(order))
        )
    else:
        cursor.execute(
            sql.SQL("SELECT * FROM {table} ORDER BY {col1} DESC;")
                .format(table=sql.Identifier('question'), col1=sql.Identifier(parameter))
        )
    sorted_questions = cursor.fetchall()
    return sorted_questions


@connection.connection_handler
def list_first_questions(cursor):
    cursor.execute(
        sql.SQL("SELECT * FROM {table} LIMIT 5;")
            .format(table=sql.Identifier('question'))
        )
    names = cursor.fetchall()
    return names



@connection.connection_handler
def delete_sql_questions(cursor, id_to_delete):
    cursor.execute(
        sql.SQL("DELETE FROM {table} WHERE {col}=%s;")
            .format(table=sql.Identifier('comment'), col=sql.Identifier('question_id')), [id_to_delete]
    )
    cursor.execute(
        sql.SQL("SELECT id FROM {table} WHERE {col}=%s;")
            .format(table=sql.Identifier('answer'), col=sql.Identifier('question_id')), [id_to_delete]
    )
    answers = cursor.fetchall()

    for answer in answers:
        answer=int(answer["id"])
        cursor.execute(
            sql.SQL("DELETE FROM {table} WHERE {col}=%s;")
                .format(table=sql.Identifier('comment'), col=sql.Identifier('id')), [answer]
        )

    cursor.execute(
        sql.SQL("DELETE FROM {table} WHERE {col}=%s;")
            .format(table=sql.Identifier('answer'), col=sql.Identifier('question_id')), [id_to_delete]
    )
    cursor.execute(
        sql.SQL("DELETE FROM {table} WHERE {col}=%s;")
            .format(table=sql.Identifier('question_tag'), col=sql.Identifier('question_id')), [id_to_delete]
    )
    cursor.execute(
        sql.SQL("DELETE FROM {table} WHERE {col}=%s;")
            .format(table=sql.Identifier('question'), col=sql.Identifier('id')), [id_to_delete]
    )


@connection.connection_handler
def delete_sql_answers(cursor, id_to_delete):
    cursor.execute(
        sql.SQL("DELETE FROM {table} WHERE {col}=%s;")
            .format(table=sql.Identifier('comment'), col=sql.Identifier('answer_id')), [id_to_delete]
    )
    cursor.execute(
        sql.SQL("DELETE FROM {table} WHERE {col}=%s;")
            .format(table=sql.Identifier('answer'), col=sql.Identifier('id')), [id_to_delete]
    )


@connection.connection_handler
def display_question(cursor, parameter):
    cursor.execute(
        sql.SQL("SELECT * FROM {table} where {col} = %s;").format(table=sql.Identifier('question'),
                                                                  col=sql.Identifier('id')), [parameter]
    )
    question = cursor.fetchall()
    return question


@connection.connection_handler
def display_answers(cursor, parameter):
    cursor.execute(
        sql.SQL("SELECT * FROM {table} where {col} = %s ORDER BY {col2} ASC;")
            .format(table=sql.Identifier('answer'),
                    col=sql.Identifier('question_id'),
                    col2=sql.Identifier('id')), [parameter]
    )
    answers = cursor.fetchall()
    return answers


@connection.connection_handler
def update_views(cursor, parameter):
    cursor.execute(
        sql.SQL("UPDATE {table} SET {col}={col} + 1 WHERE {col2} = %s;")
            .format(table=sql.Identifier('question'),
                    col=sql.Identifier('view_number'),
                    col2=sql.Identifier('id')), [parameter]
    )


@connection.connection_handler
def update_question(cursor, parameter, message, title):
    cursor.execute(
        sql.SQL("UPDATE {table} SET {col2}=%s, {col3} =%s WHERE {col1} = %s;")
            .format(table=sql.Identifier('question'),
                    col2=sql.Identifier('message'),
                    col1=sql.Identifier('id'),
                    col3=sql.Identifier('title')), [message, title, parameter]
    )


@connection.connection_handler
def vote_item_up_down(cursor, parameter, type, direction):
    if type == 'question':
        if direction == "up":
            cursor.execute(
            sql.SQL("UPDATE {table} SET {col}={col}+1 WHERE {col2} = %s;")
            .format(table=sql.Identifier('question'),
                    col=sql.Identifier('vote_number'),
                    col2=sql.Identifier('id')), [parameter]
            )
        elif direction == "down":
            cursor.execute(
            sql.SQL("UPDATE {table} SET {col}={col}-1 WHERE {col2} = %s;")
            .format(table=sql.Identifier('question'),
                    col=sql.Identifier('vote_number'),
                    col2=sql.Identifier('id')), [parameter]
            )

    elif type == 'answer':
        if direction == "up":
            cursor.execute(
            sql.SQL("UPDATE {table} SET {col}={col}+1 WHERE {col2} = %s;")
            .format(table=sql.Identifier('answer'),
                    col=sql.Identifier('vote_number'),
                    col2=sql.Identifier('id')), [parameter]
            )
        elif direction == "down":
            cursor.execute(
            sql.SQL("UPDATE {table} SET {col}={col}-1 WHERE {col2} = %s;")
            .format(table=sql.Identifier('answer'),
                col=sql.Identifier('vote_number'),
                col2=sql.Identifier('id')), [parameter]
            )

@connection.connection_handler
def max_id(cursor):
    cursor.execute("""SELECT MAX(id) FROM tag""")
    maxim_id = cursor.fetchall()
    return maxim_id

@connection.connection_handler
def add_tag(cursor, tag_name, question_id):
    id_to_add = max_id()[0]['max'] + 1
    cursor.execute(
        sql.SQL("INSERT INTO {table} VALUES (%s, %s);")
            .format(table=sql.Identifier('tag')), [id_to_add, tag_name]
    )
    cursor.execute(
        sql.SQL("INSERT INTO {table} VALUES (%s, %s);")
            .format(table=sql.Identifier('question_tag')), [question_id, id_to_add]
    )

