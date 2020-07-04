from config import Config
from config import LoginForm
from flask import Flask
from flask import flash
from flask import redirect
from flask import render_template
from golf_bokning import TeeTimes
from golf_bokning import main

app = Flask(__name__)
app.config.from_object(Config)


@app.route('/', methods=['GET', 'POST'])
@app.route('home', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        TeeTimes
        return redirect('/home')
    return render_template('login.html', title='Sign In', form=form)

@app.route('/index', methods=['GET'])
def get_times():
    form = LoginForm()
    if form.validate_on_submit():
        main(form.username.data, form.password.data)
        return redirect('/home')
    return render_template('login.html', title='Sign In', form=form)
	return render_template('index.html', title='Times')



if __name__ == '__main__':
    app.run(debug=True)