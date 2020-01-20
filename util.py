import connection as connection
from datetime import datetime
import data_manager as data_manager
import random
import string
from psycopg2 import sql

today = datetime.today()

def order_by_value(dataset, param, order='asc'):
    """
    :param dataset: a list of dictionaries
    :param param: the key of the inner dicts based on which the list is sorted
    :param order: default values takes 'asc' or 'desc'
    :return:

    """
    list_of_possible_key_ints = ['id', 'view_number', 'vote_number']
    if param in list_of_possible_key_ints:

        if order == 'desc':
            ordered_dataset = sorted(dataset, key=lambda i: int(i[param]), reverse=True)
        elif order == 'asc':
            ordered_dataset = sorted(dataset, key=lambda i: int(i[param]))
        return ordered_dataset
    elif param == 'submission_time':
        if order == 'desc':
            ordered_dataset = sorted(dataset, key=lambda i: datetime.strptime(i[param], "%Y-%m-%d-%H:%M:%S"),
                                     reverse=True)
        elif order == 'asc':
            ordered_dataset = sorted(dataset, key=lambda i: datetime.strptime(i[param], "%Y-%m-%d-%H:%M:%S"))
        return ordered_dataset
    else:
        if order == 'desc':
            ordered_dataset = sorted(dataset, key=lambda i: i[param].lower(), reverse=True)
            return ordered_dataset
        elif order == 'asc':
            ordered_dataset = sorted(dataset, key=lambda i: i[param].lower())
            return ordered_dataset


def make_compat_display(dataset, html_elem='not_textarea'):
    if type(dataset) == dict:
        if html_elem == 'not_textarea':
            for dicto in dataset:
                for key in dicto.keys():
                    dicto[key] = dicto[key].replace('\r\n', '<br/>')
        if html_elem == 'textarea':
            for dicto in dataset:
                for key in dicto.keys():
                    dicto[key] = dicto[key].replace('<br/>', '\r\n')
    elif type(dataset) == str:
        if html_elem == 'not_textarea':
            dataset = dataset.replace('\r\n', '<br/>')
        elif html_elem == 'textarea':
            dataset = dataset.replace('<br/>', '\r\n')
    return dataset


def question_list_size():
    questions_list = connection.read_questions(data_manager.QUESTIONS_FILE)
    return len(questions_list)


def random_string(string_length=10):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for x in range(string_length))


def apply_fancy(string,search_in):
    new_string = string.lower()
    new_string = new_string.split('+')
    final_string = search_in.split()
    search_in_new = search_in.lower()
    search_in_new = search_in_new.split()
    count_your_blessings = 0
    positions = []
    for string in new_string:
        for string_search in range(len(search_in_new)):
            if string == search_in_new[string_search]:
                count_your_blessings += 1
                positions.append(string_search)

    for pos in positions:
        final_string[pos] = f"<span style=\"color:red\">{final_string[pos]}</span>"
    final_string = str.join(" ", final_string)
    return final_string

@connection.connection_handler
def read_comments_sql(cursor):
    cursor.execute(
        """
        SELECT * FROM comment;
        """
    )

    comments = cursor.fetchall()
    return comments


@connection.connection_handler
def read_questions_sql(cursor):
    cursor.execute(
        """
        SELECT * FROM question;
        """
    )

    questions = cursor.fetchall()
    return questions


@connection.connection_handler
def read_answers_sql(cursor):
    cursor.execute(
        """
        SELECT * FROM answer
        """
    )

    answers = cursor.fetchall()


@connection.connection_handler
def read_question_comments(cursor, question_id):
    cursor.execute(
        """
        SELECT * FROM comment
        WHERE question_id='{id}'
        """.format(id=question_id)
    )

    question_comments = cursor.fetchall()
    return question_comments


@connection.connection_handler
def read_question_id(cursor, answer_id):
    cursor.execute(
        """
        SELECT question_id FROM answer
        WHERE id = '{answer_id}'
        """.format(answer_id=answer_id)
    )
    question_id = cursor.fetchall()
    return question_id

# @connection.connection_handler
# def read_answer_id(cursor, question_id):
#     cursor.execute(
#         """
#         SELECT id FROM answer
#         WHERE question_id = '{question_id}'
#         """.format(question_id=question_id)
#     )
#     question_id = cursor.fetchall()
#     return question_id
#
# print(read_answer_id(29))

@connection.connection_handler
def order_questions_by(cursor, order):
    if order == 'asc':
        cursor.execute(
            """
            SELECT * FROM question
            ORDER BY id asc ;
            """
        )
        questions_ordered = cursor.fetchall()
        return questions_ordered
    elif order == 'desc':
        cursor.execute(
            """
            SELECT * FROM question
            ORDER BY id desc ;
            """
        )
        questions_ordered = cursor.fetchall()
        return questions_ordered
