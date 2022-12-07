from enum import Enum

from flask import Flask, request, flash, url_for, redirect, render_template

# https://pypi.org/project/flask/FLAS-sqlalchemy/
from flask_sqlalchemy import SQLAlchemy

# SQLite
# sqlite3_db = '/Users/display/Library/DBeaverData/workspace6/.metadata/sample-database-sqlite-1/Chinook.db'
# uri: str = f'sqlite:///{sqlite3_db}'
# MySQL
# hostname: str = 'pmourey.mysql.pythonanywhere-services.com'
# uri = f'mysql://pmourey:fifa2022@{hostname}/sample'
# mysql://username:password@server/db

app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = uri
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students2.sqlite3'
app.config['SECRET_KEY'] = "fifa 2022"

db = SQLAlchemy(app)


class Students(db.Model):
    id = db.Column('student_id', db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    city = db.Column(db.String(50))
    addr = db.Column(db.String(200))
    pin = db.Column(db.String(10))

    def __init__(self, name, city, addr, pin):
        self.name = name
        self.city = city
        self.addr = addr
        self.pin = pin


@app.route('/')
def show_all():
    return render_template('show_all.html', students=Students.query.all())


@app.route('/new', methods=['GET', 'POST'])
def new():
    if request.method == 'POST':
        if not request.form['name'] or not request.form['city'] or not request.form['addr']:
            flash('Please enter all the fields', 'error')
        else:
            student = Students(request.form['name'], request.form['city'],
                               request.form['addr'], request.form['pin'])

            db.session.add(student)
            db.session.commit()
            flash('Record was successfully added')
            return redirect(url_for('show_all'))
    return render_template('new.html')


@app.before_request
def create_tables():
    db.create_all()


if __name__ == '__main__':
    # db.create_all()
    app.run(debug=True)
