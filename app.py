from flask import Flask, render_template, redirect, session, flash
from werkzeug.exceptions import Unauthorized
from models import connect_db, db, User, Feedback
from forms import RegisterForm, LoginForm, FeedbackForm

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

    return redirect('/register')

@app.route("/register", methods=['GET'])
def register_form():
    """New user registration route"""

    form = RegisterForm()  

    return render_template('register.html', form=form)    

@app.route('/register', methods=['POST'])
def post_register_form():
    """New user registration route"""

    form = RegisterForm()  

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

    form = LoginForm()  

    return render_template('login.html', form=form)

@app.route('/login', methods=['POST'])
def post_login_form():
    """User login route"""

    form = LoginForm()  

    if form.validate_on_submit():
        username = form.username.data
        pwd = form.password.data

        user = User.authenticate(username=username, pwd=pwd)

        if user:
            session['username'] = user.username
            return redirect(f'/users/{user.username}')
        else:
            form.username.errors = ["Invalid username/password."]
            return render_template("users/login.html", form=form)

        return redirect('/login')

@app.route('/users/<username>', methods=['GET'])
def users_info(username):
    """Show user info GET route"""
    if "username" not in session or username != session['username']:
        raise Unauthorized()

    if 'username' in session:
        user = User.query.filter_by(username=username).first()
        feedback = Feedback.query.filter_by(username=username)
        return render_template('/user.html', user=user, feedback=feedback)

    return redirect('/login')

@app.route('/users/<username>/feedback/add', methods=['GET'])
def feedback_form(username):
    """Feedback form GET route"""

    if 'username' in session:
        form = FeedbackForm()
        return render_template('/feedback.html', form=form)
    
    return redirect('/login')

@app.route('/users/<username>/feedback/add', methods=['POST'])
def post_feedback_form(username):
    """Feedback form POST route"""

    form = FeedbackForm()

    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data


        if 'username' in session:
            user_feedback = Feedback(title=title, content=content, username=username)
            db.session.add(user_feedback)
            db.session.commit()
            return redirect(f'/users/{username}')
        
        return redirect('/login')

@app.route('/feedback/<int:id>/update', methods=['GET'])  
def update_feedback_form(id):
    """Edit feedback GET route"""

    user_feedback = Feedback.query.get_or_404(id)

    if 'username' in session:
        form = FeedbackForm(obj=user_feedback)
        return render_template('/feedback.html', form=form, edit_mode=True, id=user_feedback.id)
    
    return redirect('/login')

@app.route('/feedback/<int:id>/update', methods=['POST'])  
def post_update_feedback_form(id):
    """Edit feedback POST route"""
    
    form = FeedbackForm()

    if form.validate_on_submit() and 'username' in session:
        title = form.title.data
        content = form.content.data

        user_feedback = Feedback.query.get_or_404(id)

        user_feedback.title = title
        user_feedback.content = content

        db.session.add(user_feedback)
        db.session.commit()

        return redirect(f'/users/{user_feedback.username}')
    
    return redirect(f'/feedback/{id}/update')

@app.route('/feedback/<int:id>/delete', methods=['POST'])
def delete_feedback(id):
    """Delete feedback route"""
    user_feedback = Feedback.query.get_or_404(id)

    if 'username' in session:

        db.session.delete(user_feedback)
        db.session.commit()

        return redirect(f'/users/{user_feedback.username}')

@app.route('/users/<username>/delete', methods=['POST'])
def delete_user(username):
    """Delete user route"""

    if 'username' in session:
        user = User.query.filter_by(username=username).first()
        db.session.delete(user)
        db.session.commit()
        session.pop('username')

    return redirect('/login')

@app.route('/users/logout')
def logout_user():
    """User logout route"""

    if 'username' in session:
        session.pop('username')

    return redirect('/login')
