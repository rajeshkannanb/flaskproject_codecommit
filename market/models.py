from market import db
from market import bcrypt
from market import login_manager
from flask_login import UserMixin

"""
Steps to create db entries:
#1 Go to python terminal, execute the following steps as it is to create one entry in db.
#2 from main import db
#3 db.create_all()  // One time activity. It will create a new db and it will be added in project. (main.db)
#4 from main import Item
#5 item1 = Item(name="Laptop", price=600, barcode="435672376513", description="desc_laptop")
#6 db.session.add(item1)
#7 db.session.commit()
#8 Item.query.all()

Steps to link entries between two tables.
#1 Create an user
user2 = User(username='varshini', email_address='varshini@mywebsite.com', password_hash='123456')
#2 Add user to db
db.session.add(user2)
db.session.commit()

#3 Create an item
item2 = Item(name='Laptop Lenova', price=1000, barcode='758957689851', description='Laptop Lenova')
#4 Add item to db
db.session.add(item2)
db.session.commit()

#5. Pick the item from Item table
i2 = Item.query.filter_by(name='Laptop Lenova').first()
#6  Assign the owner from user table
i2.owner = User.query.filter_by(name='varshini').first().id
#7 Update db
db.session.add(i2)
db.session.commit()

#8 Verify the owner ship
u2 = User.query.filter_by(username='varshini').first()
u2.items
"""


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(length=30), nullable=False, unique=True)
    email_address = db.Column(db.String(length=30), nullable=False, unique=True)
    password_hash = db.Column(db.String(length=60), nullable=False)
    budget = db.Column(db.Integer(), nullable=False, default=1000)
    items = db.relationship('Item', backref='owned_user', lazy=True)

    def __repr__(self):
        return f'User {self.username}'

    @property
    def prettier_budget(self):
        if len(str(self.budget)) > 4:
            return f'{str(self.budget)[:-3]},{str(self.budget)[-3:]}$'
        else:
            return f'{self.budget}$'

    @property
    def password(self):
        return self.password

    @password.setter
    def password(self, plain_text_password):
        self.password_hash = bcrypt.generate_password_hash(plain_text_password).decode('utf-8')

    def check_password_correction(self, attempted_password):
        return bcrypt.check_password_hash(self.password_hash, attempted_password)

    def can_purchase(self, item_object):
        return self.budget >= item_object.price

    def can_sell(self, item_object):
        return item_object in self.items

class Item(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(length=30), nullable=False, unique=True)
    price = db.Column(db.Integer(), nullable=False)
    barcode = db.Column(db.String(length=12), nullable=False, unique=True)
    description = db.Column(db.String(length=1024), nullable=False, unique=True)
    owner = db.Column(db.Integer(), db.ForeignKey('user.id'))

    def __repr__(self):
        return f'Item {self.name}'

    def buy(self, user_obj):
        self.owner = user_obj.id
        user_obj.budget -= self.price
        db.session.commit()

    def sell(self, user_obj):
        self.owner = None
        user_obj.budget += self.price
        db.session.commit()
