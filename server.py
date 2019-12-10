from flask import Flask, render_template, redirect, request, url_for
import data_manager as data_manager

app = Flask(__name__)


@app.route('/list')
def route_index():
    return render_template('index.html')


@app.route('/question/<question_id>')
def route_question(question_id):
    pass


@app.route('/add-question', methods=['GET', 'POST'])
def route_add_question():
    id = data_manager.add_question()
    if request.method == 'POST':
        data_manager.add_question()
        return redirect(url_for('route_question', question_id=id))
    return render_template('addquestion.html')


@app.route('/question/<question_id>/edit')
def route_edit_question(question_id):
    pass


@app.route('/question/<question_id>/delete')
def route_delete_question(question_id):
    pass


@app.route('/question/<question_id>/new-answer')
def route_add_answer(question_id):
    pass


@app.route('/answer/<answer_id>/delete')
def route_delete_answer(answer_id):
    pass


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
        port="7070"
    )
