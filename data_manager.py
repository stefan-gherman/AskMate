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
        answer = int(answer["id"])
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
def update_answer(cursor, parameter, message):
    cursor.execute(
        sql.SQL("UPDATE {table} SET {col2} = %s WHERE {col1} = %s;")
            .format(table=sql.Identifier('answer'),
                    col1=sql.Identifier('id'),
                    col2=sql.Identifier('message')), [message, parameter]
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


@connection.connection_handler
def get_tag_questions(cursor, question_id):
    cursor.execute(
        sql.SQL("SELECT * FROM {table} WHERE {col1}=%s;")
            .format(table=sql.Identifier('question_tag'), col1=sql.Identifier('question_id'), ), [question_id]
    )
    all_tag_ids = cursor.fetchall()
    tag_list = []
    for tag_to_print in all_tag_ids:
        tag_to_print = int(tag_to_print['tag_id'])
        cursor.execute(
            sql.SQL("SELECT * FROM {table} WHERE {col}=%s;")
                .format(table=sql.Identifier('tag'), col=sql.Identifier('id')), [tag_to_print]
        )
        names = cursor.fetchall()
        tag_list.append(names)
    return tag_list


@connection.connection_handler
def delete_tag_questions(cursor, question_id, tag_id_to_delete):
    cursor.execute(
        sql.SQL("DELETE FROM {table} WHERE {col1}=%s AND {col2}=%s;")
            .format(table=sql.Identifier('question_tag'), col1=sql.Identifier('question_id'),
                    col2=sql.Identifier('tag_id')), [question_id, tag_id_to_delete]
    )
    cursor.execute(
        sql.SQL("DELETE FROM {table} WHERE {col}=%s;")
            .format(table=sql.Identifier('tag'), col=sql.Identifier('id')), [tag_id_to_delete]
    )

@connection.connection_handler
def search_for_phrase(cursor, phrase_for_query):
    cursor.execute(
        sql.SQL(
            "SELECT * from {table} WHERE to_tsvector({col1}) @@ to_tsquery(%s) OR to_tsvector({col2}) @@ to_tsquery(%s) ORDER BY {col3} desc;")
            .format(table=sql.Identifier('question'),
                    col1=sql.Identifier('title'),
                    col2=sql.Identifier('message'),
                    col3=sql.Identifier('vote_number')), [phrase_for_query, phrase_for_query]
    )

    questions_found = cursor.fetchall()
    return questions_found


@connection.connection_handler
def add_question_comment(cursor, message, question_id, answer_id):
    date = util.datetime.today()
    submission_time = date.now().strftime("%Y-%m-%d %H:%M:%S")
    print(question_id)
    print(answer_id)
    if question_id is not None:
        cursor.execute(
            """
            INSERT INTO comment (question_id, message, submission_time, edited_count) 
            VALUES ('{question_id}', '{message}', '{submission_time}', '0');
            """.format(question_id=question_id,
                       message=message,
                       submission_time=submission_time)
        )
    else:
        cursor.execute(
            """
            INSERT INTO comment (answer_id, message, submission_time, edited_count) 
            VALUES ('{answer_id}', '{message}', '{submission_time}', '0');
            """.format(answer_id=answer_id,
                       message=message,
                       submission_time=submission_time)
        )
