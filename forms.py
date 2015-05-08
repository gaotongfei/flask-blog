# coding: utf8
from wtforms import StringField, SubmitField, PasswordField, TextAreaField, BooleanField
from wtforms.validators import Required, Email, Length
from flask.ext.wtf import Form
from flask.ext.pagedown.fields import PageDownField


class LoginForm(Form):
    email = StringField('电子邮箱:', validators=[Required(), Length(1, 64), Email()])
    password = PasswordField('密码:', validators=[Required()])
    remember_me = BooleanField('记住我')
    submit = SubmitField('提交')


class RegisterForm(Form):
    email = StringField('电子邮箱:', validators=[Email(), Required()])
    username = StringField('用户名:' ,validators=[Required()])
    password = PasswordField('密码', validators=[Required()])
    submit = SubmitField('提交')


class PostArticle(Form):
    # title = StringField('标题', validators=[Required()])
    # body = TextAreaField('正文', validators=[Required()])
    title = StringField('标题', validators=[Required()])
    body = PageDownField('正文', validators=[Required()])
    abstract = TextAreaField('简介', validators=[Required()])
    category = StringField('分类', validators=[Required()])
    pub_time = StringField('时间')
    submit = SubmitField('发表')
