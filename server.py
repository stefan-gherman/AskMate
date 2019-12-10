from flask import Flask, request, render_template

app = Flask(__name__)

@app.route('/')
@app.route('/list')
def route_index():
    return render

@app.route('/question/<question_id>')
def route_question(question_id):
    return render_template('index.html')


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

#test
if __name__ == "__main__":
    app.run(
        debug=True,
        host="0.0.0.0",
        port= 7070
    )
