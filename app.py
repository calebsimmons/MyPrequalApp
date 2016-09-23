from flask import (Flask, g, render_template, flash, redirect, url_for,
                   abort)
from flask.ext.bcrypt import check_password_hash
from flask.ext.login import (LoginManager, login_user, logout_user,
                             login_required, current_user)

import forms
import models

DEBUG = True
PORT = 8000
HOST = 'localhost'

app = Flask(__name__)
app.secret_key = '571XD1GkpmhtnFxpyg5x'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view='login'

@login_manager.user_loader
def load_user(userid):
    try:
        return models.User.get(models.User.id == userid)
    except models.DoesNotExist:
        return None


@app.before_request
def before_request():
    """Connect to the database before each request."""
    g.db = models.DATABASE
    g.db.connect()
    g.user = current_user

@app.after_request
def after_request(response):
    """Close the database connection after each request."""
    g.db.close()
    return response

@app.route('/register', methods=('GET','POST'))
def register():
    form = forms.RegisterForm()
    if form.validate_on_submit():
        flash("Yay, you are registered!",'success')
        models.User.create_user(
            username = form.username.data,
            email = form.email.data,
            password = form.password.data
        )
        return redirect(url_for('index'))
    return render_template('register.html',form=form)

@app.route('/login',methods=('GET','POST'))
def login():
    form = forms.LoginForm()
    if form.validate_on_submit():
        try:
            user = models.User.get(models.User.email == form.email.data)
        except models.DoesNotExist:
            flash("Your email or password doesn't match!","error")
        else:
            if check_password_hash(user.password, form.password.data):
                login_user(user)
                flash("You've been logged in!","success")
                return redirect(url_for('index'))
            else:
                flash("Your email or password doesn't match!","error")
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You've been logged out!",'success')
    return redirect(url_for('index'))

@app.route('/request_letter/',methods=('GET','POST'))
@login_required
def request_letter():
    form = forms.LetterRequest()
    if form.validate_on_submit():
        base_loan_amount = form.sales_price.data-form.down_payment.data
        print base_loan_amount
        total_loan_amount = base_loan_amount
        models.LoanProposal.create(
            borrower = g.user._get_current_object(),
            loan_program = form.loan_program.data,
            sales_price = float(form.sales_price.data),
            base_loan_amount = float(base_loan_amount),
            total_loan_amount = float(total_loan_amount),
            rate = float(form.rate.data)
        )
        flash("We have recived your request!","success")
        return redirect(url_for('index'))
    return render_template('request_letter.html',form=form)

@app.route('/view_letters/')
@login_required
def view_letters():
    letters = current_user.get_letters().limit(100)
    return render_template('available_letters.html',letters=letters)


@app.route('/')
def index():
    if g.user._get_current_object():
        user = current_user
    return render_template('index.html',user=user)

@app.errorhandler(404)
def not_fount(error):
    return render_template('404.html'), 404

if __name__ == '__main__':
    models.initialize()
    try:
        models.User.create_user(
            username = 'calebsimmons',
            email = 'csimmons@freedmont.com',
            password = 'Fr33dm0nt1',
            admin=True
        )
    except ValueError:
        pass
    app.run(debug=DEBUG,host=HOST,port=PORT)
