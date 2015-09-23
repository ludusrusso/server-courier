from flask import Flask, render_template, request, redirect, url_for
from flask.ext.wtf import Form
from wtforms import StringField, IntegerField, SelectField, SubmitField, FloatField
from wtforms.validators import Required

from flask_bootstrap import Bootstrap
from flask.ext.sqlalchemy import SQLAlchemy
import os
basedir = os.path.abspath(os.path.dirname(__file__))

from flask.ext.script import Manager 
from flask.ext.migrate import Migrate, MigrateCommand



app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
db = SQLAlchemy(app)
Bootstrap(app)
manager = Manager(app)
migrate = Migrate(app, db)
manager.add_command('db', MigrateCommand)

class RegistrationForm(Form):
    name = StringField('Nome')
    surname = StringField('Cognome')
    mail = StringField('Email')
    goal = SelectField('Dove vuoi andare', choices=[], coerce=int)
    submit = SubmitField('Invia')

class AddGoalForm(Form):
    label = StringField('label')
    x = FloatField('x')
    y = FloatField('y')
    submit = SubmitField('Invia')


class CheckInForm(Form):
    mail = StringField('Email')
    pin = IntegerField('PIN')
    submit = SubmitField('Invia')


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    surname = db.Column(db.String(64))
    goal_id = db.Column(db.Integer, db.ForeignKey('goals.id'))
    email = db.Column(db.String(64), unique=True, index=True)
    pin = db.Column(db.Integer, index=True)

    def __repr__(self):
        return '<User %r>' % self.name


class Goal(db.Model):
    __tablename__ = 'goals'
    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String(64))
    x = db.Column(db.Float)
    y = db.Column(db.Float)
    users = db.relationship('User', backref='goal')

    def __repr__(self):
        return '<User %r>' % self.label


@app.route('/users')
def users():
    return render_template('users.html', users=User.query.all())

@app.route('/goals')
def goals():
    return render_template('goals.html', goals=Goal.query.all())


@app.route('/new_goal', methods=['GET', 'POST'])
def new_goal():
    form = AddGoalForm(request.form)
    if request.method == 'POST' and form.validate():    
        goal = Goal(label=form.label.data, x=form.x.data, y=form.y.data)
        db.session.add(goal)
        return redirect(url_for('.goals'))
    return render_template('register.html', form=form)


@app.route('/new_user', methods=['GET', 'POST'])
def register():
    form = RegistrationForm(request.form)
    form.goal.choices = [(g.id, g.label) for g in Goal.query.all()]
    if request.method == 'POST' and form.validate():    
        name = form.name.data
        surname = form.surname.data
        mail = form.mail.data
        goal_id = form.goal.data
        from random import randint
        pin = randint(1000, 9999) 
        user = User(name=name, surname=surname, email=mail, goal=Goal.query.filter_by(id=goal_id).first(), pin=pin)
        db.session.add(user)
        return redirect(url_for('.users'))
    return render_template('register.html', form=form)


@app.route('/checkin', methods=['GET', 'POST'])
def checkin():
    form = CheckInForm(request.form)
    if request.method == 'POST' and form.validate():
        user = User.query.filter_by(pin = form.pin.data, email=form.mail.data).first_or_404()
        if user is not None:
            return render_template('checkin.html', user=user)
    return render_template('register.html', form=form)

@app.route('/')
def hello_world():
    return 'Hello World!'

if __name__ == '__main__':
    manager.run()
