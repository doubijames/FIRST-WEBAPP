import orm,asyncio
from models import User,Blog,Comment

async def test(loop):
    await orm.create_pool(loop,user='root',password='a65900842',db='awesome')
    u = User(name='TEST2', email='1477789425@example.com', passwd='12340', image='about:CNM.com')

    await u.save()

loop = asyncio.get_event_loop()
loop.run_until_complete(test(loop))
loop.close()