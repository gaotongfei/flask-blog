# coding=utf8
import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
from flask import Flask, render_template, redirect, request, url_for, flash
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.bootstrap import Bootstrap
from flask.ext.script import Manager
from forms import LoginForm, RegisterForm, PostArticle
from flask.ext.migrate import Migrate, MigrateCommand
from flask.ext.login import UserMixin, LoginManager, login_required, login_user
from werkzeug.security import generate_password_hash, check_password_hash

basedir = os.path.abspath(os.path.dirname(__file__))
# 初始化
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.sqlite'
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SECRET_KEY'] = 'i bet you don not know the key'
db = SQLAlchemy(app)
bootstrap = Bootstrap(app)
manager = Manager(app)
migrate = Migrate(app, db)
manager.add_command('db', MigrateCommand)
login_manager = LoginManager(app)
login_manager.session_protection = 'basic'
login_manager.login_view = 'login'


class Content(db.Model):
    __tablename__ = 'contents'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64))
    pub_time = db.Column(db.DateTime)
    body = db.Column(db.Text)

    def __repr__(self):
        return "<Content %r>" % self.title


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)

    def __repr__(self):
        return "<Role %r>" % self.name


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))

    @property
    def password(self):
        raise AttributeError('密码是不可读取的类型')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# 定义路由
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login.html', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    email = None
    password = None
    remember_me = None
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(request.args.get('next') or url_for('index'))
        else:
            flash('邮箱或者密码不正确')
        #flash('电子邮箱或密码不正确')
    form.email.data = ''
    return render_template('login.html', form=form, email=email, password=password, remember_me=remember_me)


@app.route('/register.html', methods=['GET', 'POST'])
def register():
    email = None
    username = None
    password = None
    form = RegisterForm()
    if form.validate_on_submit():
        email = form.email.data
        username = form.username.data
        password = form.password.data
    return render_template('register.html', form=form,
                           email=email, username=username, password=password)


@app.route('/post-article.html', methods=['GET', 'POST'])
def post_article():
    title = None
    body = None
    node = None
    form = PostArticle()
    if form.validate_on_submit():
        title = form.title.data
        body = form.body.data
        node = form.node.data

    return render_template('post-article.html', form=form, title=title, body=body, node=node)


if __name__ == '__main__':
    manager.run()
