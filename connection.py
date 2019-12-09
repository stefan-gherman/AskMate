import csv

QUESTIONS_HEADER = ['id', 'submission_time', 'view_number', 'vote_number', 'title', 'message', 'image']
ANSWERS_HEADER = ['id', 'submission_time', 'vote_number', 'question_id', 'message', 'image']


def read_questions(csv_file):
    question_list = []
    with open(csv_file, 'r') as csvfile:
        csvreader = csv.DictReader(csvfile)
        for row in csvreader:
            question_list.append(row)
    return question_list


def read_answers(csv_file):
    answers_list = []
    with open(csv_file, 'r') as csvfile:
        csvreader = csv.DictReader(csvfile)
        for row in csvreader:
            answers_list.append(row)
    return answers_list


def write_questions(csv_file, data:list):
    with open(csv_file, 'w+', newline='') as csvfile:
        csvwriter = csv.DictWriter(csvfile, fieldnames=QUESTIONS_HEADER)
        csvwriter.writeheader()
        for question in data:
            csvwriter.writerow(question)


def write_answers(csv_file, data:list):
    with open(csv_file, 'w+', newline='') as csvfile:
        csvwriter = csv.DictWriter(csvfile, fieldnames=ANSWERS_HEADER)
        csvwriter.writeheader()
        for answear in data:
            csvwriter.writerow(answear)