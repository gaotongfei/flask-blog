基于python flask实现的blog程序.

### 如何使用:

####Linux(ubuntu)

安装pip,和virtualenv

```
sudo apt-get install python-pip
sudo apt-get install virtualenv
```

从仓库中clone程序

```
git clone https://github.com:gaotongfei/flask-blog.git
```

进入目录

```
cd flask-blog
```

创建python虚拟环境

```
virtualenv venv
```

启动虚拟环境

```
source venv/bin/activate
```

安装依赖

```
pip install -r requirements.txt
```

添加管理员账号

```
python app.py shell
```

```
>>>from app import db, User
>>>Admin = User(email=’name@example.com’,username=’name’,password=’your-password’)
# 把email,username,password换成你的.
>>>db.session.add(Admin)
>>>db.session.commit()
```

现在数据库里就有你的用户信息了.

运行程序

```
python app.py runserver
```

点击`登录`,输入你的邮箱和密码

登录后你就可以开始写博客了.

目前支持markdown写作


