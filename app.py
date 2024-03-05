from flask import Flask, render_template, url_for, session, redirect, g, request
from form import LoginForm, CreateAccountForm, ResetPasswordForm, FilterForm, AddToBasketForm, BasketForm, SearchBarForm
from flask_session import Session
from database import get_db, close_db
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

app = Flask(__name__)
app.teardown_appcontext(close_db)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SECRET_KEY'] = 'hello'
app.config['SESSION_PERMANANT'] = False
app.secret_key = 'very-secret'
Session(app)

@app.before_request
def load_logged_in_user():
    g.user = session.get('username', None)


def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if g.user is None:
            return redirect(url_for('login', next=request.url))
        return view(*args, **kwargs)
    return wrapped_view

#HOMEPAGE
#TODO ADD FILTER FUNCTIONALITY
@app.route('/', methods=['POST', 'GET'])
def flowers():
    login = 'login'
    if session.get('login'):
        login = 'logout'
    db = get_db()
    results = db.execute(
        '''SELECT * FROM flowers;''').fetchall()
    filter_form = FilterForm()
    search_form = SearchBarForm()
    if filter_form.validate_on_submit():
        #TODO allow user to filter the default page
        choice = filter_form.filter.data
        if choice == 'Highest First':
            results = db.execute(
                '''SELECT * FROM flowers ORDER BY price DESC;'''
            ).fetchall()
        elif choice == 'Lowest First':
            results = db.execute(
                '''SELECT * FROM flowers ORDER BY price ASC'''
            ).fetchall()
    return render_template('flowers.html', form=filter_form, flowers=results, login=login, search_form=search_form )

#TODO EXTRA allow the user search for items
@app.route('/seach', methods=['POST', 'GET'])
def search():
    login = 'login'
    if session.get('login'):
        login = 'logout'
    search_form = SearchBarForm()
    filter_form = FilterForm()
    db = get_db()
    results = db.execute(
        '''SELECT * FROM flowers;''').fetchall()
    if search_form.validate_on_submit():
        search = search_form.search.data
        results = db.execute(
            '''SELECT * FROM flowers WHERE flower_name LIKE ?;''',('%'+search+'%',)).fetchall()
        print('hi')
    return render_template('flowers.html',form=filter_form, flowers=results, login=login, search_form=search_form)
        

#ACCOUNT AND LOGIN
#TODO LOGIN PAGE
#TODO FIX THE PASSWORD ENCRYPTION
@app.route('/login', methods=['POST', 'GET'])
def login():
    if session.get('username'):
        return redirect(url_for('logout'))
    form = LoginForm()
    db = get_db()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        validUser = db.execute(
            '''SELECT * FROM users WHERE email =?;''', (email,)).fetchone() 
        if not validUser:
            return redirect (url_for('create_account'))
        if not check_password_hash(validUser['password'], password):
            form.password.errors.append('Incorrect Password')
        else:
            session.clear()
            session['username'] = validUser['username']
            session['login'] = True
            return redirect (url_for('flowers'))
    return render_template('login.html', form=form)

#TODO LOGOUT
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('flowers'))

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
                '''INSERT INTO users(username, email, password)
                VALUES (?, ?, ?);''',(username, email, generate_password_hash(password)))
            db.commit()
            session['username'] = username
            print(username)
            return redirect(url_for('flowers'))
        return redirect(url_for('basket'))
    return render_template('account.html', form=form)

#TODO RESET PASSWORD
#TODO SEND AN EMAIL TO RESET
@app.route('/reset_password', methods=['POST', 'GET'])
def reset_password():
    '''Allows the user to send reset password, then redirects to the login page'''
    db = get_db()
    form = ResetPasswordForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.new_password.data
        check_email = db.execute(
            '''SELECT * FROM users WHERE email =?;''', (email,)).fetchone()
        if check_email is not None:
            db.execute(
                '''UPDATE users SET password =?;''', (generate_password_hash(password),))
            db.comit()
            return redirect(url_for('login'))
        else:
            form.email.errors.append('Account with this email does not exist')
    #need to send an email to the user so they can reset the password
    return render_template('reset_password.html', form=form)

#BASKET
#TODO create a basket
@app.route('/basket', methods=['POST', 'GET'])
def basket():
    form = BasketForm()
    if 'basket' not in session:
        session['basket'] = {}
    if 'amount' not in session:
        session['amount'] = 0
    if form.validate_on_submit():
        return redirect(url_for('purchase_complete'))
    return render_template('basket.html', items=session['basket'], amount=session['amount'], form=form)

@app.route('/add_to_basket/<flower_name>', methods=['POST', 'GET'])
def add_to_basket(flower_name):
    form = AddToBasketForm()
    db = get_db()
    flower = db.execute(
        '''SELECT * FROM flowers WHERE flower_name =?;''',(flower_name,)).fetchone()
    if form.validate_on_submit():
        if 'basket' not in session:
            session['basket'] = {}
            session['amount'] = float(flower['price'])
        if flower_name not in session['basket']:
            session['basket'][flower_name]  = 1
            session['amount'] += float(flower['price'])
        else:
            session['basket'][flower_name] += 1
            session['amount'] += float(flower['price'])
        session['amount'] = round((float(session['amount'])), 2)
        return redirect(url_for('flowers'))
    return render_template('purchase.html', form=form, flower=flower )

@app.route('/increase_from_basket/<flower_name>', methods=['POST', 'GET'])
def increase_from_basket(flower_name):
    db = get_db()
    amount_to_add = db.execute(
        '''SELECT * FROM flowers WHERE flower_name =?''', (flower_name,)).fetchone()
    amount = amount_to_add['price']
    session['amount'] += amount
    session['basket'][flower_name] += 1
    session.modified = True
    session['amount'] = round((float(session['amount'])), 2)
    return redirect(url_for('basket'))

@app.route('/decrease_from_basket/<flower_name>', methods=['POST', 'GET'])
def decrease_from_basket(flower_name):
    db = get_db()
    amount_to_remove = db.execute(
        '''SELECT * FROM flowers WHERE flower_name =?''', (flower_name,)).fetchone()
    amount = amount_to_remove['price']
    session['amount'] -= amount
    if session['basket'][flower_name] <= 1:
        del session['basket'][flower_name]
    else:
        session['basket'][flower_name] -= 1
    session.modified = True
    session['amount'] = round((float(session['amount'])), 2)
    return redirect(url_for('basket'))

@app.route('/delete/<flower_name><amount>')
def delete(flower_name, amount):
    db = get_db()
    amount_to_remove = db.execute(
        '''SELECT * FROM flowers WHERE flower_name =?''', (flower_name,)).fetchone()
    print(amount_to_remove)
    amount_to_remove = amount_to_remove['price']
    session['amount'] -= amount_to_remove * float(amount)
    del session['basket'][flower_name]
    session['amount'] = round((float(session['amount'])), 2)
    return redirect(url_for('basket'))

#TODO payment page
@app.route('/pay')
def pay():
    pass

@app.route('/address')
def address():
    pass

@app.route('/purchase_complete')
def purchase_complete():
    #want to keep track of 'points'. £1 = 1 point
    if session.get('username'):
        username = session['username']
        print(session['username'])
        db = get_db()
        current_points = db.execute(
            '''SELECT * FROM users WHERE username =?;''', (username,)).fetchone()
        if current_points['points'] == None:
            current_points = 0
        else:
            current_points = int(current_points['points'])
        updated_points = int(session['amount']) + current_points
        db.execute(
            '''UPDATE users SET points =? ''', (updated_points,)
        )
        db.commit()
    print(updated_points)
    session['amount'] = 0
    session['basket'] = {}
    return render_template('purchaseComplete.html')

#TODO ACCOUNT PAGE
@login_required
@app.route('/account')
def account():
    db = get_db()
    username = session['username']
    account_info = db.execute(
        '''SELECT * FROM users WHERE username =?;''', (username,)).fetchall()
    email = account_info['email']
    points = account_info['points']
    return render_template('account.html', username=username, email=email, points=points)
    #have a link to reset password

#TODO create an administrator that can add or remove
@app.route('/admin', methods=['POST','GET'])
def admin():
    pass

@app.route('/change_price', methods=['POST', 'GET'])
def change_price():
    pass

@app.route('/new_entry')
def new_entry():
    pass
@app.route('/delete_entry')
def delete_entry():
    pass






    
