from flask_wtf import FlaskForm
from wtforms import SubmitField, PasswordField, StringField, EmailField, SelectField, FloatField, FileField, RadioField, BooleanField
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


class AddToBasketForm(FlaskForm):
    addToBasket = SubmitField('Add to basket')

class BasketForm(FlaskForm):
    delete = SubmitField('Delete')
    completePurchase = SubmitField('Complete Purchase')

class AddressForm(FlaskForm):
    name = StringField('Full name', validators=[InputRequired()])
    address_line_1 = StringField('Address Line 1', validators=[InputRequired()])
    address_line_2 = StringField('Address Line 2', validators=[InputRequired()])
    town = StringField('Town', validators=[InputRequired()])
    county = StringField('County', validators=[InputRequired()])
    eircode = StringField('Eircode',validators=[InputRequired()])
    save_address = BooleanField('Save address?')
    submit = SubmitField('Add Address')

    

class SearchBarForm(FlaskForm):
    search = StringField()
    submit = SubmitField('Search')


# ADMIN FORM
class ChangePriceForm(FlaskForm):
    flower_name = StringField('Enter the name of the Flower you wish to edit')
    new_price = FloatField('Enter new price')
    submit = SubmitField('Submit Changes')

class NewEntryForm(FlaskForm):
    flower_name = StringField('Enter flower name')
    price = FloatField('Enter a price')
    photo = FileField()
    submit = SubmitField('Brh')






