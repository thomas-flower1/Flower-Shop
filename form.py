from flask_wtf import FlaskForm
from wtforms import SubmitField, PasswordField, StringField, EmailField, SelectField
from wtforms.validators import InputRequired, EqualTo

class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])
    submit = SubmitField('Login')
    
class CreateAccountForm(FlaskForm):
    username = StringField('Username: ', validators=[InputRequired()])
    email = EmailField('Email: ', validators=[InputRequired()])
    password = PasswordField('Password: ', validators=[InputRequired()])
    re_password = PasswordField('Re-enter your password: ', validators=[InputRequired(), EqualTo('password')])
    submit = SubmitField('Submit')

class ResetPasswordForm(FlaskForm):
    email = EmailField('Email', validators=[InputRequired()])
    new_password = PasswordField('Password: ', validators=[InputRequired()])
    re_password = PasswordField('Re-enter your password: ', validators=[InputRequired(), EqualTo('new_password')])
    submit = SubmitField('Continue')

class FilterForm(FlaskForm):
    filter = SelectField('filter', choices=['Recommended','Highest First', 'Lowest First'])
    submit = SubmitField('Search')

class EditTableForm(FlaskForm):
    pass

class AddToBasketForm(FlaskForm):
    addToBasket = SubmitField('Add to basket')

class BasketForm(FlaskForm):
    delete = SubmitField('Delete')
    completePurchase = SubmitField('Complete Purchase')

class AddressForm(FlaskForm):
    pass

class SearchBarForm(FlaskForm):
    search = StringField()
    submit = SubmitField('Search')






