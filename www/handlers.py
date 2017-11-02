

import re, time, json, logging, hashlib, base64, asyncio,apis

from coroweb import get, post

from models import User, Comment, Blog, next_id

from aiohttp import web

from config import configs

import markdown2

COOKIE_NAME = 'awesession'
_CONKIE_KEY = configs.session.secret

_RE_EMAIL = re.compile(r'^[a-z0-9\-\_\.]+\@[a-z0-9]+(\.[a-z0-9\-\_]+){1,4}$')
_RE_SHA1 = re.compile(r'^[a-f0-9]{40}$')

def user2cookie(user,max_age):
    '''
    为用户生成COOKIE ID-expires-sha1
    '''
    #过期时间是创建时间+存活时间
    expires = str(int(time.time() + max_age))
    s= '%s-%s-%s-%s' %(user.id,user.passwd,expires,_CONKIE_KEY)
    # SHA1是一种单向算法，可以通过原始字符串计算出SHA1结果，但无法通过SHA1结果反推出原始字符串。
    L = [user.id,expires,hashlib.sha1(s.encode('utf-8')).hexdigest()]
    return '-'.join(L)

async def cookie2user(cookie_str):
    '''
    如果COOCIE有效 解析COOKIE并加载用户
    '''
    if not cookie_str:
        return None
    try:
        L = cookie_str.split('-')
        if len(L) != 3:
            return None
        uid,expires,sha1 = L
        if int(expires)< time.time():
            return None
        user = await User.find(uid)
        if user is None:
            return None
        s = '%s-%s-%s-%s' %(uid,user.passwd,expires,_CONKIE_KEY)
        if sha1 != hashlib.sha1(s.encode('utf-8')).hexdigest():
            logging.info('invalid sha1')
            return None
        user.passwd = '*******'
        return user
    except Exception as e:
        logging.exception(e)
        return None

@get('/')
async def index(request):
    summary='Lorem ipsum dolor sit amet,consectetur adipisicing elit,sed do eiusmod tempor incididunt ut labore et dolore magna aliqua'
    blogs=[
        Blog(id='1',name='Test blog',summary=summary,created_at=time.time()-120),
        Blog(id='2', name='something new', summary=summary, created_at=time.time() - 3600),
        Blog(id='3', name='Learn swift', summary=summary, created_at=time.time() - 7200),
    ]
    return {
        '__template__':'blogs.html',
        'blogs':blogs
    }

@get('/register')
def register():
    return {'__template__':'register.html'}

@post('/api/users')
async def api_register_user(*,email,name,passwd):
    if not name or not name.strip():
        raise APIValueError('name')
    if not email or not _RE_EMAIL.match(email):
        raise APIValueError('email')
    if not passwd or not _RE_SHA1.match(passwd):
        raise APIValueError('passwd')
    users = await User.findAll('email=?',[email])
    if len(users) > 0 :
        raise APIError('register:failed', 'email', 'Email is already in use.')
    uid = next_id()
    sha1_passwd = '%s:%s'% (uid,passwd)
    user = User(id=uid, name=name.strip(), email=email, passwd=hashlib.sha1(sha1_passwd.encode('utf-8')).hexdigest(),image='http://www.gravatar.com/avatar/%s?d=mm&s=120' % hashlib.md5(email.encode('utf-8')).hexdigest())
    await user.save()
    # 制造访问coocie
    r = web.Response()
    r.set_cookie(COOKIE_NAME, user2cookie(user, 86400), max_age=86400, httponly=True)
    user.passwd = '******'
    r.content_type = 'application/json'
    r.body = json.dumps(user, ensure_ascii=False).encode('utf-8')
    return r
    await user.save()

@get('/signin')
async def signin():
    return {'__template__':'signin.html'}


@post('/api/authenticate')
async def authenticate(*,email,passwd):
    if not email:
        raise APIValueError('email','Invalid email')
    if not passwd:
        raise APIValueError('passwd','Invalid passwd')
    users = await User.findAll('email=?' ,[email])
    if len(users)==0:
        raise APIValueError('email','email not exist')
    user = users[0]
    #检查密码
    sha1 = hashlib.sha1()
    sha1.update(user.id.encode('utf-8'))
    sha1.update(b':')
    sha1.update(passwd.encode('utf-8'))
    if user.passwd != sha1.hexdigest():
        raise APIValueError('passwd','Invalid passwd')
    #检查OK,建立COOCIE发送给客户端
    r = web.Response()
    r.set_cookie(COOKIE_NAME,user2cookie(user,86400),max_age=86400,httponly=True)
    user.passwd = '*******'
    r.content_type = 'application/json'
    r.body = json.dumps(user,ensure_ascii=False).encode('utf-8')
    return r

@get('/signout')
def signout(request):
    referer = request.headers.get('Referer')
    r = web.HTTPFound(referer or '/')
    r.set_cookie(COOKIE_NAME,'-deleted-',max_age=0,httponly=True)
    logging.info('user signed out.')
    return r



