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
    global update_views
    questions = connection.read_questions('data/questions.csv')
    print('update_views', update_views, type(update_views))
    connection.write_questions('data/questions.csv', questions)
    questions = connection.read_questions('data/questions.csv')
    for elem in range(len(questions)):
        for key in questions[elem].keys():
            if str(question_id) == str(questions[elem]['id']):
                pos = elem
                print(pos)
                if update_views == True and key == 'view_number':
                    print('sum to be assigned:', str(int(questions[elem]['view_number']) + 1) )
                    questions[elem]['view_number'] = str(int(questions[elem]['view_number']) + 1)
                connection.write_questions('data/questions.csv', questions)
                questions = connection.read_questions('data/questions.csv')
    questions = questions[pos]
    answers = connection.read_answers('data/answers.csv')
    update_views = False
    return render_template('question.html', questions=questions, answers=answers, question_id=question_id)


@app.route('/add-question', methods=['GET', 'POST'])
def route_add_question():
    global update_views
    if request.method == 'POST':
        random_file_name = util.random_string()
        title = request.form['title']
        message = util.make_compat_display(request.form['message'])
        file = request.files['file']
        filename = secure_filename(file.filename)
        if file and data_manager.allowed_file(file.filename):
            # filename = secure_filename(file.filename)
            extension = filename[-4:]
            filename = str(random_file_name) + extension
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        data_manager.add_question(title, message, filename)

        update_views = False
        return redirect(url_for("route_index"))
    else:
        return render_template('add_question.html')


@app.route('/question/<question_id>/edit', methods = ['GET', 'POST'])
def route_edit_question(question_id):
    global update_views
    update_views = False
    edit_me = True
    questions = connection.read_questions('data/questions.csv')
    for elem in range(len(questions)):
       if str(questions[elem]['id']) == str(question_id):
           pos = elem
    question = questions[pos]
    if request.method == 'POST':
        title = request.form['title']
        message = request.form['message']
        message = util.make_compat_display(message,'not_textarea')
        data_manager.edit_question(question_id,title,message)
        return redirect(url_for("route_index"))
    if request.method == 'GET':
        question['message'] = util.make_compat_display(question['message'], 'textarea')
        id_q = question['id']
        return render_template('add_question.html', edit_me = edit_me, question = question, id_q = id_q)


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
        file = request.files['file']
        filename = secure_filename(file.filename)
        if file and data_manager.allowed_file(file.filename):
            print(file)
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
    reset_default = None
    question_headers = connection.return_questions_headers()
    if request.method == 'GET':
        questions = connection.read_questions('data/questions.csv')
        param = request.values.get('param')
        sort_ord = request.values.get('sort_ord')
        print(reset_default)
        if reset_default is False:
            param = None
            sort_ord = None
        print(param, sort_ord)
        questions = util.make_compat_display(questions, 'not_textarea')
        #print(questions_ordered)
        if param is None and sort_ord is None:
            update_views = True
            connection.write_questions('data/questions.csv', questions)
            questions_ordered = data_manager.sort_questions('submission_time', 'asc')
            reset_default = True
            print(reset_default)
            return render_template('index.html', question_headers=question_headers, questions=questions_ordered)

        else:
            update_views = True
            reset_default = False
            print(reset_default)
            questions_ordered = data_manager.sort_questions(param, sort_ord)
            connection.write_questions('data/questions.csv', questions_ordered)
            return render_template('index.html', question_headers=question_headers, questions=questions_ordered)

    elif request.method == 'POST':
        questions = connection.read_questions('data/questions.csv')
        param = request.values.get('param')
        sort_ord = request.values.get('sort_ord')
        questions = util.make_compat_display(questions, 'not_textarea')
        questions_ordered = data_manager.sort_questions(param, sort_ord)


# @app.route('/')
@app.route('/list_questions')
def list_questions():
    questions = data_manager.list_first_questions()

    return render_template('list_questions.html', questions=questions)


@app.route('/list_all_answers')
def list_answers():
    answers_to_display = data_manager.list_all_the_answers()

    return render_template('list_questions.html', answers_to_display=answers_to_display)


@app.route('/question/<question_id>/')
def delete_sql_question(question_id):
    question_to_delete = int(question_id)
    data_manager.delete_sql_questions(question_to_delete)

    return render_template('list_questions.html')


@app.route('/answer/<answer_id>/')
def delete_sql_answer(answer_id):
    answer_to_delete = int(answer_id)
    data_manager.delete_sql_answers(answer_to_delete)

    return render_template('list_questions.html')


@app.route('/add_image_question/<path>/<question_id>/')
def add_image_to_question(path, question_id):
    id_to_insert_image = int(question_id)
    question_with_image=data_manager.add_image_in_question(path, id_to_insert_image)

    return render_template('list_questions.html', question_with_image=question_with_image)


@app.route('/add_image_answer/<path>/<answer_id>/')
def add_image_to_answer(path, answer_id):
    id_to_insert_image = int(answer_id)
    answer_with_image=data_manager.add_image_in_answer(path, id_to_insert_image)

    return render_template('list_questions.html', answer_with_image=answer_with_image)


if __name__ == "__main__":
    app.run(
        debug=True,
        host="0.0.0.0",
        port=6372
    )
