from flask import Flask, render_template, redirect, session, flash
from models import connect_db, db, User
# from forms import RegisterForm, LoginForm

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgres:///login"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = "abc123"

connect_db(app)
db.create_all()

@app.route("/")
def homepage():
    """Show homepage"""

    return render_template("index.html")

@app.route("/register", methods=['GET'])
def register_form():
    """New user registration route"""

    form = RegisterForm()  #will create in forms.py

    return render_template('register_form.html', form=form)    

@app.route('/register', methods=['POST'])
def post_register_form():
    """New user registration route"""

    form = RegisterForm()  #will create in forms.py

    if form.validate_on_submit():
        username = form.username.data
        pwd = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data

        user = User.register(username=username, pwd=pwd, email=email, first_name=first_name, last_name=last_name)

        db.session.add(user)
        db.session.commit()

        session['username'] = user.username
    
    return redirect(f'/users/{user.username}')

@app.route('/login', methods=['GET'])
def login_form():
    """Login registration route"""

    form = LoginForm()  #will create in forms.py

    return render_template('login_form.html', form=form)

@app.route('/login', methods=['POST'])
def post_login_form():
    """User login route"""

    form = LoginForm()  #will create in forms.py

    if form.validate_on_submit():
        username = form.username.data
        pwd = form.password.data

        user = User.authenticate(username=username, pwd=pwd)

        if user:
            session['username'] = user.username
            return redirect(f'/users/{user.username}')
        
        return redirect('/login')

@app.route("/secret")
def secret():
    """Show secret message"""

    return "You made it!"
