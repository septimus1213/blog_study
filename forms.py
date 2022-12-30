from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, TextAreaField
from wtforms.validators import DataRequired, URL, Email
from flask_ckeditor import CKEditor, CKEditorField

# ---- WTForms ------------------- #

class CreatePostForm(FlaskForm):
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    author = StringField("Your Name", validators=[DataRequired()])
    img_url = StringField("Blog Image URL", validators=[DataRequired(), URL()])
    body = CKEditorField("Blog Content", validators=[DataRequired()])
    submit = SubmitField("Submit Post")

class LoginForm(FlaskForm):
    email = StringField(label="Email",validators=[DataRequired(),Email()])
    password = PasswordField(label="Password",validators=[DataRequired()])
    submit = SubmitField(label="Login")

class RegisterForm(FlaskForm):
    email = StringField(label="Email",validators=[DataRequired(),Email()])
    name = StringField(label="Name",validators=[DataRequired()])
    password = PasswordField(label="Password",validators=[DataRequired(),])
    submit = SubmitField(label="Register")

class CommentForm(FlaskForm):
    comment = TextAreaField(label="Comment:",validators=[DataRequired()])
    submit = SubmitField(label="Submit comment")

# ------------------------------- #