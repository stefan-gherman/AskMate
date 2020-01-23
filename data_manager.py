import connection as connection
import util as util
import os
import psycopg2
import psycopg2.extras
import bcrypt
from psycopg2 import sql

QUESTIONS_FILE = 'data/questions.csv'
ANSWERS_FILE = 'data/answers.csv'
UPLOAD_FOLDER = 'static/img'
ALLOWED_EXTENSIONS = {'png', 'jpg','jpeg'}


@connection.connection_handler
def add_question(cursor, title, message, file, user_id):
    date = util.datetime.today()
    submission_time = date.now().strftime("%Y-%m-%d %H:%M:%S")
    image = "../" + UPLOAD_FOLDER + "/" + str(file)
    cursor.execute(
        """
        INSERT INTO question (submission_time, view_number, vote_number, title, message, image, user_id) 
        VALUES ('{submission_time}','0','0', '{title}', '{message}', '{image}',{user_id});
        """.format(submission_time=submission_time,
                   title=title,
                   message=message,
                   image=image,
                   user_id=user_id
                   )
    )


@connection.connection_handler
def add_answer(cursor, question_id, message, file, user_id):
    date = util.datetime.today()
    submission_time = date.now().strftime("%Y-%m-%d %H:%M:%S")
    answers_list = util.read_answers_sql()
    image = "../" + UPLOAD_FOLDER + "/" + str(file)
    cursor.execute(
        """
        INSERT INTO answer (submission_time, vote_number, question_id, message, image, user_id) 
        VALUES ('{submission_time}', '0', '{question_id}', '{message}', '{image}', {user_id} )
        """.format(submission_time=submission_time,
                   question_id=question_id,
                   message=message,
                   image=image,
                   user_id=user_id
                   )
    )


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@connection.connection_handler
def sort_questions(cursor, parameter, order):
    if order == 'asc':
        cursor.execute(
            sql.SQL(
                "SELECT {table}.*, {table2}.{col2} as user_name FROM {table} JOIN {table2} ON {table}.{col3} = {table2}.{col4} ORDER BY {col1} ASC;")
                .format(
                table=sql.Identifier('question'),
                col1=sql.Identifier(parameter),
                order=sql.Identifier(order),
                table2=sql.Identifier('person'),
                col3=sql.Identifier('user_id'),
                col4=sql.Identifier('id'),
                col2=sql.Identifier('username'))
        )
    else:
        cursor.execute(
            sql.SQL(
                "SELECT {table}.*, {table2}.{col2} as user_name FROM {table} JOIN {table2} ON {table}.{col3} = {table2}.{col4} ORDER BY {col1} DESC;")
                .format(
                table=sql.Identifier('question'),
                col1=sql.Identifier(parameter),
                order=sql.Identifier(order),
                table2=sql.Identifier('person'),
                col3=sql.Identifier('user_id'),
                col4=sql.Identifier('id'),
                col2=sql.Identifier('username'))
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
    cursor.execute(f"""
                DELETE FROM question_status WHERE question_id={id_to_delete};
    """)
    cursor.execute(
        sql.SQL("SELECT {col1} FROM {table1} WHERE {col2}=%s;")
            .format(
            col1=sql.Identifier('image'),
            table1=sql.Identifier('question'),
            col2=sql.Identifier('id')
        ), [id_to_delete]
    )

    picture = cursor.fetchall()
    picture = picture[0]['image']
    print(picture, type(picture))
    if picture != "../static/img/":
        print('is different')
        picture = picture.lstrip('.')
        picture = picture.lstrip('/')
        os.remove(picture)
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
    cursor.execute(f"""
                DELETE FROM answer_status WHERE answer_id={id_to_delete};
    """)
    cursor.execute(
        sql.SQL("SELECT {col1} FROM {table1} WHERE {col2}=%s;")
            .format(
        col1 = sql.Identifier('image'),
        table1 = sql.Identifier('answer'),
        col2 = sql.Identifier('id')
    ), [id_to_delete]
    )

    picture = cursor.fetchall()
    picture = picture[0]['image']
    print(picture, type(picture))
    if picture != "../static/img/":
        print('is different')
        picture = picture.lstrip('.')
        picture = picture.lstrip('/')
        os.remove(picture)
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
    # TODO: sanitize JOIN
    # cursor.execute(
    #     sql.SQL("SELECT * FROM {table} where {col} = %s ORDER BY {col2} ASC;")
    #         .format(table=sql.Identifier('answer'),
    #                 col=sql.Identifier('question_id'),
    #                 col2=sql.Identifier('id')), [parameter]
    # )
    # answers = cursor.fetchall()
    # return answers
    cursor.execute(f"""
                    SELECT answer.*, person.username AS username FROM answer
                    JOIN person ON answer.user_id = person.id
                    ORDER BY answer.vote_number DESC;
""")
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
            cursor.execute(
                sql.SQL(
                    "SELECT {table1}.{col1} , {table2}.{col3} FROM {table1} JOIN {table2} ON {table1}.{col1} = {table2}.{col2} WHERE {table1}.{col2} = %s LIMIT 1;")
                    .format(
                    table1=sql.Identifier('question'),
                    col1=sql.Identifier('user_id'),
                    table2=sql.Identifier('person'),
                    col2=sql.Identifier('id'),
                    col3=sql.Identifier('username')
                ), [parameter]
            )
            user_id = cursor.fetchall()
            user_id_to_update = user_id[0]['user_id']
            cursor.execute(
                sql.SQL(
                    "UPDATE {table1} SET {col1} = {col1} + 5 WHERE {col2} = %s;"
                ).format(
                    table1=sql.Identifier('person'),
                    col1=sql.Identifier('reputation'),
                    col2=sql.Identifier('id')
                ), [user_id_to_update]
            )

        elif direction == "down":
            cursor.execute(
                sql.SQL("UPDATE {table} SET {col}={col}-1 WHERE {col2} = %s;")
                    .format(table=sql.Identifier('question'),
                            col=sql.Identifier('vote_number'),
                            col2=sql.Identifier('id')), [parameter]
            )
            cursor.execute(
                sql.SQL(
                    "SELECT {table1}.{col1} , {table2}.{col3} FROM {table1} JOIN {table2} ON {table1}.{col1} = {table2}.{col2} WHERE {table1}.{col2} = %s LIMIT 1;")
                    .format(
                    table1=sql.Identifier('question'),
                    col1=sql.Identifier('user_id'),
                    table2=sql.Identifier('person'),
                    col2=sql.Identifier('id'),
                    col3=sql.Identifier('username')
                ), [parameter]
            )
            user_id = cursor.fetchall()
            user_id_to_update = user_id[0]['user_id']
            cursor.execute(
                sql.SQL(
                    "UPDATE {table1} SET {col1} = {col1}  - 2 WHERE {col2} = %s;"
                ).format(
                    table1=sql.Identifier('person'),
                    col1=sql.Identifier('reputation'),
                    col2=sql.Identifier('id')
                ), [user_id_to_update]
            )

    elif type == 'answer':
        if direction == "up":
            cursor.execute(
                sql.SQL("UPDATE {table} SET {col}={col}+1 WHERE {col2} = %s;")
                    .format(table=sql.Identifier('answer'),
                            col=sql.Identifier('vote_number'),
                            col2=sql.Identifier('id')), [parameter]
            )
            cursor.execute(
                sql.SQL(
                    "SELECT {table1}.{col1} , {table2}.{col3} FROM {table1} JOIN {table2} ON {table1}.{col1} = {table2}.{col2} WHERE {table1}.{col2} = %s LIMIT 1;")
                    .format(
                    table1=sql.Identifier('answer'),
                    col1=sql.Identifier('user_id'),
                    table2=sql.Identifier('person'),
                    col2=sql.Identifier('id'),
                    col3=sql.Identifier('username')
                ), [parameter]
            )
            user_id = cursor.fetchall()
            user_id_to_update = user_id[0]['user_id']
            cursor.execute(
                sql.SQL(
                    "UPDATE {table1} SET {col1} = {col1}  + 10 WHERE {col2} = %s;"
                ).format(
                    table1=sql.Identifier('person'),
                    col1=sql.Identifier('reputation'),
                    col2=sql.Identifier('id')
                ), [user_id_to_update]
            )


        elif direction == "down":
            cursor.execute(
                sql.SQL("UPDATE {table} SET {col}={col}-1 WHERE {col2} = %s;")
                    .format(table=sql.Identifier('answer'),
                            col=sql.Identifier('vote_number'),
                            col2=sql.Identifier('id')), [parameter]
            )
            cursor.execute(
                sql.SQL(
                    "SELECT {table1}.{col1} , {table2}.{col3} FROM {table1} JOIN {table2} ON {table1}.{col1} = {table2}.{col2} WHERE {table1}.{col2} = %s LIMIT 1;")
                    .format(
                    table1=sql.Identifier('answer'),
                    col1=sql.Identifier('user_id'),
                    table2=sql.Identifier('person'),
                    col2=sql.Identifier('id'),
                    col3=sql.Identifier('username')
                ), [parameter]
            )
            user_id = cursor.fetchall()
            user_id_to_update = user_id[0]['user_id']
            cursor.execute(
                sql.SQL(
                    "UPDATE {table1} SET {col1} = {col1}  -2  WHERE {col2} = %s;"
                ).format(
                    table1=sql.Identifier('person'),
                    col1=sql.Identifier('reputation'),
                    col2=sql.Identifier('id')
                ), [user_id_to_update]
            )


@connection.connection_handler
def max_id(cursor):
    cursor.execute("""SELECT MAX(id) FROM tag""")
    maxim_id = cursor.fetchall()
    return maxim_id


@connection.connection_handler
def add_tag(cursor, tag_name, question_id):
    question_id = int(question_id)
    print('Am i Here?')
    cursor.execute(
        sql.SQL("SELECT  {table1}.{col1}, {table2}.{col2} FROM {table1} JOIN {table3} ON {table3}.{col4} = {table1}.{col5} JOIN {table2} on {table3}.{col6} = {table2}.{col5} WHERE {table3}.{col6} = %s;")
            .format(
            table1 = sql.Identifier('tag'),
            col1 = sql.Identifier('name'),
            table2 = sql.Identifier('question'),
            col2 = sql.Identifier('title'),
            table3 = sql.Identifier('question_tag'),
            col4=sql.Identifier('tag_id'),
            col5=sql.Identifier('id'),
            col6=sql.Identifier('question_id')

                    ), [question_id]
    )
    tags = cursor.fetchall()
    tag_names = [tag['name'].lower() for tag in tags]
    print(tag_names)
    if tag_name.lower() not in tag_names:
        id_to_add = max_id()[0]['max'] + 1
        cursor.execute(
            sql.SQL("INSERT INTO {table} VALUES (%s, %s);")
                .format(table=sql.Identifier('tag')), [id_to_add, tag_name.title()]
        )
        cursor.execute(
            sql.SQL("INSERT INTO {table} VALUES (%s, %s);")
                .format(table=sql.Identifier('question_tag')), [question_id, id_to_add]
        )
    else:
        print('Debug: Already There')


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
            "SELECT * from {table} WHERE to_tsvector('simple_english_no_stop',{col1}) @@ to_tsquery('simple_english_no_stop', %s) OR to_tsvector('simple_english_no_stop', {col2}) @@ to_tsquery('simple_english_no_stop' ,%s) ORDER BY {col3} desc;")

            .format(table=sql.Identifier('question'),
                    col1=sql.Identifier('title'),
                    col2=sql.Identifier('message'),
                    col3=sql.Identifier('vote_number')), [phrase_for_query, phrase_for_query]
    )
#     cursor.execute(f"""
#                     SELECT * FROM question WHERE title LIKE '%{phrase_for_query}%' OR message LIKE '%{phrase_for_query}%';
# """)
    questions_found = cursor.fetchall()
    return questions_found


@connection.connection_handler
def add_question_comment(cursor, message, question_id, answer_id, user_id):
    date = util.datetime.today()
    submission_time = date.now().strftime("%Y-%m-%d %H:%M:%S")
    print(question_id)
    print(answer_id)
    if question_id is not None:
        cursor.execute(
            """
            INSERT INTO comment (question_id, message, submission_time, edited_count, user_id) 
            VALUES ('{question_id}', '{message}', '{submission_time}', '0', {user_id});
            """.format(question_id=question_id,
                       message=message,
                       submission_time=submission_time,
                       user_id=user_id)
        )
    else:
        cursor.execute(
            """
            INSERT INTO comment (answer_id, message, submission_time, edited_count, user_id) 
            VALUES ('{answer_id}', '{message}', '{submission_time}', '0', {user_id});
            """.format(answer_id=answer_id,
                       message=message,
                       submission_time=submission_time,
                       user_id=user_id)
        )


@connection.connection_handler
def add_user_in_db(cursor, value_username, value_password):
    cursor.execute(
        sql.SQL("INSERT INTO {table} ({col1}, {col2})VALUES (%s, %s);")
            .format(table=sql.Identifier('person'),
                    col1=sql.Identifier('username'),
                    col2=sql.Identifier('password')), [value_username, value_password]

    )


@connection.connection_handler
def update_accept_answer(cursor, answer_id):
    cursor.execute(
        sql.SQL("UPDATE {table} SET {col1} = TRUE WHERE {col2} = %s;")
            .format(table=sql.Identifier('answer'),
                    col1=sql.Identifier('accepted'),
                    col2=sql.Identifier('id')), [answer_id]
    )
    cursor.execute(
        sql.SQL(
            "SELECT {table1}.{col1} , {table2}.{col3} FROM {table1} JOIN {table2} ON {table1}.{col1} = {table2}.{col2} WHERE {table1}.{col2} = %s LIMIT 1;")
            .format(
            table1=sql.Identifier('answer'),
            col1=sql.Identifier('user_id'),
            table2=sql.Identifier('person'),
            col2=sql.Identifier('id'),
            col3=sql.Identifier('username')
        ), [answer_id]
    )
    user_id = cursor.fetchall()
    user_id_to_update = user_id[0]['user_id']
    cursor.execute(
        sql.SQL(
            "UPDATE {table1} SET {col1} = {col1}  + 15 WHERE {col2} = %s;"
        ).format(
            table1=sql.Identifier('person'),
            col1=sql.Identifier('reputation'),
            col2=sql.Identifier('id')
        ), [user_id_to_update]
    )


@connection.connection_handler
def update_clear_answer(cursor, answer_id):
    cursor.execute(f"""
                    UPDATE answer
                    SET accepted=false
                    WHERE id={answer_id};
""")


@connection.connection_handler
def get_password_by_username(cursor, username):
    cursor.execute(
        f"""
        SELECT password FROM person WHERE username='{username}';
"""
    )
    result = cursor.fetchone()
    password = result['password']
    return password


@connection.connection_handler
def verify_password(cursor, plain_text_password, hashed_password):
    hashed_bytes_password = hashed_password.encode('utf-8')
    return bcrypt.checkpw(plain_text_password.encode('utf-8'), hashed_bytes_password)


@connection.connection_handler
def get_username_by_user_id(cursor, user_id):
    cursor.execute(f"""
                   SELECT username FROM person
                   WHERE id='{user_id}';
""")
    result = cursor.fetchone()
    target_user_username = result['username']
    return target_user_username


@connection.connection_handler
def get_all_user_questions(cursor, user_id):
    cursor.execute(f"""
            SELECT person.username, question.title, question.id FROM person
            JOIN question ON person.id = question.user_id
            WHERE person.id={user_id}
            ;
""")
    user_questions = cursor.fetchall()
    return user_questions


@connection.connection_handler
def get_all_user_answers(cursor, user_id):
    cursor.execute(f"""
            SELECT person.username, answer.message, answer.question_id FROM person
            JOIN answer ON person.id = answer.user_id
            WHERE person.id={user_id}
            ;
""")
    user_answers = cursor.fetchall()
    return user_answers


@connection.connection_handler
def get_all_user_comments(cursor, user_id):
    cursor.execute(f"""
            SELECT person.username, 
                    comment.message, 
                    comment.question_id, 
                    comment.answer_id, 
                    ( SELECT answer.question_id FROM answer
                        WHERE id=comment.answer_id) AS answers_linked_question_id
            FROM person
            JOIN comment ON person.id = comment.user_id
            WHERE person.id={user_id}
            ;
""")
    user_comments = cursor.fetchall()
    return user_comments


@connection.connection_handler
def get_user_id_by_username(cursor, username):
    cursor.execute(f"""
                           SELECT id FROM person
                           WHERE username='{username}';
        """)
    result = cursor.fetchone()
    user_id = result['id']
    return user_id


@connection.connection_handler
def count_number_of_tags(cursor):
    cursor.execute(
        sql.SQL("""
            SELECT COUNT(question_id) AS Number, tag_id, tag.name
            FROM question_tag
            JOIN tag ON question_tag.tag_id = tag.id
            GROUP BY tag_id, tag.name
        """)
        )

    data = cursor.fetchall()
    return data


@connection.connection_handler
def get_list_users(cursor):
    cursor.execute(
        f""" SELECT username, created, reputation FROM person;
"""
    )
    result = cursor.fetchall()
    return result


@connection.connection_handler
def get_newest_questions(cursor):
    cursor.execute(f"""
                    SELECT question.*, person.username AS username FROM question
                    JOIN person ON question.user_id = person.id
                    ORDER BY submission_time DESC 
                    LIMIT 5;
""")
    newest_questions = cursor.fetchall()
    return newest_questions


@connection.connection_handler
def get_username_by_question_id(cursor, question_id):
    cursor.execute(f"""
                    SELECT person.username FROM person
                    JOIN question ON person.id = question.user_id
                    WHERE question.id={question_id};
""")
    result = cursor.fetchone()
    db_username_by_question_id = result['username']
    return db_username_by_question_id


@connection.connection_handler
def get_accepted_value_for_answer(cursor, answer_id):
    cursor.execute(f"""
                    SELECT accepted FROM answer 
                    WHERE id={answer_id};
""")
    result = cursor.fetchone()
    current_accepted_value = result['accepted']
    return current_accepted_value


@connection.connection_handler
def get_question_data_and_username(cursor, question_id):
    cursor.execute(f"""
                    SELECT question.*, person.username AS username FROM question
                    JOIN person ON question.user_id = person.id
                    WHERE question.id = {question_id};
""")
    question = cursor.fetchone()
    return question


@connection.connection_handler
def get_question_status_for_user(cursor, question_id, username):
    cursor.execute(f"""
                    SELECT status FROM question_status
                    WHERE question_id={question_id} AND username='{username}';
""")
    result = cursor.fetchone()
    status = result['status']
    return status


@connection.connection_handler
def set_question_status_for_user(cursor, question_id, username):
    cursor.execute(f"""
                    INSERT INTO question_status (question_id, status, username)
                    VALUES ({question_id}, 0, '{username}');
""")


@connection.connection_handler
def get_answer_status_for_user(cursor, answer_id, username):
    cursor.execute(f"""
                        SELECT status FROM answer_status
                        WHERE answer_id={answer_id} AND username='{username}';
    """)
    result = cursor.fetchone()
    status = result['status']
    return status


@connection.connection_handler
def set_answer_status_for_user(cursor, answer_id, username):
    cursor.execute(f"""
                    INSERT INTO answer_status (answer_id, status, username)
                    VALUES ({answer_id}, 0, '{username}');
""")


@connection.connection_handler
def question_status_plus_one(cursor, question_id, username):
    cursor.execute(f"""
                    UPDATE question_status
                    SET status = status + 1
                    WHERE question_id={question_id} AND username='{username}';
""")


@connection.connection_handler
def question_status_minus_one(cursor, question_id, username):
    cursor.execute(f"""
                    UPDATE question_status
                    SET status = status - 1
                    WHERE question_id={question_id} AND username='{username}';
""")


@connection.connection_handler
def answer_status_plus_one(cursor, answer_id, username):
    cursor.execute(f"""
                    UPDATE answer_status
                    SET status = status + 1
                    WHERE answer_id={answer_id} AND username='{username}';
""")


@connection.connection_handler
def answer_status_minus_one(cursor, answer_id, username):
    cursor.execute(f"""
                    UPDATE answer_status
                    SET status = status - 1
                    WHERE answer_id={answer_id} AND username='{username}';
""")
