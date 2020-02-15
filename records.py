import os
from flask import Flask, render_template, redirect, request, url_for, make_response, session
from flask_pymongo import PyMongo, pymongo
from bson.objectid import ObjectId
from datetime import date
from os import path
from passlib.hash import sha256_crypt
from app import app

mongo = PyMongo(app)

# add record page
@app.route('/add_record')
def add_record():
    return render_template('addrecord.html')

# insert a record to the DB
@app.route('/insert_record', methods=['POST'])
def insert_record():
    currentUser = session['username']
    users = mongo.db.users
    login_user = users.find_one({'username' : currentUser})
    username = login_user.get('username')
    records = mongo.db.records
    session_type = request.form['session_type']
    location = login_user.get('location')
    # current users data
    gender = login_user.get('gender')
    age = login_user.get('age')
    body_weight = login_user.get('body_weight')
    bw_unit = login_user.get('bw_unit')
    # checking the session type
    if session_type == 'weightlifting':
        training_session = {'session_exercise_1': request.form['session_exercise_1'],'session_sets_1': request.form['session_sets_1'] , 'session_weight_1': float(request.form['session_weight_1'])}
    elif session_type == 'running':
        training_session = float(request.form['distance'])
    elif session_type == 'cycling':
        training_session = float(request.form['distance'])
    elif session_type == 'walking':
        training_session = float(request.form['distance'])
        # the data from the form
    date = request.form['date']
    dateYear = date[2: 4]
    dateMonth = date[5:7]
    dateDay = date[8:10]
    date = dateDay + '-' + dateMonth + '-' + dateYear
    dateSortNo = dateYear + dateMonth + dateDay
    length_hour = request.form['length_hour']
    length_min = request.form['length_min']
    motivated = request.form['motivated']
    effort = request.form['effort']
    difficulty = request.form['difficulty'] 
    session_unit = request.form['session_unit']
    notes = request.form['notes']
    weightliftingDict = {'session_unit': session_unit,'bw_unit': bw_unit, 'body_weight': body_weight,'session_type': session_type, 'age': age, 'gender': gender ,'username':username, 'notes': notes, 'training_session': training_session, 'location': location, 'date': date, 'dateSortNo': dateSortNo, 'length_hour': int(length_hour), 'length_min': int(length_min), 'motivated':motivated, 'effort': effort,'difficulty': difficulty}
    records.insert_one(weightliftingDict)
    return redirect('record')

# just the records logged by the user
@app.route('/users_records')
def users_records():
        # to find out if the user is already logged in
    try:
        currentUser = session['username']
    except:
        return redirect(url_for('login_page'))
    user = mongo.db.users
    currentUsersAccount = user.find_one({'username': currentUser})
    # get filter info from cookies
    filter_date = request.cookies.get('filter_date_user_records')
    filter_session_type = request.cookies.get('filter_session_type_records')  
    def filter():
        filter_dictionary = {'username': currentUser}
        if filter_date:
            filter_dictionary.update({'date': filter_date})
        if filter_session_type:
            if filter_session_type != 'all':
                filter_dictionary.update({'session_type': filter_session_type})
        
        return filter_dictionary
    records = mongo.db.records.find(filter())
    # sort the sessions by the date
    sortCards = request.cookies.get('sort_profile')
    if sortCards == 'Newest First':
        records = records.sort("dateSortNo", pymongo.DESCENDING)
    elif sortCards == 'Oldest First':
        records = records.sort("dateSortNo", pymongo.ASCENDING)
    else:
        records = records.sort("dateSortNo", pymongo.DESCENDING)
    # all the records saved by the user
    allRecords = mongo.db.records.find({'username': currentUser})
    recordCount = 0
    for record in allRecords:
        recordCount += 1

    return render_template('usersRecords.html', records=records, allRecords=recordCount, filter_session_type=filter_session_type)

# filter the records for the users records page.
@app.route('/filter_usersrecords', methods=['POST'])
def filter_usersrecords():
    filter_sort = request.form['sort_session_records']
    filter_session_type = request.form["filter_session_type_records"]
    filter_date = request.form['filter_session_date_records']
    res = make_response(redirect(url_for('users_records')))
    res.set_cookie('filter_session_type_records', filter_session_type)
    res.set_cookie('filter_session_date_records', filter_date)
    res.set_cookie('sort_session_records', filter_sort)
    return res
 
# the records logged by all users page
@app.route('/record')
def record():
    records = mongo.db.records.find()
    currentUser = session['username']
    users = mongo.db.users
    login_user = users.find_one({'username' : currentUser})
    unitVar = login_user.get('selected_unit')
    unit_distance = login_user.get('selected_distance')
    # finding all the bench press one rep max and sorting them with the height number to the start of the list
    weightBenched = mongo.db.records.find({'training_session.session_exercise_1': 'Bench Press', 'training_session.session_sets_1': '1'})
    sortedBench = weightBenched.sort('training_session.session_weight_1', pymongo.DESCENDING)
    # finding all the Squat one rep max and sorting them with the height number to the start of the list
    weightSquat = mongo.db.records.find({'training_session.session_exercise_1': 'Squat', 'training_session.session_sets_1': '1'})
    sortedSquat = weightSquat.sort('training_session.session_weight_1', pymongo.DESCENDING)
    # finding all the Deadlift one rep max and sorting them with the height number to the start of the list
    weightDeadlift = mongo.db.records.find({'training_session.session_exercise_1': 'Deadlift', 'training_session.session_sets_1': '1'})
    sortedDeadlift = weightDeadlift.sort('training_session.session_weight_1', pymongo.DESCENDING)
    recordCount = mongo.db.records.find()
    recordCountStore = 0
    for record in recordCount:
        recordCountStore += 1
    return render_template('records.html', recordCount=recordCountStore, distanceUnit=unit_distance, records=records, unit=unitVar, weightBenched=sortedBench, sortedSquat=sortedSquat, sortedDeadlift=sortedDeadlift)

# filter the records on the records page for all users
@app.route('/filter_records', methods=['POST'])
def filter_records():
    filter_sort = request.form['sort_session_records']
    filter_session_type = request.form["filter_session_type_records"]
    filter_date = request.form['filter_session_date_records']
    res = make_response(redirect(url_for('users_records')))
    res.set_cookie('filter_session_type_records', filter_session_type)
    res.set_cookie('filter_session_date_records', filter_date)
    res.set_cookie('sort_session_records', filter_sort)
    return res

# delete a record from the DB
@app.route('/delete_record/<session_id>')
def delete_record(session_id):
    mongo.db.records.remove({'_id': ObjectId(session_id)})
    return redirect(url_for('profile'))
