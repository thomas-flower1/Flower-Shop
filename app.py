from flask import Flask, render_template, url_for, session, redirect
from form import LoginForm, CreateAccountForm, ResetPasswordForm, FilterForm
from flask_session import Session
from database import get_db, close_db
from werkzeug.security import generate_password_hash, check_password_hash




app = Flask(__name__)
app.teardown_appcontext(close_db)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SECRET_KEY'] = 'hello'
app.config['SESSION_PERMANANT'] = False
app.secret_key = 'very-secret'
Session(app)


#TODO a filter, order price low to high, high to low, recommended

 


#TODO create a login page
@app.route('/login', methods=['POST', 'GET'])
def login():
    form = LoginForm()
    db = get_db
    if form.validate_on_submit():
        email = form.email.data
        password = form.password
        validUser = db.execute(
            '''SELECT * FROM users WHERE email =?;''', (email,)).fetchone() 
        if validUser is None:
            redirect (url_for('create_account'))
        elif not check_password_hash(validUser['password'], password):
            form.password.append('Incorrect Password')
        else:
            session.clear()
            session['username'] = db.execute(
                '''SELECT username FROM users WHERE email =?''',(email,)).fetchone()
            redirect (url_for('flowers'))
        
        #lead the user to a create account page
    return render_template('login.html', form=form)

@app.route('/create_account', methods=['POST', 'GET'])
def create_account():
    form = CreateAccountForm()
    db = get_db()
    if form.validate_on_submit():
        username = form.username.data
        
        email = form.email.data
        password = form.password.data

        check_username = db.execute(
            '''SELECT * FROM users WHERE username =?;''', (username,)).fetchone()
        
        
        check_email = db.execute(
            '''SELECT * FROM users WHERE email =?;''', (email,)).fetchone()
        
        if check_username:
            form.username.errors.append('Username is already taken.')
        if check_email:
            form.email.errors.append('Email already in use.')
        else:
            db.execute (
                '''INSERT INTO users(username, email, password) VALUES (?, ?, ?);''',(username, email, generate_password_hash(password)))
            db.commit()
            return redirect(url_for('flowers'))
    


        

        

    return render_template('account.html', form=form)

            




@app.route('/reset_password', methods=['POST', 'GET'])
def reset_password():
    '''Allows the user to send reset password, then redirects to the login page'''
    form = ResetPasswordForm()
    if form.validate_on_submit():
        return redirect(url_for('login'))
    #need to send an email to the user so they can reset the password
    return render_template('reset_password.html', form=form)


    


#TODO create a basket
@app.route('/basket')
def basket():
    pass

#TODO create a default page
@app.route('/')
def flowers():
    db = get_db()
    flowers = db.execute(
        '''SELECT * FROM flowers;''').fetchall()

    form = FilterForm()
    if form.validate_on_submit:
        choice = form.filter.data
        if choice == 'Highest First':

            flowers = db.execute(
                '''SELECT * FROM flowers ORDER BY price DESC;'''
            ).fetchall()
        elif choice == 'Lowest First':
            flowers = db.execute(
                '''SELECT * FROM flowers ORDER BY price ASC'''
            ).fetchall()
    
    return render_template('flowers.html', flowers=flowers)
    



#TODO allow user to filter the default page
#TODO create an administrator that can add or remove
#TODO allow the user to receive emails
#TODO payment page
#TODO