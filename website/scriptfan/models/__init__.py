#!/usr/bin/env python
#-*-coding:utf-8-*-
from scriptfan.extensions import db
from datetime import datetime

def getUserObject(slug=None, user_id=None):
    user = None
    if not slug and not user_id:
        if 'user' in session:
            user = g.user
    elif slug:
        user = User.query.filter_by(slug=slug).first()
    elif user_id:
        user = User.query.filter_by(id=user_id).first()
    return user

follow_user_post = db.Table('follow_user_post',
            db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
            db.Column('post_id', db.Integer, db.ForeignKey('posts.id'), primary_key=True),
        )

class UserInfo(db.Model):
    """
    用户信息表
    """
    __tablename__ = 'user_info'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    motoo = db.Column(db.String(255))
    introduction = db.Column(db.Text)
    phone = db.Column(db.String(15), unique=True, nullable=True) # 手机号码
    phone_status = db.Column(db.Integer, nullable=True) # 手机可见度: 0-不公开 1-公开 2-向成员公开
    photo = db.Column(db.String(255), nullable=True) # 存一张照片，既然有线下的聚会的，总得认得人才行

    def __init__(self, user_id):
        self.user_id = user_id

    def __repr__(self):
        return "<UserInfo (%s)>" % self.user_id

class User(db.Model):
    """
    用户表
    修改email地址时需要经过验证
    """
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(45), unique=True, nullable=False) # 登陆使用的
    email_status = db.Column(db.Integer, nullable=True) # 邮箱可见度: 0-不公开 1-公开 2-向成员公开
    nickname = db.Column(db.String(45), unique=True, nullable=False) # 昵称, 显示时用的
    password = db.Column(db.String(45), nullable=True) # 密码
    is_email_verified = db.Column(db.Boolean, nullable=False)
    slug = db.Column(db.String(45), nullable=True) # 用户页面
    created_time = db.Column(db.DateTime, nullable=False)
    modified_time = db.Column(db.DateTime, nullable=False)
    last_login_time = db.Column(db.DateTime, default=datetime.now())

    info = db.relationship('UserInfo', uselist=False)

    def __init__(self, nickname, email):
        self.nickname = nickname
        self.email = email
        self.paste_num = 0
        self.created_time = self.modified_time = datetime.now()
        self.is_email_verified = True

    def __repr__(self):
        return "<User (%s|%s)>" % (self.nickname, self.email)

    def set_password(self, password):
        self.password = hashPassword(password)

    @property
    def url(self):
        if self.slug:
            return url_for('userapp.view', slug=self.slug)
        return url_for('userapp.view', user_id=self.id)

    def get_avatar_url(self, size=20):
        return "http://www.gravatar.com/avatar/%s?size=%s&d=%s/static/images/avatar/default.jpg" % (
                hashlib.md5(self.email).hexdigest(),
                size,
                request.url_root)

class UserOpenID(db.Model):
    """
    用户绑定OpenID的表
    一个用户可以对应多个OpenID
    """
    __tablename__ = 'user_openid'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False) # openid关联的用户
    openid_src = db.Column(db.String(45), nullable=False) # openid的提供商，比如 google 
    openid_url = db.Column(db.String(255), nullable=False, unique=True) # 记录的 openid, 不能重复

class Resource(db.Model):
    """
    资源表
    汇集图片、视频、演示文稿等资源, 用于嵌入活动中
    """
    __tablename__ = 'resources'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id')) # 发布者
    filetype = db.Column(db.String(45)) # 类型: video, audio, image, slides, pdf, webpage, ...
    created_time = db.Column(db.DateTime)
    modified_time = db.Column(db.DateTime)


class Activity(db.Model):
    """
    活动表
    每期活动需要一个公告
    """
    __tablename__ = 'activities'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id')) # 发起人
    title = db.Column(db.String(255)) # 活动标题
    content = db.Column(db.Text) # 活动介绍
    slug = db.Column(db.String(255)) # 页面地址
    start_time = db.Column(db.DateTime) # 活动开始时间
    end_time = db.Column(db.DateTime) # 活动结束时间
    created_time = db.Column(db.DateTime)
    modified_time = db.Column(db.DateTime)

    followers = db.relationship(User, secondary=follow_user_post) # 参与者
