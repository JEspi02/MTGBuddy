from flask_app import app
from flask import render_template, redirect, request, session
from flask_app.models.user import User
from flask_app.models.deck import Deck

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect('/dashboard')

    return render_template('index.html')

@app.route('/user/dashboard')
def dashboard():
    if "user_id" not in session:
        return redirect("/")
    user = User.get_by_id({"id": session["user_id"]})
    print(user.__dict__)  # print out the user object for debugging
    decks = Deck.get_all(session["user_id"])  # Fetch all decks for the current user
    return render_template('dashboard.html', user=user, decks=decks)

@app.route('/match_start')
def match_start():
    return render_template('match_start.html')

@app.route('/user/login')
def login():
    if 'user_id' in session:
        return redirect('/dashboard')

    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login_success():
    user = User.validate_login(request.form)
    if not user:
        return redirect('/user/login')

    session['user_id'] = user.id
    return redirect("/user/dashboard")

@app.route('/register', methods=['POST'])
def register_success():
    if not User.validate_reg(request.form):
        return redirect('/user/login')

    user_id = User.save(request.form)
    session['user_id'] = user_id
    return redirect('/dashboard')

@app.route('/user/logout')
def logout():
    if 'user_id' in session:
        session.pop('user_id')
    return redirect('/user/login')
