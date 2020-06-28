from flask import Flask, request, redirect, render_template, session, \
    g, url_for, flash
from functools import wraps
import sqlite3

# Configuration

DATABASE = 'blog.db'
USERNAME = 'admin'
PASSWORD = 'admin'
SECRET_KEY = 'hard_to_guess'

app = Flask(__name__)

# pulls in configuration from ALL CAPS variable

app.config.from_object(__name__)

# function to connect to db
def connect_db():
    return sqlite3.connect(app.config['DATABASE'])

def login_required(test):
    @wraps(test)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return test(*args, **kwargs)
        else:
            flash("You need to login first")
            return redirect(url_for('login'))
    return wrap





# helper -- Routes

@app.route('/', methods=['GET', 'POST'])
def login():
    error = None
    status_code = 200
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME'] \
            or request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid Credentials. Please try again'
            status_code = 401
        else:
            session["logged_in"] = True
            return redirect(url_for('main'))
    return render_template('login.html', error=error), status_code

@app.route('/main')
@login_required
def main():
    g.db = connect_db()
    cursor = g.db.execute('SELECT * FROM posts')
    posts = [dict(title=row[0], post=row[1]) for row in cursor.fetchall()]
    g.db.commit()
    g.db.close()
    return render_template('main.html', posts=posts)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('login'))

@app.route('/add', methods=['POST'])
def add():
    title = request.form['title']
    post = request.form['post']
    if not title or not post:
        flash('you must fill in the required fields')
        return redirect(url_for('main'))
    else:
        g.db = connect_db()
        g.db.execute('INSERT INTO posts (title, post) VALUES(?, ?)', (request.form['title'], request.form['post']))
        g.db.commit()
        g.db.close()
        flash('Entry was successful..!')
        return redirect(url_for('main'))


if __name__ == '__main__':
    app.run(debug=True)