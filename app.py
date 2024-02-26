from flask import Flask, render_template, url_for, session, redirect
from form import LoginForm
from flask_session import Session
from database import get_db, close_db



app = Flask(__name__)
Session(app)
app.teardown_appcontext(close_db)
app.config['SESSION_TYPE'] = 'filesystem'


#TODO create a login page
@app.route('/login')
def login():
    pass


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