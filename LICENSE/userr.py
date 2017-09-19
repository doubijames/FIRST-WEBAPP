from ormm import Model,StringField,IntegerField

class User(Model):
    __table__ = 'users'

    id = IntegerField(primary_key=True)
    name = StringField()
    user = User(id=123,name = 'Micheal')
    user.insert()
    user.User.findAll()
