from flask import Flask, render_template, redirect, request, url_for, flash, abort
from flask_bootstrap import Bootstrap
from flask_gravatar import Gravatar
from bs4 import BeautifulSoup
from functools import wraps

from forms import *
from database_manager import *

app = Flask(__name__)
ckeditor = CKEditor(app=app)
app.config['SECRET_KEY'] = 'verysecretkey'
Bootstrap(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# ---- PROFILE PICTURE CLASS ----- #
gravatar = Gravatar(app,
                    size=40,
                    rating='g',
                    default='retro',
                    force_default=False,
                    force_lower=False,
                    use_ssl=False,
                    base_url=None)
# -------------------------------- #


# ---- USER LOADER --------------- #

""" Since we're using sqlite3 we had to create this "User" class,
so our "user_loader" can work as intended.  """
class User(UserMixin):
    def __init__(self, id, email, password, name):
         self.id = id
         self.email = email
         self.password = password
         self.name = name
         self.authenticated = False

    def is_active(self):
        return self.is_active()
    def is_anonymous(self):
        return False
    def is_authenticated(self):
        return self.authenticated
    def is_active(self):
        return True
    def get_id(self):
        return self.id

@login_manager.user_loader
def load_user(id):
   db = sqlite3.connect('blog_database.db')
   cursor = db.cursor()
   cursor.execute("SELECT * FROM blog_users WHERE id = (?)",[id])
   user = cursor.fetchone()
   if user is None:
      return None
   else:
      return User(int(user[0]), user[1], user[2],user[3])

# -------------------------------- #

# ---- ADMIN ONLY DECORATOR ------ #
def admin_only(func):
    @wraps(func)
    def any_func(*args, **kwargs):
        if current_user.id == 1:
            return func(*args, **kwargs)
        else:
            return abort(403)
    return any_func
# -------------------------------- #




@app.route('/')
def get_all_posts():
    posts = GetPosts()
    return render_template("index.html", all_posts=posts)


# --------------------------------- #
"""BeautifulSoup is used on post texts and comments in order to parse the html code from the inputs."""

@app.route("/post/<int:index>", methods=["GET","POST"])
def show_post(index):
    form = CommentForm()
    posts = GetPosts()
    requested_post = None
    for blog_post in posts:
        if blog_post["id"] == index:
            requested_post = blog_post
            comments = GetCommentsByPostID(index)

    if form.validate_on_submit():
        AddComment(post_id=index,text=BeautifulSoup(form.comment.data,"html.parser").text)
        return redirect(url_for("show_post",index=index))
    return render_template("post.html", post=requested_post, form=form, comments=comments)

@app.route("/editpost/<int:post_id>", methods=["GET", "POST"])
@admin_only
def edit_post(post_id):
    header = "Edit Post"
    req_method = "PATCH"
    posts = GetPosts()
    for blog_post in posts:
        if blog_post["id"] == post_id:
            post = blog_post
    form = CreatePostForm(title=post["title"],
                            subtitle=post["subtitle"],
                            img_url=post["img_url"],
                            author=post["author"],
                            body=post["body"])
    if form.validate_on_submit():
        EditPost(id=post_id,
        title=form.title.data,
        subtitle=form.subtitle.data,
        author=form.author.data,
        img_url=form.img_url.data,
        body=BeautifulSoup(form.body.data,"html.parser").text)
        return redirect(url_for('get_all_posts'))
    return render_template('make-post.html', form=form, header=header, req_method=req_method,id=post_id)

@app.route("/new-post", methods=["GET","POST"])
@admin_only
def new_post():
    form = CreatePostForm()
    header = "New Post"
    req_method = "POST"
    if form.validate_on_submit():
        title = form.title.data
        subtitle = form.subtitle.data
        author = form.author.data
        img_url = form.img_url.data
        body = BeautifulSoup(form.body.data,"html.parser").text

        SubmitPost(title=title,subtitle=subtitle,author=author,img_url=img_url,body=body)
        return redirect(url_for('get_all_posts'))
    return render_template('make-post.html', form=form, header=header, req_method=req_method)

# --------------------------------- #

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/delete/<int:id>")
@admin_only
def delete(id):
    DeletePost(id)
    return redirect(url_for('get_all_posts'))

@app.route('/login', methods=["GET","POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('secrets',name=current_user.name))
    form = LoginForm()
    if form.validate_on_submit():
        user_email = form.email.data
        user_pass = form.password.data
        if GetUser(email=user_email,password=user_pass,load_user_func=load_user):
            return redirect(url_for("get_all_posts"))
        else:
            if DoesUserExist(form.email.data):
                flash("Unable to log in. Incorrect password.")
            else:
                flash("The email you enetered is not registered.")
            return redirect(url_for("login"))
    
    return render_template("login.html", form=form)

@app.route("/register", methods=["GET","POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if RegisterUser(email=form.email.data,
            password=generate_password_hash(password=form.password.data,method="pbkdf2:sha256",salt_length=8),
        name=form.name.data):
            return redirect(url_for("login"))
        else:
            flash("The email you entered is already registered.")
            return redirect(url_for("register"))
    return render_template("register.html", form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for("get_all_posts"))

if __name__ == "__main__":
    app.run()