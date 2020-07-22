from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
# from app import login

db = SQLAlchemy()


#for user details
class FoodUser(UserMixin, db.Model):
    __tablename__ = 'fooduser'

    user_id = db.Column(db.String(), primary_key=True)
    name = db.Column(db.String(),nullable=False)
    password = db.Column(db.String(),nullable=False)
    email = db.Column(db.String(),nullable=False)
    age = db.Column(db.Integer,nullable=False)
    weight = db.Column(db.Integer,nullable=False)
    gender = db.Column(db.String,nullable=False)
    height = db.Column(db.Integer,nullable=False)
    activity = db.Column(db.String(), nullable=False)

    def get_id(self):
           return (self.user_id)

    food_entries = db.relationship('FoodEntry', backref='FoodUser', lazy=True)

    def __init__(self, user_id, name, password, email, age, weight, gender, height, activity):
        self.user_id = user_id
        self.name = name
        self.password = password
        self.email = email
        self.age = age
        self.weight = weight
        self.gender = gender
        self.height = height
        self.activity = activity


#list of attributes
class Attributes(db.Model):
    __tablename__ = 'attr'

    attr_id = db.Column(db.String(), primary_key=True)

    attr_entries = db.relationship('AttrEntry', backref='Attributes', lazy=True)

    def __init__(self, attr_id):
        self.attr_id = attr_id

#list of Ingredients
class Ingredients(db.Model):
    __tablename__ = 'ingr'

    ingr_id = db.Column(db.String(), primary_key=True)

    ingr_entries = db.relationship('IngrEntry', backref='Ingredients', lazy=True)

    def __init__(self, ing_id):
        self.ingr_id = ing_id


#list of Nutrients
class Nutrients(db.Model):
    __tablename__ = 'nut'

    nut_id = db.Column(db.String(), primary_key=True)

    nut_entries = db.relationship('NutEntry', backref='Nutrients', lazy=True)

    def __init__(self, nut_id):
        self.nut_id = nut_id

# list of food items
class FoodItems(db.Model):
    __tablename__ = 'food_item'

    food_item_id = db.Column(db.String(), primary_key=True)
    calorie = db.Column(db.Integer,nullable=False)
    actual_label = db.Column(db.String)

    food_entries = db.relationship('FoodEntry', backref='FoodItems', lazy=True)


    def __init__(self, food_item_id, calorie, actual_label):
        self.food_item_id = food_item_id
        self.calorie = calorie
        self.actual_label = actual_label

#  list of food entries
class FoodEntry(db.Model):
    __tablename__ = 'food_entry'

    food_entry_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(), db.ForeignKey("fooduser.user_id"),nullable=False)
    food_item_id = db.Column(db.String(), db.ForeignKey("food_item.food_item_id"),nullable=False)
    image = db.Column(db.String(),nullable=False)
    date_time = db.Column(db.DateTime,nullable=False)

    ingr_entries = db.relationship('IngrEntry',backref='FoodEntry',lazy=True)
    attr_entries = db.relationship('AttrEntry',backref='FoodEntry',lazy=True)
    nut_entries = db.relationship('NutEntry',backref='FoodEntry',lazy=True)


    def __init__(self,food_entry_id, user_id, food_item_id, image, date_time):
        self.food_entry_id = food_entry_id
        self.user_id = user_id
        self.food_item_id = food_item_id
        self.image = image
        self.date_time = date_time


#list of Ingredients entries
class IngrEntry(db.Model):
    __tablename__ = 'ingr_entry'

    ingr_entry_id =db.Column(db.Integer, primary_key=True)
    food_entry_id = db.Column(db.Integer, db.ForeignKey('food_entry.food_entry_id'))
    ingr_id = db.Column(db.String(), db.ForeignKey("ingr.ingr_id"), nullable=False)
    ingr_value = db.Column(db.Float,nullable=False)


    def __init__(self,ingr_entry_id, food_entry_id, ingr_id, ingr_value):
        self.ingr_entry_id = ingr_entry_id
        self.food_entry_id = food_entry_id
        self.ingr_id = ingr_id
        self.ingr_value = ingr_value


#list of Attributes entries
class AttrEntry(db.Model):
    __tablename__ = 'attr_entry'

    attr_entry_id =db.Column(db.Integer, primary_key=True)
    food_entry_id = db.Column(db.Integer, db.ForeignKey('food_entry.food_entry_id'))
    attr_id = db.Column(db.String(), db.ForeignKey("attr.attr_id"), nullable=False)
    attr_value = db.Column(db.Integer,nullable=False)


    def __init__(self,attr_entry_id, food_entry_id, attr_id, attr_value):
        self.attr_entry_id = attr_entry_id
        self.food_entry_id = food_entry_id
        self.attr_id = attr_id
        self.attr_value = attr_value


#list of Nutrients entries
class NutEntry(db.Model):
    __tablename__ = 'nut_entry'

    nut_entry_id =db.Column(db.Integer, primary_key=True)
    food_entry_id = db.Column(db.Integer, db.ForeignKey('food_entry.food_entry_id'))
    nut_id = db.Column(db.String(), db.ForeignKey("nut.nut_id"),nullable=False)
    nut_value = db.Column(db.Integer,nullable=False)


    def __init__(self,nut_entry_id, food_entry_id, nut_id, nut_value):
        self.nut_entry_id = nut_entry_id
        self.food_entry_id = food_entry_id
        self.nut_id = nut_id
        self.nut_value = nut_value
