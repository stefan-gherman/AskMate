from flask import Flask, request, render_template, redirect, url_for
import connection as con
import util as ut
app = Flask(__name__)

@app.route('/')
@app.route('/list')
def route_index():
    return render

#test
@app.route('/question/<question_id>', methods = ['GET', 'POST'])
def route_question(question_id):
    questions = con.read_questions('data/questions.csv')
    questions[int(question_id)]['view_number'] = str(int( questions[int(question_id)]['view_number']) + 1)
    con.write_questions('data/questions.csv', questions)
    questions = questions[int(question_id)]
    answers = con.read_answers('data/answers.csv')
    return render_template('question.html', questions = questions, answers = answers, question_id = question_id)
#test

@app.route('/add-question')
def route_add_question():
    pass


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

#test
question_headers = con.return_questions_headers()
@app.route('/test_this', methods = ['GET', 'POST'])
def route_test_this():
    if request.method == 'GET':
        print(request.values.get('param'), request.values.get('sort_ord'))
        questions = con.read_questions('data/questions.csv')
        param = request.values.get('param')
        sort_ord = request.values.get('sort_ord')
        questions = ut.make_compat_display(questions, 'not_textarea')
        questions_ordered = ut.order_by_value(questions, param, sort_ord)
        if questions_ordered == None:
            con.write_questions('data/questions.csv', questions)
            questions_ordered = ut.order_by_value(questions, 'submission_time', 'desc')
            return render_template('test_page.html', question_headers=question_headers, questions=questions_ordered)
        else:
            con.write_questions('data/questions.csv', questions_ordered)
            return render_template('test_page.html', question_headers=question_headers, questions=questions_ordered)
#test
if __name__ == "__main__":
    app.run(
        debug=True,
        host="0.0.0.0",
        port= 7070
    )
