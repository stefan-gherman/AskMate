from flask import Flask, render_template, redirect, request, url_for, session
import os
import data_manager as data_manager
import connection as connection
import util as util
from werkzeug.utils import secure_filename


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = data_manager.UPLOAD_FOLDER
app.secret_key = os.urandom((20))
app.config['SERVER_NAME'] = '192.168.0.221:5000'
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

    tags = data_manager.get_tag_questions(question_id_conv)
    global update_views

    if update_views == True:
        data_manager.update_views(question_id_conv)
    # questions = dict(data_manager.display_question(question_id_conv).pop())
    question = data_manager.get_question_data_and_username(question_id)
    answers = data_manager.display_answers(question_id_conv)
    comments = util.read_comments_sql()
    question_comments = util.read_question_comments(question_id)
    update_views = False
    db_username_by_question_id = data_manager.get_username_by_question_id(question_id)
    return render_template('question.html',
                           question=question,
                           answers=answers,
                           question_id=question_id_conv,
                           question_comments=question_comments,
                           comments=comments,
                           tags=tags,
                           db_username_by_question_id=db_username_by_question_id
                           )


@app.route('/add-question', methods=['GET', 'POST'])
def route_add_question():
    global update_views
    if request.method == 'POST':
        random_file_name = util.random_string()
        title = request.form['title']
        title = title.rstrip('?')
        title = title + ' ' + '?'
        message = util.make_compat_display(request.form['message'])
        message = message.replace("'", "''")
        title = title.replace("'", "''")
        file = request.files['file']
        filename = secure_filename(file.filename)
        user_id = data_manager.get_user_id_by_username(session['username'])
        print(user_id)
        if file and data_manager.allowed_file(file.filename):
            extension = filename[-4:]
            filename = str(random_file_name) + extension
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        data_manager.add_question(title, message, filename, user_id)
        # print(session['username'], ' this is the session.')
        update_views = False
        return redirect(url_for("route_index", username='text_text'))
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
        title = title.rstrip('?')
        title = title + ' ' + '?'
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
        user_id = data_manager.get_user_id_by_username(session['username'])
        data_manager.add_answer(question_id, message, filename, user_id)
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
    try:
        status = data_manager.get_question_status_for_user(question_id, session['username'])
    except:
        data_manager.set_question_status_for_user(question_id, session['username'])
    question_id_conv = int(question_id)
    status = data_manager.get_question_status_for_user(question_id, session['username'])
    if status == 0 or status == -1:
        data_manager.vote_item_up_down(question_id_conv, 'question', 'up')
        data_manager.question_status_plus_one(question_id, session['username'])
        return redirect(request.referrer)
    else:
        return redirect(request.referrer)


@app.route('/question/<question_id>/vote_down')
def route_question_vote_down(question_id):
    try:
        status = data_manager.get_question_status_for_user(question_id, session['username'])
    except:
        data_manager.set_question_status_for_user(question_id, session['username'])
    question_id_conv = int(question_id)
    status = data_manager.get_question_status_for_user(question_id, session['username'])
    if status == 0 or status == 1:
        data_manager.vote_item_up_down(question_id_conv, 'question', 'down')
        data_manager.question_status_minus_one(question_id, session['username'])
        return redirect(request.referrer)
    else:
        return redirect(request.referrer)


@app.route('/answer/<answer_id>/vote_up')
def route_answer_vote_up(answer_id):
    try:
        status = data_manager.get_answer_status_for_user(answer_id, session['username'])
    except:
        data_manager.set_answer_status_for_user(answer_id, session['username'])
    global update_views
    global questions_found
    update_views = False
    answer_id_conv = int(answer_id)
    status = data_manager.get_answer_status_for_user(answer_id, session['username'])
    if status == 0 or status == -1:
        data_manager.vote_item_up_down(answer_id_conv, 'answer', 'up')
        data_manager.answer_status_plus_one(answer_id, session['username'])
        return redirect(request.referrer)
    else:
        return redirect(request.referrer)


@app.route('/answer/<answer_id>/vote_down')
def route_answer_vote_down(answer_id):
    try:
        status = data_manager.get_answer_status_for_user(answer_id, session['username'])
    except:
        data_manager.set_answer_status_for_user(answer_id, session['username'])
    global update_views
    global questions_found
    update_views = False
    answer_id_conv = int(answer_id)
    status = data_manager.get_answer_status_for_user(answer_id, session['username'])
    if status == 0 or status == 1:
        data_manager.vote_item_up_down(answer_id_conv, 'answer', 'down')
        data_manager.answer_status_minus_one(answer_id, session['username'])
        return redirect(request.referrer)
    else:
        return redirect(request.referrer)


param = None
sort_ord = None


@app.route('/')
def route_home():
    newest_questions = data_manager.get_newest_questions()
    return render_template('home.html',
                           questions=newest_questions)


@app.route('/list', methods=['GET', 'POST'])
def route_index():
    global update_views
    update_views = True
    global param
    global sort_ord
    show_sort = True
    question_headers = connection.return_questions_headers()
    if request.method == 'GET':
        param = request.values.get('param')
        sort_ord = request.values.get('sort_ord')
        print(param, sort_ord)
        if param is None and sort_ord is None:
            update_views = True
            questions_ordered = data_manager.sort_questions('submission_time', 'desc')

            return render_template('index.html', question_headers=question_headers, questions=questions_ordered,
                                   param_display='Submission Time', order_display='Descending', show_sort=show_sort)
        else:
            update_views = True
            questions_ordered = data_manager.sort_questions(param, sort_ord)
            if sort_ord == 'asc':
                order_display = 'Ascending'
            elif sort_ord == 'desc':
                order_display = 'Descending'
            if param == 'submission_time':
                param_display = 'Submission Time'
            elif param == 'title':
                param_display = 'Title'
            elif param == 'vote_number':
                param_display = 'Vote Number'
            elif param == 'view_number':
                param_display = 'View Number'
            return render_template('index.html', question_headers=question_headers, questions=questions_ordered,
                                   order_display=order_display, param_display=param_display, show_sort=show_sort)

    # elif request.method == 'POST':
    #     questions = connection.read_questions('data/questions.csv')
    #     param = request.values.get('param')
    #     sort_ord = request.values.get('sort_ord')
    #     questions = util.make_compat_display(questions, 'not_textarea')
    #     questions_ordered = data_manager.sort_questions(param, sort_ord)


@app.route('/question/<question_id>/')
def delete_sql_question(question_id):
    global questions_found
    question_to_delete = int(question_id)
    data_manager.delete_sql_questions(question_to_delete)
    return redirect(url_for('route_home'))


@app.route('/answer/<answer_id>/')
def delete_sql_answer(answer_id):
    answer_to_delete = int(answer_id)
    data_manager.delete_sql_answers(answer_to_delete)
    return redirect(request.referrer)


@app.route('/question-new-tag/<question_id>')
def question_tag(question_id):
    question_id_to_add = int(question_id)
    return render_template('tag_question.html', question_id=question_id_to_add)


@app.route('/question/<question_id>/new-tag', methods=['GET', 'POST'])
def chose_question_tag(question_id):
    question_id_to_add = int(question_id)
    if request.method == 'GET':
        return render_template('tag_question.html', question_id=question_id_to_add)

    if request.method == 'POST':
        tag1_input = request.form.get('css')
        tag2_input = request.form.get('html')
        tag3_input = request.form.get('sql')
        tag4_input = request.form.get('php')
        tag5_input = request.form.get('java')
        tag6_input = request.form.get('cplus')
        tag7_input = request.form.get('javascript')
        tag8_input = request.form.get('python')
        new_tag_input = request.form.get('new_tag')

    tag_name_list = [tag1_input, tag2_input, tag3_input, tag4_input, tag5_input, tag6_input, tag7_input, tag8_input,
                     new_tag_input]

    for tag in tag_name_list:
        if tag is not None and tag != '':
            data_manager.add_tag(tag, question_id_to_add)

    #return route_question(question_id_to_add)
    return redirect(url_for('route_question', question_id = question_id_to_add))

@app.route('/question/<question_id>/tag/<tag_id>/delete')
def delete_one_tag(question_id, tag_id):
    question_on_page = int(question_id)
    tag_to_delete = int(tag_id)
    data_manager.delete_tag_questions(question_on_page, tag_to_delete)

    #return route_question(question_on_page)
    return redirect(url_for('route_question', question_id=question_on_page))

questions_found = []
phrase_for_query = ""


@app.route('/search', methods=['GET', 'POST'])
def return_search():
    show_sort = False
    global questions_found
    global search_phrase
    global phrase_for_query
    search_phrase = request.values.get('search')
    search_phrase_for_highlighting = search_phrase
    if search_phrase is None:
        questions_found = data_manager.search_for_phrase(phrase_for_query)
        search_phrase_for_highlighting = phrase_for_query
        for question in questions_found:
            question["title"] = util.apply_fancy(search_phrase_for_highlighting, question['title'])
            question["message"] = util.apply_fancy(search_phrase_for_highlighting, question['message'])
        search_res = []
        for question in questions_found:
            if '<span' in question['title'].split() or '<span' in question['message'].split():
                search_res.append(question)
        print('Search Res:', search_res)
        return render_template("search-results.html",
                               search_phrase=search_phrase,
                               questions=search_res,
                               show_sort=show_sort)

    search_phrase = search_phrase.split()
    print("Search phrase", search_phrase)
    phrase_for_query = str.join("&", search_phrase)
    print("Phrase for query", phrase_for_query)
    questions_found = data_manager.search_for_phrase(phrase_for_query)
    for question in questions_found:
        question["title"] = util.apply_fancy(search_phrase_for_highlighting, question['title'])
        question["message"] = util.apply_fancy(search_phrase_for_highlighting, question['message'])
    for question in questions_found:
        print('This is a question', question)
    search_res = []
    for question in questions_found:
        if '<span' in question['title'].split() or '<span' in question['message'].split():
            search_res.append(question)
    print('Search Res:', search_res)
    return render_template("search-results.html",
                           search_phrase=search_phrase,
                           questions=search_res,
                           show_sort=show_sort)


@app.route('/question/<question_id>/new-comment', methods=['GET', 'POST'])
def route_add_question_comment(question_id):
    answer_id = None
    if request.method == 'POST':
        message = request.form['message']
        user_id = data_manager.get_user_id_by_username(session['username'])
        data_manager.add_question_comment(message=message,
                                          question_id=question_id,
                                          answer_id=answer_id,
                                          user_id=user_id)
        return redirect(url_for('route_question', question_id=question_id))

    return render_template('add_comment.html',
                           question_id=question_id,
                           answer_id=answer_id)


@app.route('/answer/<answer_id>/new-comment', methods=['GET', 'POST'])
def route_add_answer_comment(answer_id):
    answer_id = answer_id
    question_id = util.read_question_id(answer_id)
    question_id = question_id[0]['question_id']
    if request.method == 'POST':
        message = request.form['message']
        user_id = data_manager.get_user_id_by_username(session['username'])
        data_manager.add_question_comment(message=message,
                                          question_id=None,
                                          answer_id=answer_id,
                                          user_id=user_id)
        return redirect(url_for('route_question',
                                question_id=question_id))

    return render_template('add_comment.html',
                           answer_id=answer_id,
                           id=question_id)


@app.route('/registration', methods=['GET', 'POST'])
def registration_page():
    return render_template('registration.html');


@app.route('/register_form', methods=['GET', 'POST'])
def register_user():
    if request.method == 'POST':
        input_username = request.form.get('username')
        input_password = request.form.get('password')
        input_confirm = request.form.get('confirm')

        if input_password == input_confirm:
            hash_password = util.hash_password(input_password)
            try:
                data_manager.add_user_in_db(input_username, hash_password)
            except:
                message_invalid = "Sorry, that username already exists!"
                return render_template('registration.html', message_invalid=message_invalid)
            return redirect(url_for('login'))
        else:
            message = 'Password confirmation unsuccessful. Please try again.'
            return render_template('registration.html', message=message)
    return render_template('registration.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            hashed_password = data_manager.get_password_by_username(request.form['username'])
            if data_manager.verify_password(request.form['password'], hashed_password):
                session['username'] = request.form['username']
                return redirect(url_for('route_home'))
            else:
                return render_template('login.html', alert_me=True)
        except:
            no_user_in_db_message = 'Username or password invalid.'
            return render_template('login.html',
                                   no_user_in_db_message=no_user_in_db_message)
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('route_home'))


@app.route('/user_accept_answer/<answer_id>')
def route_accept_answer(answer_id):
    current_accepted_value = data_manager.get_accepted_value_for_answer(answer_id)
    if current_accepted_value is False:
        data_manager.update_accept_answer(answer_id)
    else:
        data_manager.update_clear_answer(answer_id)
    return redirect(request.referrer)


@app.route('/user/<user_id>')
def display_user_activity(user_id):
    target_user_username = data_manager.get_username_by_user_id(user_id)
    target_user_questions = data_manager.get_all_user_questions(user_id)
    target_user_answers = data_manager.get_all_user_answers(user_id)
    target_user_comments = data_manager.get_all_user_comments(user_id)
    return render_template('user.html',
                           target_user_username=target_user_username,
                           target_user_questions=target_user_questions,
                           target_user_answers=target_user_answers,
                           target_user_comments=target_user_comments)


@app.route('/list_users')
def list_users():
    data_list_users = data_manager.get_list_users()
    return render_template('list_users.html', data_list_users=data_list_users)


@app.route('/tags')
def route_tags():
    data = data_manager.count_number_of_tags()
    names_list = []
    for elem in data:
        names_list.append(elem['name'])
    empty_dict = {}
    for tag in names_list:
        if tag not in empty_dict.keys():
            empty_dict[tag] = 1
        else:
            empty_dict[tag] += 1
    freq_counter = []
    for key in empty_dict.keys():
        freq_counter.append((key, empty_dict[key]))
    print(freq_counter)
    freq_counter = sorted(freq_counter,key = lambda element: element[1], reverse = True)
    print(freq_counter)
    sorted_by_freq = dict(freq_counter)
    return render_template('tags.html', data=sorted_by_freq)


if __name__ == "__main__":
    app.run(
        debug=True,
        host="0.0.0.0",
        port=5000
    )
