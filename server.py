from flask import Flask, render_template, redirect, request, url_for
import os
import data_manager as data_manager
import connection as connection
import util as util
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = data_manager.UPLOAD_FOLDER

# @app.route('/')
# @app.route('/list')
# def route_index():
#     FILE = 'data/questions.csv'
#     questions = connection.read_questions(FILE)
#     return render_template('index.html', questions=questions)

# @app.after_request
# def after_request(response):
#     response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
#     return response


update_views = True


@app.route('/question/<question_id>', methods=['GET', 'POST'])
def route_question(question_id):
    if question_id != '' and question_id is not None:
        question_id_conv = int(question_id)
    global update_views

    if update_views == True:
        data_manager.update_views(question_id_conv)
    questions = dict(data_manager.display_question(question_id_conv).pop())
    answers = data_manager.display_answers(question_id_conv)
    update_views = False
    return render_template('question.html', questions=questions, answers=answers, question_id=question_id_conv)


@app.route('/add-question', methods=['GET', 'POST'])
def route_add_question():
    global update_views
    if request.method == 'POST':
        random_file_name = util.random_string()
        title = request.form['title']
        message = util.make_compat_display(request.form['message'])
        message = message.replace("'", "''")
        title = title.replace("'", "''")
        file = request.files['file']
        filename = secure_filename(file.filename)
        if file and data_manager.allowed_file(file.filename):
            extension = filename[-4:]
            filename = str(random_file_name) + extension
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        data_manager.add_question(title, message, filename)
        update_views = False
        return redirect(url_for("route_index"))
    else:
        return render_template('add_question.html')


@app.route('/question/<question_id>/edit', methods=['GET', 'POST'])
def route_edit_question(question_id):
    question_id_conv = int(question_id)
    global update_views
    update_views = False
    edit_me = True
    if request.method == 'POST':
        title = request.form['title']
        message = request.form['message']
        message = util.make_compat_display(message, 'not_textarea')
        data_manager.update_question(question_id_conv, message, title)
        return redirect(url_for("route_index"))
    if request.method == 'GET':
        question = data_manager.display_question(question_id_conv)
        question[0]['message'] = util.make_compat_display(question[0]['message'], 'textarea')
        id_q = question[0]['id']
        return render_template('add_question.html', edit_me=edit_me, question=question, id_q=id_q)


@app.route('/question/<question_id>/<answer_id>/edit', methods=['GET', 'POST'])
def route_edit_answer(question_id, answer_id):
    global update_views
    update_views = False
    edit_me = True
    answer_id = answer_id.rstrip('}')
    if request.method == 'POST':
        answer_id_conv = int(answer_id)
        question_id_conv = int(question_id)
        message = request.form['message']
        message = util.make_compat_display(message, 'not_textarea')
        data_manager.update_answer(answer_id_conv, message)
        return redirect(url_for('route_question', question_id=question_id_conv))
    elif request.method == 'GET':
        answer_id_conv = int(answer_id)
        question_id_conv = int(question_id)
        answer = data_manager.display_answers(question_id_conv)
        for i in range(len(answer)):
            answer[i] = dict(answer[i])
        print('This is answer after conv', answer)
        for i in range(len(answer)):
            if answer[i]['id'] == answer_id_conv:
                answer_editable = answer[i]
        print('\n', 'This is the editable answer.', answer_editable)
        answer_editable['message'] = util.make_compat_display(answer_editable['message'], 'textarea')
        id_a = answer_editable['id']
        id_q = answer_editable['question_id']
        return render_template('add_answer.html', edit_me=edit_me, answer=answer_editable, id_q=id_q, id_a=id_a)


@app.route('/question/<question_id>/delete')
def route_delete_question(question_id):
    questions = data_manager.delete_question(question_id)
    return redirect(request.referrer)


@app.route('/question/<question_id>/new-answer', methods=['GET', 'POST'])
def route_add_answer(question_id):
    global update_views
    update_views = False
    if request.method == 'POST':
        random_file_name = util.random_string()
        message = util.make_compat_display(request.form['message'])
        message = message.replace("'", "''")
        file = request.files['file']
        filename = secure_filename(file.filename)
        if file and data_manager.allowed_file(file.filename):
            extension = filename[-4:]
            filename = str(random_file_name) + extension
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        data_manager.add_answer(question_id, message, filename)
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
    question_id_conv = int(question_id)
    data_manager.vote_item_up_down(question_id_conv, 'question', 'up')
    return redirect('/list')


@app.route('/question/<question_id>/vote_down')
def route_question_vote_down(question_id):
    question_id_conv = int(question_id)
    data_manager.vote_item_up_down(question_id_conv, 'question', 'down')
    return redirect('/list')


@app.route('/answer/<answer_id>/vote_up')
def route_answer_vote_up(answer_id):
    global update_views
    update_views = False
    answer_id_conv = int(answer_id)
    data_manager.vote_item_up_down(answer_id_conv, 'answer', 'up')
    return redirect(request.referrer)


@app.route('/answer/<answer_id>/vote_down')
def route_answer_vote_down(answer_id):
    global update_views
    update_views = False
    answer_id_conv = int(answer_id)
    data_manager.vote_item_up_down(answer_id_conv, 'answer', 'down')
    return redirect(request.referrer)


@app.route('/')
@app.route('/list', methods=['GET', 'POST'])
def route_index():
    global update_views
    update_views = True
    question_headers = connection.return_questions_headers()
    if request.method == 'GET':
        param = request.values.get('param')
        sort_ord = request.values.get('sort_ord')

        if param is None and sort_ord is None:
            update_views = True
            questions_ordered = data_manager.sort_questions('submission_time', 'asc')

            return render_template('index.html', question_headers=question_headers, questions=questions_ordered)
        else:
            update_views = True
            questions_ordered = data_manager.sort_questions(param, sort_ord)
            return render_template('index.html', question_headers=question_headers, questions=questions_ordered)

    # elif request.method == 'POST':
    #     questions = connection.read_questions('data/questions.csv')
    #     param = request.values.get('param')
    #     sort_ord = request.values.get('sort_ord')
    #     questions = util.make_compat_display(questions, 'not_textarea')
    #     questions_ordered = data_manager.sort_questions(param, sort_ord)

# @app.route('/')
@app.route('/list_questions')
def list_questions():
    questions = data_manager.list_first_questions()

    return render_template('list_questions.html', questions=questions)


@app.route('/question/<question_id>/')
def delete_sql_question(question_id):
    question_to_delete = int(question_id)
    data_manager.delete_sql_questions(question_to_delete)

    return redirect(request.referrer)


@app.route('/answer/<answer_id>/')
def delete_sql_answer(answer_id):
    answer_to_delete = int(answer_id)
    data_manager.delete_sql_answers(answer_to_delete)

    return redirect(request.referrer)


if __name__ == "__main__":
    app.run(
        debug=True,
        host="0.0.0.0",
        port=6372
    )
