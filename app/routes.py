# Import packages
from app import app
import pickle
from flask import Flask, request , redirect, url_for, render_template
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import numpy as np
import cv2
from flask import flash
import json
import keras.models
from keras.models import model_from_json
import tensorflow as tf
from tensorflow.python.keras.backend import set_session
from tensorflow.python.keras.models import load_model

from googlesearch import search
import bs4 as bs
import requests
import logging
import xml
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

import os
from datetime import datetime
from gensim.models import Word2Vec

from .models import FoodUser, FoodEntry, FoodItems, IngrEntry, AttrEntry, NutEntry
from psycopg2.extensions import register_adapter, AsIs

from flask_login import login_user, current_user, login_required,  logout_user

from datetime import datetime

import matplotlib.pyplot as plt
import cvlib as cv
import numpy as np

def addapt_numpy_float64(numpy_float32):
  return AsIs(numpy_float32)
register_adapter(np.float32, addapt_numpy_float64)

sess = tf.Session()
graph = tf.get_default_graph()

#Load model
set_session(sess)
json_file = open('ml/model.json','r')
loaded_model_json = json_file.read()
json_file.close()
model = model_from_json(loaded_model_json)

#load weights into new model
model.load_weights("ml/model.h5")
print("loaded model successfully")

ingr_attr_model = Word2Vec.load('ml/ingr_attr_model.model')
print("ingr model loaded.")

attr_model = Word2Vec.load('ml/attr.model')
print("attr model loaded.")

nut_model = Word2Vec.load('ml/nut_model.model')
print("nutrient model loaded.")

UPLOAD_FOLDER = 'app/static/uploads/'
ALLOWED_EXTENSIONS = { 'png', 'jpg', 'jpeg'}
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:megha123@localhost/eatiza'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
db = SQLAlchemy(app)
print('db connected!!')

@app.route('/success/<name>')
def success(name):
   return 'welcome %s' % name

@app.route('/index',methods = ['POST', 'GET'])
def index():
    error = None
    if request.method == 'POST':
        if request.form['nm'] != 'chetana' and request.form['pwd'] != 'chetana':
            error = 'Invalid Credentials. Please try again.'
        else:
            return 'login successful'
    return render_template('index.html', error=error)
'''@app.route('/signup',methods = ['POST', 'GET'])
def signup():
    if request.method == 'POST':
       user_id = request.form['User_id']
       name = request.form['Name']
       pwd = request.form['Password']
       email = request.form['Email']
       age = request.form['Age']
       weight = request.form['Weight']
       gender = request.form['Gender']
       height = request.form['Height']

       user_obj = FoodUser.query.filter_by(user_id=user_id).first()
       if user_obj:
          return "userid already exists!!"

       user = FoodUser(user_id=user_id,name=name,password=pwd,email=email,age=age,weight=weight,gender=gender,height=height)
       db.session.add(user)
       db.session.commit()

       #print('inserted!!')
       #print(user_id)
       #print(name)
       #print(pwd)
    return render_template('signup.html')
'''

# to check extensions of files
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



@app.route('/food',methods = ['POST', 'GET'])
def food():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            print ("file Uploaded")

        imgData = request.get_data()
        path=os.path.join(app.config['UPLOAD_FOLDER'],filename)
        print(filename)
        im = cv2.imread(os.path.join(path))  # convert to array
        im = cv2.cvtColor(im,cv2.COLOR_BGR2RGB)
        bbox, label, conf = cv.detect_common_objects(im)
        print(bbox)
        print("opencv module built")

        if bbox != []:
          areas = [w*h for x,y,w,h in bbox]
          i_biggest = np.argmax(areas)
          biggest = bbox[i_biggest]

          start = (biggest[0], biggest[1])
          end = (biggest[2], biggest[3])
          color = (0,255, 0)
          thickness = 2
          im = cv2.rectangle(im, start, end, color, thickness)
          im = cv2.resize(im, (200, 200))  # resize to normalize data size

        data=[]
        data.append(im)
        data=np.array(data)
        data = data.astype('float32')/255

        global sess
        global graph
        with graph.as_default():
            set_session(sess)
            out = model.predict_classes(data)
        print(out)

        food_labels = ['Pizza','Ice-cream','Fried rice','Chicken wings','Samosa']


        user_id = 'chetana24'
        food_item_id = food_labels[out[0]]
        image = path
        dt = datetime.now()
        food_entry_id = food_item_id + str(dt)


        food_entry = FoodEntry(food_entry_id = food_entry_id, user_id = user_id, food_item_id = food_item_id, image = image, date_time = dt)
        db.session.add(food_entry)
        db.session.commit()
        print("food entry inserted!!")

        #search for actual label for nlp model
        food_item_obj = FoodItems.query.filter_by(food_item_id = food_item_id).first()
        # food_entry_obj = FoodEntry.query.filter_by(food_item_id = food_item_id).filter_by(user_id = user_id).all()
        food_ingredients = {}
        food_attributes = {}
        food_nutrients = {}


        if food_item_obj:
            actual_label = food_item_obj.actual_label
            filename=open('ml/list.txt','r')
            ingr=filename.read().split()

            filename=open('ml/attr.txt','r')
            attr=filename.read().split()

            filename=open('ml/nutrients.txt','r')
            nut=filename.read().split()

            for l in ingr:
                # print(l,ingr_attr_model.wv.similarity(actual_label, l))
                food_ingredients.update({l : ingr_attr_model.wv.similarity(actual_label,l)})

                sorted_ingredients= sorted(food_ingredients.items() ,  key=lambda x: x[1], reverse =True)[:8]

            # Iterate over the sorted sequence
            for e in sorted_ingredients :
                ingr_entry_id = food_entry_id + '_' + e[0]
                ingr_entry = IngrEntry(ingr_entry_id = ingr_entry_id,food_entry_id = food_entry_id, ingr_id = e[0], ingr_value = e[1])
                db.session.add(ingr_entry)
                db.session.commit()

            print("ingredients stored!!")

            for l in attr:
                # print(l,ingr_attr_model.wv.similarity(actual_label, l))
                food_attributes.update({l : attr_model.wv.similarity(actual_label,l)})

                sorted_attributes= sorted(food_attributes.items() ,  key=lambda x: x[1], reverse =True)[:5]

            # Iterate over the sorted sequence
            for e in sorted_attributes :
                attr_entry_id = food_entry_id + '_' + e[0]
                attr_entry = AttrEntry(attr_entry_id = attr_entry_id,food_entry_id = food_entry_id, attr_id = e[0], attr_value = e[1])
                db.session.add(attr_entry)
                db.session.commit()

            print("attributes stored!!")

            for l in nut:
                # print(l,ingr_attr_model.wv.similarity(actual_label, l))
                food_nutrients.update({l : nut_model.wv.similarity(actual_label,l)})

                sorted_nutrients= sorted(food_nutrients.items() ,  key=lambda x: x[1], reverse =True)[:5]

            # Iterate over the sorted sequence
            for e in sorted_nutrients :
                nut_entry_id = food_entry_id + '_' + e[0]
                nut_entry = NutEntry(nut_entry_id = nut_entry_id,food_entry_id = food_entry_id, nut_id = e[0], nut_value = e[1])
                db.session.add(nut_entry)
                db.session.commit()

            print("nutrients stored!!")


            # # display_ingr(food_entry_id)
        ingr_data = []
        attr_data = []
        nut_data = []
        ingr_data = IngrEntry.query.filter_by(food_entry_id = food_entry_id).all()
        attr_data = AttrEntry.query.filter_by(food_entry_id = food_entry_id).all()
        nut_data = NutEntry.query.filter_by(food_entry_id = food_entry_id).all()
        return render_template('food.html',img_path=path,  ingr_data=ingr_data, attr_data = attr_data, nut_data = nut_data)

    else:
        return render_template('food.html')


@login_required
@app.route('/dashboard',methods = ['POST', 'GET'])
def dashboard():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            print ("file Uploaded")


        imgData = request.get_data()
        path=os.path.join(app.config['UPLOAD_FOLDER'],filename)
        print(filename)
        x = cv2.imread(os.path.join(path))  # convert to array
        x = cv2.cvtColor(x,cv2.COLOR_BGR2RGB)
        x = cv2.resize(x, (200, 200))  # resize to normalize data size
        print("opencv module built")

        data=[]
        data.append(x)
        data=np.array(data)
        data = data.astype('float32')/255

        global sess
        global graph
        with graph.as_default():
            set_session(sess)
            out = model.predict_classes(data)
        print(out)

        food_labels = ['Pizza','Ice-cream','Fried rice','Chicken wings','Samosa']


        label=""
        user_id = current_user.user_id;
        food_item_id = food_labels[out[0]]
        image = path
        dt = datetime.now()
        food_entry_id = food_item_id + str(dt)

        image_link = os.path.join("static/uploads/",filename)
        food_entry = FoodEntry(food_entry_id = food_entry_id, user_id = user_id, food_item_id = food_item_id, image = image_link, date_time = dt)
        db.session.add(food_entry)
        db.session.commit()
        print("food entry inserted!!")

        #search for actual label for nlp model
        food_item_obj = FoodItems.query.filter_by(food_item_id = food_item_id).first()
        label = food_labels[out[0]]
        calorie = food_item_obj.calorie
        # image_link = os.path.join("static/uploads/",filename)


        food_ingredients = {}
        food_attributes = {}
        food_nutrients = {}


        if food_item_obj:
            actual_label = food_item_obj.actual_label
            filename=open('ml/list.txt','r')
            ingr=filename.read().split()

            filename=open('ml/attr.txt','r')
            attr=filename.read().split()

            filename=open('ml/nutrients.txt','r')
            nut=filename.read().split()

            #Sort ingredients based on similarity of actual_label with ingredient
            for l in ingr:
                # print(l,ingr_attr_model.wv.similarity(actual_label, l))
                food_ingredients.update({l : ingr_attr_model.wv.similarity(actual_label,l)})

                sorted_ingredients= sorted(food_ingredients.items() ,  key=lambda x: x[1], reverse =True)[:8]

            # Iterate over the sorted sequence
            for e in sorted_ingredients :
                ingr_entry_id = food_entry_id + '_' + e[0]
                ingr_entry = IngrEntry(ingr_entry_id = ingr_entry_id,food_entry_id = food_entry_id, ingr_id = e[0], ingr_value = e[1])
                db.session.add(ingr_entry)
                db.session.commit()

            print("ingredients stored!!")

            #Sort attributes based on similarity of actual_label with attribute
            for l in attr:
                # print(l,ingr_attr_model.wv.similarity(actual_label, l))
                food_attributes.update({l : attr_model.wv.similarity(actual_label,l)})

                sorted_attributes= sorted(food_attributes.items() ,  key=lambda x: x[1], reverse =True)[:5]


            # Iterate over the sorted sequence
            for e in sorted_attributes :
                attr_entry_id = food_entry_id + '_' + e[0]
                attr_entry = AttrEntry(attr_entry_id = attr_entry_id,food_entry_id = food_entry_id, attr_id = e[0], attr_value = e[1])
                db.session.add(attr_entry)
                db.session.commit()

            print("attributes stored!!")

            #Sort nutrients based on similarity of actual_label with nutrient
            for l in nut:
                # print(l,ingr_attr_model.wv.similarity(actual_label, l))
                food_nutrients.update({l : nut_model.wv.similarity(actual_label,l)})

                sorted_nutrients= sorted(food_nutrients.items() ,  key=lambda x: x[1], reverse =True)[:5]

            # Iterate over the sorted sequence
            for e in sorted_nutrients :
                nut_entry_id = food_entry_id + '_' + e[0]
                nut_entry = NutEntry(nut_entry_id = nut_entry_id,food_entry_id = food_entry_id, nut_id = e[0], nut_value = e[1])
                db.session.add(nut_entry)
                db.session.commit()

            print("nutrients stored!!")

            ingr_data = []
            attr_data = []
            nut_data = []
            ingr_data = IngrEntry.query.filter_by(food_entry_id = food_entry_id).all()
            attr_data = AttrEntry.query.filter_by(food_entry_id = food_entry_id).all()
            nut_data = NutEntry.query.filter_by(food_entry_id = food_entry_id).all()

            print(actual_label)

            #Retrieve Links for healthy Food Recipes
            query ="healthy " + actual_label + " recipe"
            print(query)
            links=[]
            for j in search(query, num=5, stop=5, pause=2):
              links.append(j)
            def remove_html_tags(text):
                return ''.join(xml.etree.ElementTree.fromstring(text).itertext())
            class Recipe_list:
              def __init__(self, link,title):
                self.link = link
                self.title = title
            recipes=[] #array of objects of recipe_list
            for l in links:
              r = requests.get(l);
              if r.status_code != 200:
                  continue
              soup = bs.BeautifulSoup(r.text, 'lxml')
              t=str(soup.find("title"))
              t=remove_html_tags(t)
              recipes.append(Recipe_list(l,t))


              # calorie_tracker(calorie)
        return render_template('dashboard.html',label = label, calorie = calorie, image_link = image_link, ingr_data = ingr_data, attr_data=attr_data, nut_data = nut_data,recipes=recipes, current_user = current_user)
    else:
        return render_template('dashboard.html', current_user = current_user)

        # if calorie:
        #     return redirect(url_for('calorie_tracker', current_user = current_user))

@app.route('/chart',methods = ['POST', 'GET'])
def chart():
    labels = [
    'JAN', 'FEB', 'MAR', 'APR',
    'MAY', 'JUN', 'JUL', 'AUG',
    'SEP', 'OCT', 'NOV', 'DEC'
    ]

    values = [
    967.67, 1190.89, 1079.75, 1349.19,
    2328.91, 2504.28, 2873.83, 4764.87,
    4349.29, 6458.30, 9907, 16297
    ]


    line_labels=labels
    line_values=values
    return render_template('chart.html',labels=line_labels,values=line_values,max=17000)


@app.route('/signup', methods=['POST', 'GET'])
def signup():
    exists= False
    if request.method == 'POST':
       print('into post method')
       user_id = request.form['userid']
       name = request.form['name']
       pwd = request.form['password']
       email = request.form['email']
       age = request.form['age']
       weight = request.form['weight']
       gender = request.form['gender']
       height = request.form['height']
       activity = request.form.get("activity")

       user_obj = FoodUser.query.filter_by(user_id=user_id, email=email).first()
       if user_obj:
          exists=True
          return render_template('signup.html', exists=exists)
       else:
           user = FoodUser(user_id=user_id,name=name,password=pwd,email=email,age=age,weight=weight,gender=gender,height=height, activity=activity)
           db.session.add(user)
           db.session.commit()
           print('inserted!!')
           login_user(user)
           # return render_template('dashboard.html', name = current_user.name)
           return redirect(url_for('dashboard', current_user = current_user))
       #print(user_id)
       #print(name)
       #print(pwd)

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    invalid = False
    if request.method == 'POST':
        user_id = request.form['userid']
        pwd = request.form['password']

        user_obj = FoodUser.query.filter_by(user_id=user_id, password=pwd).first()

        if user_obj:
            print('login successful')
            login_user(user_obj)
            # return render_template('dashboard.html', name = current_user.name)
            return redirect(url_for('dashboard', current_user = current_user))
        else:
            invalid = True
            return render_template('login.html', invalid=invalid)

    return render_template('login.html')


@login_required
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))


@login_required
@app.route('/update_profile', methods=['POST', 'GET'])
def update_profile():
    if request.method == 'POST':
        age = request.form['age']
        weight = request.form['weight']
        gender = request.form['gender']
        height = request.form['height']
        activity = request.form.get("activity")

        # user = FoodUser.query.filter_by(user_id=current_user.user_id, email=current_user.email)
        user = db.session.query(FoodUser).filter_by(user_id = current_user.user_id).first()
        user.age = age
        user.weight = weight
        user.gender = gender
        user.activity = activity
        user.height = height
        db.session.commit()

        current_user.age = age
        current_user.weight = weight
        current_user.gender = gender
        current_user.activity = activity
        current_user.height = height

    return render_template('update_profile.html', current_user=current_user)


@login_required
@app.route('/change_pwd', methods=['POST', 'GET'])
def change_pwd():

    if request.method == 'POST':
        invalid = False
        same_pwd = False

        password = request.form['password']
        old_password = request.form['old_password']

        print(password, old_password)
        if password == old_password:
            same_pwd = True
            return render_template('change_password.html', same_pwd=same_pwd, current_user = current_user)

        user = FoodUser.query.filter_by(user_id=current_user.user_id, password=old_password).first()

        if user:
            user = db.session.query(FoodUser).filter_by(user_id = current_user.user_id, password = old_password).first()
            user.password = password
            current_user.password = password
            db.session.commit()

        else:
            invalid = True
            return render_template('change_password.html', invalid = invalid, current_user = current_user)

        if invalid == False and same_pwd == False:
            return redirect(url_for('dashboard', current_user=current_user))

    return render_template('change_password.html', current_user=current_user)


@login_required
@app.route('/calorie_tracker')
def calorie_tracker():
    cur_weight = current_user.weight
    cur_gender = current_user.gender
    cur_activity = current_user.activity
    cur_age = current_user.age
    cur_height = current_user.height

    if cur_gender == 'male':
        BMR = 88.32 + (13.397 * cur_weight) + (4.799 * cur_height) - (5.677 * cur_age)
    else:
        BMR = 447.593 + (9.247 * cur_weight) + (3.098 * cur_height) - (4.330 * cur_age)

    print(BMR)
    if cur_activity == 'moderate':
        calorie_intake = int(BMR * 1.65)
    elif cur_activity == 'active':
        calorie_intake = int(BMR * 2.0)
    else:
        calorie_intake = int(BMR * 1.3)
    print("calorie:",calorie_intake)

    cur_food_id = []
    calorie = 0
    cur_food_id = FoodEntry.query.filter_by(user_id = current_user.user_id).all()
    for i in cur_food_id:
        food_item_obj = FoodItems.query.filter_by(food_item_id = i.food_item_id).first()
        d1 = i.date_time
        d2 = datetime.now()
        days_diff = (d2-d1).days
        if days_diff < 1:
            calorie =  int(calorie + food_item_obj.calorie)

# User Activities
    today_food = []
    yesterday_food = []
    two_daysago_food = []
    for i in cur_food_id:
        d1 = i.date_time
        d2 = datetime.now()
        days_diff = (d2-d1).days
        print(days_diff)
        if days_diff < 1:
            cur_nut_obj=NutEntry.query.filter_by(food_entry_id = i.food_entry_id).first()
            today_food.append((i.food_item_id,cur_nut_obj.nut_id))
        elif days_diff >=1 and days_diff < 2:
            cur_nut_obj=NutEntry.query.filter_by(food_entry_id = i.food_entry_id).first()
            yesterday_food.append((i.food_item_id,cur_nut_obj.nut_id))
        elif days_diff >=2 and days_diff < 3:
            cur_nut_obj=NutEntry.query.filter_by(food_entry_id = i.food_entry_id).first()
            two_daysago_food.append((i.food_item_id,cur_nut_obj.nut_id))



    labels = [
    '6 Days Before','5 Days Before','4 Days Before', '3 Days Before', '2 Days Before', 'Yesterday', 'Today'
    ]

    values = [0,0,0,0,0,0,0]

    for i in cur_food_id:
        food_item_obj = FoodItems.query.filter_by(food_item_id = i.food_item_id).first()
        d1 = i.date_time
        d2 = datetime.now()
        days_diff = (d2-d1).days
        if days_diff < 1:
            values[6] = values[6] + food_item_obj.calorie
        elif days_diff >= 1 and days_diff < 2:
            values[5] = values[5] + food_item_obj.calorie
        elif days_diff >=2 and days_diff < 3:
            values[4]  = values[4] + food_item_obj.calorie
        elif days_diff >=3 and days_diff <4:
            values[3] = values[3] + food_item_obj.calorie
        elif days_diff >=4 and days_diff < 5:
            values[2] = values[2] + food_item_obj.calorie
        elif days_diff >=5 and days_diff < 6:
            values[1] = values[1] + food_item_obj.calorie
        elif days_diff >=6 and days_diff < 7:
            values[0] = values[0] + food_item_obj.calorie

    line_labels=labels
    line_values=values

    return render_template('calorie_tracker.html', current_user=current_user, calorie_intake = calorie_intake,food_calorie=calorie,today_food=today_food,yesterday_food=yesterday_food,two_daysago_food=two_daysago_food,labels=line_labels,values=line_values)

@app.route('/food_diary')
def food_diary():
    label_calorie = []

    cur_food_id = FoodEntry.query.filter_by(user_id = current_user.user_id).all()
    for i in cur_food_id:
        food_item_obj = FoodItems.query.filter_by(food_item_id = i.food_item_id).first()
        food_nutrients = NutEntry.query.filter_by(food_entry_id = i.food_entry_id).all()
        food_nut = []
        for j in food_nutrients:
            print(j)
            food_nut.append(j.nut_id)

        food_attributes = AttrEntry.query.filter_by(food_entry_id = i.food_entry_id).all()
        food_attr = []
        for k in food_attributes:
            food_attr.append((k.attr_id))

        food_ingredients = IngrEntry.query.filter_by(food_entry_id = i.food_entry_id).all()
        food_ingr = []
        for l in food_ingredients:
            food_ingr.append((l.ingr_id))

        d = i.date_time
        only_date = d.date()
        label_calorie.append([food_item_obj.food_item_id,food_item_obj.calorie,i.image,only_date,food_nut,food_attr,food_ingr])
    print(str(food_nut)[1:-1])
    return render_template('food_diary.html',label_calorie=label_calorie)
