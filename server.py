from flask import Flask, render_template, redirect, request, url_for
import data_manager as data_manager
import connection as connection
import util as util

app = Flask(__name__)


# @app.route('/')
# @app.route('/list')
# def route_index():
#     FILE = 'data/questions.csv'
#     questions = connection.read_questions(FILE)
#     return render_template('index.html', questions=questions)

update_views = True
@app.route('/question/<question_id>', methods=['GET', 'POST'])
def route_question(question_id):
    global update_views
    questions = connection.read_questions('data/questions.csv')
    print(update_views)
    if update_views == True:
        questions[int(question_id)]['view_number'] = int(questions[int(question_id)]['view_number']) + 1
        connection.write_questions('data/questions.csv', questions)
    for elem in range(len(questions)):
        for key in questions[elem].keys():
            if question_id == questions[elem]['id']:
                pos = elem
    questions = questions[pos]
    answers = connection.read_answers('data/answers.csv')
    return render_template('question.html', questions=questions, answers=answers, question_id=question_id)


@app.route('/add-question', methods=['GET', 'POST'])
def route_add_question():
    global update_views
    if request.method == 'POST':
        title = request.form['title']
        message = request.form['message']
        data_manager.add_question(title, message)
        questions_list = connection.read_questions(data_manager.QUESTIONS_FILE)
        update_views = True
        return redirect(url_for("route_question", question_id=str(len(questions_list) - 1)))
    else:
        return render_template('add_question.html')


@app.route('/question/<question_id>/edit')
def route_edit_question(question_id):
    global update_views
    update_views = False
    pass


@app.route('/question/<question_id>/delete')
def route_delete_question(question_id):
    questions = data_manager.delete_question(question_id)
    return redirect(request.referrer)


@app.route('/question/<question_id>/new-answer', methods=['GET', 'POST'])
def route_add_answer(question_id):
    global update_views
    update_views = False
    if request.method == 'POST':
        message = request.form['message']
        data_manager.add_answer(question_id, message)
        return redirect(url_for('route_question', question_id=question_id))
    return render_template('add_answer.html', question_id=question_id)


@app.route('/answer/<answer_id>/delete')
def route_delete_answer(answer_id):
    global update_views
    update_views = False
    answers = data_manager.delete_answer(answer_id)
    return redirect(request.referrer)


@app.route('/question/<question_id>/vote_up')
def route_question_vote_up(question_id):
    data_manager.vote_question(question_id, 'vote_up')
    return redirect('/list')


@app.route('/question/<question_id>/vote_down')
def route_question_vote_down(question_id):
    data_manager.vote_question(question_id, 'vote_down')
    return redirect('/list')


@app.route('/answer/<answer_id>/vote_up')
def route_answer_vote_up(answer_id):
    global update_views
    update_views = False
    data_manager.vote_answer(answer_id, 'vote_up')
    return redirect(request.referrer)


@app.route('/answer/<answer_id>/vote_down')
def route_answer_vote_down(answer_id):
    global update_views
    update_views = False
    data_manager.vote_answer(answer_id, 'vote_down')
    return redirect(request.referrer)

@app.route('/')
@app.route('/list', methods=['GET', 'POST'])
def route_index():
    global update_views
    update_views = True
    question_headers = connection.return_questions_headers()
    if request.method == 'GET':
        print(request.values.get('param'), request.values.get('sort_ord'))
        questions = connection.read_questions('data/questions.csv')
        param = request.values.get('param')
        sort_ord = request.values.get('sort_ord')
        questions = util.make_compat_display(questions, 'not_textarea')
        questions_ordered = util.order_by_value(questions, param, sort_ord)
        if questions_ordered == None:
            connection.write_questions('data/questions.csv', questions)
            questions_ordered = util.order_by_value(questions, 'submission_time', 'desc')
            return render_template('index.html', question_headers=question_headers, questions=questions_ordered)
        else:
            connection.write_questions('data/questions.csv', questions_ordered)
            return render_template('index.html', question_headers=question_headers, questions=questions_ordered)


# test
if __name__ == "__main__":
    app.run(
        debug=True,
        host="0.0.0.0",
        port=7070
    )
