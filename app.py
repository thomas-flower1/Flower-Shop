from flask import Flask, render_template, url_for, session, redirect, g, request
from form import LoginForm, CreateAccountForm, ResetPasswordForm, FilterForm, AddToBasketForm, BasketForm, SearchBarForm, ChangePriceForm, NewEntryForm, AddressForm
from flask_session import Session
from database import get_db, close_db
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import os
from werkzeug.utils import secure_filename
import re

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

def admin_login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if g.user != 'thomas':
            return redirect(url_for('flowers', next=request.url))
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
    return render_template('create_account.html', form=form)

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
            db.commit()
            return redirect(url_for('login'))
        else:
            form.email.errors.append('Account with this email does not exist')
    #need to send an email to the user so they can reset the password
    return render_template('reset_password.html', form=form)

@app.route('/add_address', methods=['POST', 'GET'])
@login_required
def add_address():
    form = AddressForm()
    db = get_db()
    message = 'Add new address'
    #check if they already have an address
    check_address = db.execute(
        '''SELECT * FROM users AS u JOIN address AS a ON u.user_id = a.user_id WHERE u.username =?;''', (session['username'],)).fetchone()
    if form.validate_on_submit():
            address_line_1 = form.address_line_1.data
            address_line_2 = form.address_line_2.data
            town = form.town.data
            county = form.county.data
            eircode = form.eircode.data
            user = db.execute(
                '''SELECT * FROM users WHERE username =?''', (session['username'],)).fetchone()
            user_id = user['user_id']
            if check_address:
                db.execute(
                    '''UPDATE address SET address_line_1=?, address_line_2=?, town=?, county=?, eircode=? WHERE user_id =?; ''',(address_line_1, address_line_2, town, county, eircode, user_id)
                )
                db.commit()
            else:
                db.execute(
                    '''INSERT INTO address VALUES(?, ?, ?, ?, ?, ?);''', (user_id
                                                                        , address_line_1, address_line_2, town, county, eircode))
                db.commit()
            return redirect(url_for('flowers'))
    return render_template('add_address.html', form=form, message=message)
        

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


#TODO
@app.route('/address', methods=['GET', 'POST'])
def address():
    form = AddressForm()
    db = get_db()
    session['shipping'] = True
    session['address'] = {}
    if form.validate_on_submit():
        save = form.save_address.data
        for key, value in form.data.items():
            session['address'][key] = value
        #we are going to use the user_id to link to the address database
        if session.get('username', None) and save:
            #check if the user already has an address
            check_address = db.execute(
                '''SELECT * FROM users AS u JOIN address AS a ON u.user_id = a.user_id WHERE username =?''', (session['username'],)).fetchone()
            if check_address:
                message = 'Using saved address'
                return redirect('purchase_overview')
                #well we need to get the address
                
            address_line_1 = form.address_line_1
            address_line_2 = form.address_line_2
            town = form.town.data
            county = form.county.data
            eircode = form.eircode.data
            #users logged in get free shipping, £5.99
            session['shipping'] = False
            #getting the primary key
            user = db.execute(
                '''SELECT * FROM users WHERE username =?''', (session['username'],)).fetchone()
            user_id = user['user_id']
            db.execute(
                '''INSERT INTO address VALUES(?, ?, ?, ?, ?, ?);''', (user_id, address_line_1, address_line_2, town, county, eircode))
            db.commit()
        return redirect(url_for('flowers'))
    return render_template('shipping.html', form=form, shipping=session['shipping'])

#TODO
@app.route('/purchase_overview')
def purchase_overview():
    #10% discount
    discount = 0.9
    shipping = 5.99
    #we need to list all the items in the basket, name, price, price with shipping, discount if logged in, addess.
    name = session['address']['name'] or 'Mystery Customer'
    message = 'Hi' + name + '. This is what\'s in your cart'
    if session.get('username'):
        after_shipping = session['amount']
        final_price = session['amount'] * discount
    else:
        after_shipping = session['amount'] + shipping
        final_price = after_shipping
    return render_template('purchase_overview.html', message=message, address=session['address'], before_shipping=session['amount'], 
                           after_shipping=after_shipping, final_price=final_price)


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
@app.route('/account')
@login_required
def account():
    db = get_db()
    username = session['username']
    account_info = db.execute(
        '''SELECT * FROM users WHERE username =?;''', (username,)).fetchone()
    email = account_info['email']
    points = account_info['points']
    return render_template('account.html', username=username, email=email, points=points)
    #have a link to reset password

#TODO create an administrator that can add or remove
@app.route('/admin', methods=['POST','GET'])
def admin():
    db = get_db()
    username = session['username']
    account_info = db.execute(
        '''SELECT * FROM users WHERE username =?;''', (username,)).fetchone()
    email = account_info['email']
    points = account_info['points']
    return render_template('account.html', username=username, email=email, points=points)
    

@app.route('/change_price', methods=['POST', 'GET'])
#@admin_login_required
def change_price():
    form = ChangePriceForm()
    db = get_db()
    current_flower_names = db.execute(
        '''SELECT * FROM flowers''').fetchall()
    #getting the current flower names
    flowers = [flower_dict['flower_name'] for flower_dict in current_flower_names]
    print(flowers)
    if form.validate_on_submit():
        flower_name = form.flower_name.data
        new_price = float(form.new_price.data)
        if flower_name.capitalize() not in flowers:
            form.flower_name.errors.append('Flower not in database. Please Try again')
            print('bruh')
        else:
            print('ok')
            db.execute(
                '''UPDATE flowers SET price=? WHERE flower_name =?;''',(new_price, flower_name,))
            db.commit()
            return redirect(url_for('flowers'))
    return render_template('change_price.html', form=form, current_flower_names=current_flower_names)

def valid_img(img):
    if re.search(r'.+\.(jpg|png)$', img):
        return img
    
def valid_entry(flower):
    db = get_db()
    check = db.execute(
        '''SELECT * FROM flowers WHERE flower_name =?;''', (flower.capitalize(),)).fetchone()
    print(check)
    if check is not None:
        return False
    return True
    
@app.route('/new_entry', methods=['POST', 'GET'])
def new_entry():
    form = NewEntryForm() 
    if form.validate_on_submit():
        file = form.photo.data
        name = form.flower_name.data
        price = form.price.data
        filename = secure_filename(file.filename)
        print(filename)
        if valid_img(filename) and valid_entry(name):
            filename = secure_filename(file.filename)
            try:
                #gets the path then adds static to the end
                path = os.path.join((os.path.dirname(__file__)), 'static', filename)
                file.save(path)
                db = get_db()
                db.execute(
                    ''' INSERT INTO flowers (flower_name, price, img_url) VALUES (?,?,?);''', (name, price, filename))
                db.commit()
            except FileExistsError:
                    form.photo.errors.append('File already exists')
        elif not valid_img(filename):
            form.photo.errors.append('Not a valid file. Extensions must be either PNG or JPG')
        else:
            form.flower_name.errors.append('Flower already exists in database! ')
            return 
    return render_template('new_entry.html', form=form)






    
