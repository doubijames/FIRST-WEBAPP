import orm, asyncio
from models import User, Blog, Comment

async def test(loop):
    await orm.create_pool(loop=loop, user='root', password='a65900842', db='awesome')
    u = User(name='zhen', email='410583828.com', passwd='65900842', image='www.baidu.com')
    await u.save()

loop = asyncio.get_event_loop()
loop.run_until_complete(test(loop))
loop.close()