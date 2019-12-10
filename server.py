from flask import Flask, render_template, request, redirect, url_for
import connection
import data_manager

app = Flask(__name__)
FILE = 'data/questions.csv'

@app.route('/list')
def route_index():
    questions = connection.read_questions(FILE)

    return render_template('index.html', questions=questions)


@app.route('/question/<question_id>')
def route_question(question_id):
    pass


@app.route('/add-question')
def route_add_question():
    pass


@app.route('/question/<question_id>/edit')
def route_edit_question(question_id):
    pass


@app.route('/question/<question_id>/delete')
def route_delete_question(question_id):
    questions = data_manager.delete_question(question_id)
    return render_template('index.html', questions=questions)


@app.route('/question/<question_id>/new-answer')
def route_add_answer(question_id):
    pass


@app.route('/answer/<answer_id>/delete')
def route_delete_answer(answer_id):
    answers = data_manager.delete_answer(answer_id)
    return render_template('question.html', answers=answers)


@app.route('/question/<question_id>/vote_up')
def route_question_vote_up(question_id):
    pass


@app.route('/question/<question_id>/vote_down')
def route_question_vote_down(question_id):
    pass


@app.route('/answer/<answer_id>/vote_up')
def route_answer_vote_up(answer_id):
    pass


@app.route('/answer/<answer_id>/vote_down')
def route_answer_vote_down(answer_id):
    pass


if __name__ == "__main__":
    app.run(
        debug=True,
        host="localhost",
        port=7070
    )
