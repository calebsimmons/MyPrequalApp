from flask_wtf import Form
from wtforms import (StringField, PasswordField, TextAreaField, IntegerField,
                    DecimalField)
from wtforms.validators import (DataRequired, Regexp, ValidationError, Email,
                               Length, EqualTo, NumberRange)
from models import User

def name_exists(form,field):
    if User.select().where(User.username == field.data).exists():
        raise ValidationError("User with that name already exists.")

def email_exists(form,field):
    if User.select().where(User.email == field.data).exists():
        raise ValidationError("User with that email already exists.")

class RegisterForm(Form):
    username = StringField(
        "Username",
        validators=[
            DataRequired(),
            Regexp(
                r'[a-zA-Z0-9_]+$',
                message = ("Username should be one word, letters,"
                           "numbers, and underscores only.")
            ),
            name_exists,
        ]
    )
    email = StringField(
        "Email",
        validators=[
            DataRequired(),
            Email(),
            email_exists
        ]
    )
    password = PasswordField(
        "Password",
        validators=[
            DataRequired(),
            Length(min=6,message="Passwords must be at least 6 characters long."),
            EqualTo('password2',message="Passwords must match.")
        ]
    )
    password2 = PasswordField(
        "Confirm Password",
        validators=[DataRequired()]
    )


class LoginForm(Form):
    email = StringField("Email", validators=[DataRequired(),Email()])
    password = PasswordField("Password", validators=[DataRequired()])

class LetterRequest(Form):
    loan_program = StringField("Loan Program", validators=[DataRequired()])
    sales_price = DecimalField("Sales Price", validators=[DataRequired()])
    down_payment = DecimalField("Down Payment",validators=[DataRequired()])
    rate = DecimalField("Rate", validators=[DataRequired()])

    def validate(self):
        """Overwrites the default validations so that the down_payment can be
        checked against sales_price"""
        #this performs default validations
        if not Form.validate(self):
            return False
        result = True
        seen = set()
        if self.down_payment.data >= self.sales_price.data:
            self.down_payment.errors.append("Down payment must be less than sales price.")
            result = False
        else:
            seen.add(self.down_payment.data)
        return result




