from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# This variable and the for loop below are used to make local DB active for local work, and Heroku's Postgres in production.
ENV = "dev"

if ENV == "dev":
    app.debug = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bookmarks.db'
else:
    app.debug = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://zseqffcyzrnskd:4dc604400fb9a173e66b9c267bdbca05a44193aca0b55ad4a14db3628495bf8a@ec2-54-210-128-153.compute-1.amazonaws.com:5432/d49uvmgku8bqjj'

db = SQLAlchemy(app)

class Bookmark(db.Model):
    __tablename__ = 'bookmark'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    link = db.Column(db.String(300), nullable=False)
    marked_read = db.Column(db.Boolean)

# db.create_all() This line is commented out now, because it's needed only in the first run of the server.

# The index root always collects unread and read bookmarks from DB and brings them to the screen
@app.route("/")
def index():
    unread = Bookmark.query.filter_by(marked_read = False).all()
    read = Bookmark.query.filter_by(marked_read = True).all()
    return render_template("base.html", unread = unread, read = read)

# This root makes a database transaction to ADD a bookmark, and redirects back to index
@app.route("/add", methods=["POST"])
def add():
    bookmark = Bookmark(title=request.form['bookmarktitle'], link=request.form['bookmarklink'], marked_read=False)
    db.session.add(bookmark)
    db.session.commit()
    return redirect(url_for('index'))

# This root makes a database transaction to mark a bookmark as read, and redirects back to index
@app.route("/markread/<id>")
def mark_read(id):
    bookmark = Bookmark.query.filter_by(id=int(id)).first()
    bookmark.marked_read = True
    db.session.commit()
    return redirect(url_for('index'))

# This root makes a database transaction to mark a bookmark as unread, and redirects back to index
@app.route("/markunread/<id>")
def mark_unread(id):
    bookmark = Bookmark.query.filter_by(id=int(id)).first()
    bookmark.marked_read = False
    db.session.commit()
    return redirect(url_for('index'))

# This root makes a database transaction to DELETE a bookmark, and redirects back to index
@app.route("/delete/<id>")
def delete(id):
    bookmark = Bookmark.query.filter_by(id=int(id)).first()
    db.session.delete(bookmark)
    db.session.commit()
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=False)