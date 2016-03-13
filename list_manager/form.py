from flask.ext.wtf import Form
from wtforms import TextField, SubmitField, PasswordField, validators, ValidationError

class SignUpForm(Form):
    name = TextField("Username",[validators.Required("Please enter your name")])
    email = TextField("Email", [validators.Required("Please enter your email"), validators.Email("Please enter the email")])
    password = PasswordField("Password",[validators.Required("Please enter the password")])
    submit = SubmitField("Signup")

class LoginForm(Form):
    email = TextField("Email", [validators.Required("Please enter your email"), validators.Email("Please enter the email")])
    password = PasswordField("Password", [validators.Required("Please enter the password")])
    submit = SubmitField("Login")
