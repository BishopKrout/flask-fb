from flask import Flask, render_template, redirect, url_for, flash
from flask_login import LoginManager, login_user, current_user, login_required, logout_user
from models import db, User, Feedback
from forms import RegistrationForm, LoginForm, FeedbackForm, DeleteUserForm, DeleteFeedbackForm

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql:///feedback_app"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = "shhhhh"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

if __name__ == '__main__':
    app.run(debug=True)


@app.route('/')
def home():
    return redirect(url_for('register'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        
        # Add your password hashing logic here (e.g., using bcrypt)
        
        user = User(username=username, password=password, email=email, first_name=first_name, last_name=last_name)
        db.session.add(user)
        db.session.commit()

        login_user(user)
        return redirect(url_for('user_profile', username=user.username))

    return render_template('users/register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        # Add your password verification logic here (e.g., using bcrypt)
        
        if user and user.password == form.password.data:
            login_user(user)
            return redirect(url_for('secret'))
        else:
            flash('Invalid username or password.', 'danger')

    login_user(user)
    return redirect(url_for('user_profile', username=user.username))

@app.route('/users/<username>')
@login_required
def user_profile(username):
    user = User.query.filter_by(username=username).first()

    if user and current_user.username == username:
        return render_template('user_profile.html', user=user)
    else:
        flash("You don't have permission to access this profile.", 'danger')
        return redirect(url_for('home'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/users/<username>')
@login_required
def user_profile(username):
    user = User.query.filter_by(username=username).first()
    delete_user_form = DeleteUserForm()

    if user and current_user.username == username:
        feedbacks = Feedback.query.filter_by(username=username).all()
        return render_template('user_profile.html', user=user, feedbacks=feedbacks, delete_user_form=delete_user_form)
    else:
        flash("You don't have permission to access this profile.", 'danger')
        return redirect(url_for('home'))

@app.route('/users/<username>/delete', methods=['POST'])
@login_required
def delete_user(username):
    user = User.query.filter_by(username=username).first()

    if user and current_user.username == username:
        Feedback.query.filter_by(username=username).delete()
        db.session.delete(user)
        db.session.commit()
        logout_user()
        return redirect(url_for('home'))
    else:
        flash("You don't have permission to delete this account.", 'danger')
        return redirect(url_for('home'))

@app.route('/users/<username>/feedback/add', methods=['GET', 'POST'])
@login_required
def add_feedback(username):
    if current_user.username != username:
        flash("You don't have permission to add feedback to this account.", 'danger')
        return redirect(url_for('home'))

    form = FeedbackForm()

    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data
        feedback = Feedback(title=title, content=content, username=username)
        db.session.add(feedback)
        db.session.commit()
        return redirect(url_for('user_profile', username=username))

    return render_template('add_feedback.html', form=form)

@app.route('/feedback/<int:feedback_id>/update', methods=['GET', 'POST'])
@login_required
def update_feedback(feedback_id):
    feedback = Feedback.query.get(feedback_id)

    if not feedback or current_user.username != feedback.username:
        flash("You don't have permission to update this feedback.", 'danger')
        return redirect(url_for('home'))

    form = FeedbackForm(obj=feedback)

    if form.validate_on_submit():
        feedback.title = form.title.data
        feedback.content = form.content.data
        db.session.commit()
        return redirect(url_for('user_profile', username=feedback.username))

    return render_template('update_feedback.html', form=form)

@app.route('/feedback/<int:feedback_id>/delete', methods=['POST'])
@login_required
def delete_feedback(feedback_id):
    feedback = Feedback.query.get(feedback_id)

    if not feedback or current_user.username != feedback.username:
        flash("You don't have permission to delete this feedback.", 'danger')
        return redirect(url_for('home'))

    db.session.delete(feedback)
    db.session.commit()
    return redirect(url_for('user_profile', username=feedback.username))