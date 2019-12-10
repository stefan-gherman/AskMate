import csv

QUESTIONS_HEADER = ['id', 'submission_time', 'view_number', 'vote_number', 'title', 'message', 'image']
ANSWERS_HEADER = ['id', 'submission_time', 'vote_number', 'question_id', 'message', 'image']


def read_questions(csv_file):
    with open(csv_file, 'r') as csvfile:
        csv_reader = csv.DictReader(csvfile)
        questions_list = [dict(row) for row in csv_reader]
    return questions_list


def read_answers(csv_file):
    answers_list = []
    with open(csv_file, 'r') as csvfile:
        csv_reader = csv.DictReader(csvfile)
        answers_list = [dict(row) for row in csv_reader]
    return answers_list


def write_questions(csv_file, data:list):
    with open(csv_file, 'w+', newline='') as csvfile:
        csv_writer = csv.DictWriter(csvfile, fieldnames=QUESTIONS_HEADER)
        csv_writer.writeheader()
        for question in data:
            csv_writer.writerow(question)


def write_answers(csv_file, data:list):
    with open(csv_file, 'w+', newline='') as csvfile:
        csv_writer = csv.DictWriter(csvfile, fieldnames=ANSWERS_HEADER)
        csv_writer.writeheader()
        for answear in data:
            csv_writer.writerow(answear)