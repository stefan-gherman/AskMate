import csv
import psycopg2
import os
import psycopg2.extras

QUESTIONS_HEADER = ['id', 'submission_time', 'view_number', 'vote_number', 'title', 'message', 'image']
ANSWERS_HEADER = ['id', 'submission_time', 'vote_number', 'question_id', 'message', 'image']


def read_questions(csv_file):
    with open(csv_file, 'r') as csvfile:
        csv_reader = csv.DictReader(csvfile)
        questions_list = [dict(row) for row in csv_reader]
    return questions_list


# test
def return_questions_headers():
    return QUESTIONS_HEADER[1:-2:1]


# test
def read_answers(csv_file):
    with open(csv_file, 'r') as csvfile:
        csv_reader = csv.DictReader(csvfile)
        answers_list = [dict(row) for row in csv_reader]
    return answers_list


def write_questions(csv_file, data):
    with open(csv_file, 'w+', newline='') as csvfile:
        csv_writer = csv.DictWriter(csvfile, fieldnames=QUESTIONS_HEADER)
        csv_writer.writeheader()
        for question in data:
            csv_writer.writerow(question)


def write_answers(csv_file, data: list):
    with open(csv_file, 'w+', newline='') as csvfile:
        csv_writer = csv.DictWriter(csvfile, fieldnames=ANSWERS_HEADER)
        csv_writer.writeheader()
        for answer in data:
            csv_writer.writerow(answer)

# Database connection Handler #

def get_connection_string():
    # setup connection string
    # to do this, please define these environment variables first
    user_name = os.environ.get('PSQL_USER_NAME')
    password = os.environ.get('PSQL_PASSWORD')
    host = os.environ.get('PSQL_HOST')
    database_name = os.environ.get('PSQL_DB_NAME')

    env_variables_defined = user_name and password and host and database_name

    if env_variables_defined:
        # this string describes all info for psycopg2 to connect to the database
        return 'postgresql://{user_name}:{password}@{host}/{database_name}'.format(
            user_name=user_name,
            password=password,
            host=host,
            database_name=database_name
        )
    else:
        raise KeyError('Some necessary environment variable(s) are not defined')


def open_database():
    try:
        connection_string = get_connection_string()
        connection = psycopg2.connect(connection_string)
        connection.autocommit = True
    except psycopg2.DatabaseError as exception:
        print('Database connection problem')
        raise exception
    return connection


def connection_handler(function):
    def wrapper(*args, **kwargs):
        connection = open_database()
        # we set the cursor_factory parameter to return with a RealDictCursor cursor (cursor which provide dictionaries)
        dict_cur = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        ret_value = function(dict_cur, *args, **kwargs)
        dict_cur.close()
        connection.close()
        return ret_value

    return wrapper

