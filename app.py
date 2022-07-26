from flask import Flask, render_template, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db, db, User, Feedback
from forms import AddUserForm, LoginUserForm, FeedbackForm
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///registration_db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = "abc123"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False


connect_db(app)

toolbar = DebugToolbarExtension(app)

@app.route('/')
def homepage():
    """Redirects to the register user page"""
    return redirect('/register')

@app.route('/register', methods=["GET", "POST"])
def register_user():
    """Shows the form to register a new user and on a POST route handles the form to register a new user."""

    form = AddUserForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data

        new_user = User.register(username=username, password=password, email=email, first_name=first_name, last_name=last_name)
        # print('************************************')
        # print(new_user)
        db.session.add(new_user)
        try:
            db.session.commit()
        except IntegrityError:
            form.username.errors.append('Username taken, please pick another')
            return render_template('register.html', form=form)
        session['user_id'] = new_user.username
        flash(f"New user account, {username} created!")

        return redirect('/secret')

    else:
        return render_template("register.html", form=form)
    

@app.route('/login', methods=['GET', 'POST'])
def login_user():
    """Shows form to login user and handles login form on a POST route"""
    form = LoginUserForm()

    if form.validate_on_submit():
        username=form.username.data
        password=form.password.data

        user = User.authenticate(username, password)

        if user:
            flash(f"Welcome back, {user.username}")
            session['user_id'] = user.username
            return redirect('/secret')
        else:
            form.username.errors=['Invalid username/password']

    return render_template('login.html', form=form)

@app.route('/secret')
def secret_route():
    """Secret!!!"""
    if "user_id" not in session:
        flash("Please login first!")
        return redirect('/login')

    return render_template('secret.html')

@app.route('/logout')
def logout_user():
    """logs a user out"""
    session.pop('user_id')
    flash("You have been logged out!")

    return redirect('/')

@app.route('/users/<username>')
def user_info(username):
    """Shows user information and feedback"""
    if 'user_id' not in session:
        flash("please login first!")
        return redirect('/login')
    
    user = User.query.get_or_404(username)
    if user.username == session['user_id']:
        fb = Feedback.query.filter_by(username=user.username).all()
        return render_template('user_details.html', user=user, fb=fb)
    else:
        return redirect('/secret')
    
@app.route('/users/<username>/delete')
def delete_user(username):
    """Deletes a user's account"""
    if 'user_id' not in session:
        flash("please login first!")
        return redirect('/login')
    
    if username == session['user_id']:
        user = User.query.get(username)
        db.session.delete(user)
        db.session.commit()
        session.pop('user_id')
        flash("Account deleted!")
        return redirect('/')
    else:
        flash("You can't delete an account that isn't yours!")
        return redirect('/secret')

@app.route('/users/<username>/feedback/add', methods=["GET", "POST"])
def add_feedback(username):
    """Shows the form to add feedback and handles the form on a POST request"""
    if 'user_id' not in session:
        flash("please login first!")
        return redirect('/login')
    
    if username == session['user_id']:
        form = FeedbackForm()

        if form.validate_on_submit():
            title=form.title.data
            content=form.content.data
            new_feedback = Feedback(title=title, content=content, username=username)
            db.session.add(new_feedback)
            db.session.commit()
            return redirect(f'/users/{username}')
        else:
            return render_template('add_feedback.html', form=form)
    else:
        flash("You can't post feedback as someone else!")
        return redirect(f'/secret')

@app.route("/feedback/<feedback_id>/update", methods=["GET", "POST"])
def edit_feedback(feedback_id):
    """Shows a form to edit feedback and on a post request handles the form"""
    if 'user_id' not in session:
        flash("please login first!")
        return redirect('/login')
    
    feedback = Feedback.query.get_or_404(feedback_id)
    
    if feedback.username == session['user_id']:
        form = FeedbackForm()

        if form.validate_on_submit():
            feedback.title = form.title.data
            feedback.content=form.content.data
            feedback.username=feedback.username
            db.session.add(feedback)
            db.session.commit()

            return redirect(f'/users/{feedback.username}')
        else:
            return render_template('edit_feedback.html', form=form)
    else:
        flash("You can't edit someone else's feedback!  thats rude.")
        return redirect(f'/secret')

@app.route('/feedback/<feedback_id>/delete')
def delete_feedback(feedback_id):
    """deletes a piece of feedback"""
    if 'user_id' not in session:
        flash("please login first!")
        return redirect('/login')
    
    feedback = Feedback.query.get_or_404(feedback_id)
    
    if feedback.username == session['user_id']:
        db.session.delete(feedback)
        db.session.commit()
        return redirect(f'/users/{feedback.username}')
    else:
        flash("You can't delete someone else's feedback!")
        return redirect(f'/secret')