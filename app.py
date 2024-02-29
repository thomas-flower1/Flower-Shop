from flask import Flask, render_template, url_for, session, redirect
from form import LoginForm, CreateAccountForm, ResetPasswordForm, FilterForm, AddToBasketForm, BasketForm
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

 
#TODO LOGIN PAGE
#TODO FIX THE PASSWORD ENCRYPTION
@app.route('/login', methods=['POST', 'GET'])
def login():
    session.clear()
    form = LoginForm()
    db = get_db()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        validUser = db.execute(
            '''SELECT * FROM users WHERE email =?;''', (email,)).fetchone() 
        
        if validUser is None:
            return redirect (url_for('create_account'))

        # elif not check_password_hash(validUser['password'], password):
        #     form.password.errors.append('Incorrect Password')
        elif not validUser['password'] == password:
            form.password.errors.append('Incorrect Password')
        else:
            session.clear()
            session['username'] = validUser['username']
            return redirect (url_for('flowers'))
        
        #lead the user to a create account page
    return render_template('login.html', form=form)


#TODO CREATE ACCOUNT
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


#TODO RESET PASSWORD
#TODO SEND AN EMAIL TO RESET
@app.route('/reset_password', methods=['POST', 'GET'])
def reset_password():
    '''Allows the user to send reset password, then redirects to the login page'''
    form = ResetPasswordForm()
    if form.validate_on_submit():
        return redirect(url_for('login'))
    #need to send an email to the user so they can reset the password
    return render_template('reset_password.html', form=form)

#TODO LOGGED IN HAS A SAVE BASKET
@app.route('/add_to_basket/<flower_name>', methods=['POST', 'GET'])
def add_to_basket(flower_name):
    '''
    If the user is logged in it shows their basket
    if not we start a session that keeps track of their basket
    '''
    form = AddToBasketForm()
    db = get_db()
    

    flower = db.execute(
        '''SELECT * FROM flowers WHERE flower_name =?;''',(flower_name,)).fetchone()
    if form.validate_on_submit():
        #if they are logged in 
        if 'user' in session:
            # basket = db.execute(
            #     '''SELECT * FROM basket'''
            # )
            pass
        if 'basket' not in session:
            session['basket'] = {}
            session['amount'] = 0

        if flower_name not in session['basket']:
            session['basket'][flower_name]  = 1
            session['amount'] = int(flower['price'])

        else:
            session['basket'][flower_name] += 1
            session['amount'] += int(flower['price'])

        return redirect(url_for('flowers'))
    
    return render_template('purchase.html', form=form, flower=flower )


#TODO create a basket
@app.route('/basket', methods=['POST', 'GET'])
def basket():
    form = BasketForm()
    if form.validate_on_submit():
        if form.completePurchase():
            return redirect(url_for('purchase_complete'))
        return redirect(url_for('flowers'))
    

    return render_template('basket.html', items=session['basket'], amount=session['amount'], form=form)

#TODO DEFUALT
#TODO ADD FILTER FUNCTIONALITY
@app.route('/', methods=['POST', 'GET'])
def flowers():
    db = get_db()
    flowers = db.execute(
        '''SELECT * FROM flowers;''').fetchall()

    form = FilterForm()
    if form.validate_on_submit():
        #TODO allow user to filter the default page
        choice = form.filter.data
        if choice == 'Highest First':

            flowers = db.execute(
                '''SELECT * FROM flowers ORDER BY price DESC;'''
            ).fetchall()
        elif choice == 'Lowest First':
            flowers = db.execute(
                '''SELECT * FROM flowers ORDER BY price ASC'''
            ).fetchall()
    
    return render_template('flowers.html', form=form, flowers=flowers)

#TODO create an administrator that can add or remove

#TODO allow the user to receive emails

#TODO payment page

#TODO Logout
@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.clear()



#TODO EXTRA allow the user search for items
    
@app.route('/purchase_complete')
def purchase_complete():
    return render_template('purchaseComplete.html')