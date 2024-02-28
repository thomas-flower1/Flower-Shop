from flask import Flask, render_template, url_for, session, redirect
from form import LoginForm, CreateAccountForm, ResetPasswordForm
from flask_session import Session
from database import get_db, close_db



app = Flask(__name__)
Session(app)
app.teardown_appcontext(close_db)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SECRET_KEY'] = 'my-secret-key'
app.config['SESSIO_PERMANANT'] = False



#TODO create a login page
@app.route('/login')
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = form.password
        profile = db.execute(
            '''SELECT * FROM users WHERE user_id =?;''', (username,)).fetchone() 
        if profile is None:
            pass
        #lead the user to a create account page

@app.route('/create_account')
def create_account():
    form = CreateAccountForm()


@app.route('/reset_password', methods=['POST', 'GET'])
def reset_password():
    '''Allows the user to send reset password, then redirects to the login page'''
    form = ResetPasswordForm()
    # if form.validate_on_submit():
    #     return redirect(url_for('login'))
    # return render_template('reset_password.html', form=form)
    
    


#TODO create a basket
@app.route('/basket')
def basket():
    pass

#TODO create a default page
@app.route('/flowers')
def flowers():
    db = get_db()
    flowers = db.execute(
        '''SELECT * FROM wines;''').fetchall()
    return render_template('flowers.html', flowers=flowers)
    



#TODO allow user to filter the default page
#TODO create an administrator that can add or remove
#TODO allow the user to receive emails
#TODO payment page
#TODO