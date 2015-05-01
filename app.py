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
from flask.ext.login import UserMixin, LoginManager, login_required, login_user, logout_user
from flask.ext.pagedown import PageDown
from werkzeug.security import generate_password_hash, check_password_hash
from markdown import markdown
import logging

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)
try:
    log.info('start reading database')
except:
    _, ex, _ = sys.exc_info()
    log.error(ex.message)

basedir = os.path.abspath(os.path.dirname(__file__))
# 初始化
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') or\
    'mysql://root:123456@127.0.0.1/blog?charset=utf8'
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
pagedown = PageDown(app)


class Content(db.Model):
    __tablename__ = 'contents'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64))
    pub_time = db.Column(db.DateTime, default=db.func.now())
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    category = db.Column(db.String(10))

    def __repr__(self):
        return "<Content %r>" % self.title
    '''
    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p']
        target.body_html = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, strip=True))

        db.event.listen(Content.body, 'set', Content.on_changed_body)
    '''


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
@app.route('/', methods=['GET', 'POST'])
def index():
    contents = Content.query.order_by(Content.pub_time.desc()).all()
    return render_template('index.html', contents=contents)


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


@app.route('/logout.html', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash('你已退出登录')
    return redirect(url_for('index'))


@app.route('/post-article.html', methods=['GET', 'POST'])
@login_required
def post_article():
    title = None
    body = None
    category = None
    form = PostArticle()
    if form.validate_on_submit():
        # title = form.title.data
        # body = form.body.data
        content = Content(title=form.title.data,
                          body=form.body.data,
                          category=form.category.data,
                          body_html=markdown(form.body.data))
        db.session.add(content)
        db.session.commit()
        return redirect(url_for('.index'))
    return render_template('post-article.html', form=form)


@app.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    content = Content.query.get_or_404(id)
    form = PostArticle()
    if form.validate_on_submit():
        content.title = form.title.data
        content.body = form.body.data
        content.body_html = markdown(form.body.data)
        db.session.add(content)
        flash('你已经更新')
        return redirect(url_for('index'))
    form.body.data = content.body
    form.title.data = content.title
    return render_template('post-article.html', form=form)


@app.route('/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete(id):
    content = Content.query.get_or_404(id)
    if content is None:
        flash('文章不存在')
        return redirect(url_for('index'))
    db.session.delete(content)
    db.session.commit()
    flash('已删除该文章')
    return redirect(url_for('index'))

@app.route('/article/<int:id>')
def article(id):
    content = Content.query.get_or_404(id)
    return render_template('article.html', content=content)

if __name__ == '__main__':
    manager.run()
