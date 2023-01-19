import sqlite3
import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user

# The "blog_post" table column order.
key_lst = ["id","title","date","body","author","author_id","img_url","subtitle"]


# ---- CONNECT TO DB ------------- #
def GetPosts():
    db = sqlite3.connect('blog_database.db')
    cursor = db.cursor()
    all_posts = []
    for post in cursor.execute("""SELECT * FROM blog_posts"""):
        lst_post = list(post)
        all_posts.append(dict(zip(key_lst,lst_post)))
    return all_posts[::-1]

def SubmitPost(title,subtitle,author,body,img_url):
    date =datetime.datetime.now()
    date_string = str(date.year)+" "+str(date.strftime("%B"))+" "+str(date.day)
    db =sqlite3.connect('blog_database.db')
    cursor = db.cursor()

    cursor.execute("""INSERT INTO blog_posts VALUES(NULL,?,?,?,?,?,?,?)""", (title,date_string,body,author,current_user.id,img_url,subtitle))
    db.commit()

def EditPost(id,title,subtitle,author,body,img_url):
    date =datetime.datetime.now()
    date_string = str(date.year)+" "+str(date.strftime("%B"))+" "+str(date.day)
    db =sqlite3.connect('blog_database.db')
    cursor = db.cursor()

    cursor.execute("""UPDATE blog_posts SET title=?, date=?, subtitle=?, author=?, author_id=?, body=?, img_url=? WHERE id=?;""",
    (title,date_string,subtitle,author,current_user.id,body,img_url,id))
    db.commit()

def DeletePost(id):
    print(f"\n Hi Mom \n")
    db = sqlite3.connect('blog_database.db')
    cursor = db.cursor()
    cursor.execute("""DELETE FROM blog_posts WHERE id=?""",(str(id)))
    db.commit()

def RegisterUser(email,password,name):
    db = sqlite3.connect("blog_database.db")
    cursor = db.cursor()
    try:
        cursor.execute("""INSERT INTO blog_users VALUES(NULL,?,?,?)""",(email,password,name))
        db.commit()
        return True
    except:
        return False

def DoesUserExist(email):
    db = sqlite3.connect("blog_database.db")
    cursor = db.cursor()
    cursor.execute("""SELECT * FROM blog_users WHERE email=?;""",(email,))
    if cursor.fetchone() == None:
        return False
    else:
        return True

def GetUser(email,password,load_user_func):
    db = sqlite3.connect("blog_database.db")
    cursor = db.cursor()
    cursor.execute("""SELECT * FROM blog_users WHERE email=?;""",(email,))
    try:
        user_lst = list(cursor.fetchone())
        Us = load_user_func(user_lst[0])
    except TypeError:
        return False
    if email == Us.email and check_password_hash(pwhash=Us.password,password=password):
        login_user(Us)
        return True
    else:
        return False

def AddComment(post_id,text):
    db = sqlite3.connect("blog_database.db")
    cursor = db.cursor()
    cursor.execute("""INSERT INTO comments VALUES(NULL,?,?,?,?)""",(current_user.id,current_user.name,text,post_id))
    db.commit()

def GetCommentsByPostID(post_id):
    db = sqlite3.connect("blog_database.db")
    cursor = db.cursor()
    cursor.execute("SELECT * FROM comments WHERE post_id=?;",(post_id,))
    return list(cursor.fetchall())
# ------------------------------- #