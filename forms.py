from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, FloatField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, Length, NumberRange, Optional

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    is_seller = BooleanField('Register as Seller')
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class ProductForm(FlaskForm):
    name = StringField('Product Name', validators=[DataRequired(), Length(max=100)])
    description = StringField('Short Description', validators=[DataRequired(), Length(max=200)])
    details = TextAreaField('Detailed Description', validators=[DataRequired()])
    price = FloatField('Price', validators=[DataRequired(), NumberRange(min=0.01)])
    category_id = SelectField('Category', validators=[DataRequired()])
    submit = SubmitField('Add Product')

class CheckoutForm(FlaskForm):
    address = StringField('Address', validators=[DataRequired()])
    city = StringField('City', validators=[DataRequired()])
    postal_code = StringField('Postal Code', validators=[DataRequired()])
    country = StringField('Country', validators=[DataRequired()])
    card_number = StringField('Card Number', validators=[DataRequired(), Length(min=16, max=16)])
    exp_month = StringField('Expiration Month', validators=[DataRequired(), Length(min=2, max=2)])
    exp_year = StringField('Expiration Year', validators=[DataRequired(), Length(min=2, max=2)])
    cvv = StringField('CVV', validators=[DataRequired(), Length(min=3, max=3)])
    submit = SubmitField('Complete Purchase')

class CategoryForm(FlaskForm):
    name = StringField('Category Name', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    submit = SubmitField('Add Category')

class SearchForm(FlaskForm):
    query = StringField('Search', validators=[DataRequired()])
    submit = SubmitField('Search')
