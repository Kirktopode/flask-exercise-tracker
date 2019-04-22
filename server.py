#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import socket
import sqlite3
from flask import Flask, request, render_template, \
    jsonify, redirect, g
from dateutil.parser import parse
from datetime import datetime
from math import floor
import uuid

# Support for gomix's 'front-end' and 'back-end' UI.
app = Flask(__name__, static_folder='public', template_folder='views')
app.config.from_object('_config')

# Set the app secret key from the secret environment variables.
app.secret = os.environ.get('SECRET')

def connect_db():
    return sqlite3.connect(app.config['DATABASE_PATH'])

# POST /api/exercise/new-user
# POST /api/exercise/add
# GET /api/exercise/log?{userId}[&from][&to][&limit]
@app.route('/')
def homepage():
    """Displays thot hormeparger."""
    return render_template('index.html')
    
@app.route('/api/exercise/log', methods=['GET'])
def getlog():
    """Simple API my hoes anddreas.
    """
    if not "userId" in request.args:
        print("userId not present")
        return jsonify({
            "error":"unknown userId"
        })
    userid = request.args["userId"]
    g.db = connect_db()
    cur = g.db.execute(
        'select name from users where user_id=?', (userid, ) 
    )
    users = cur.fetchall()
    if len(users) == 0:
        print("userId not found")
        return jsonify({
            "error":"unknown userId"
        })
    username = users[0][0]
    fromdate = 0
    if "from" in request.args:
        try:
            fromdate = floor(parse(request.args["from"]).timestamp())
        except ValueError:
            print("Failed parse of string " + request.args["from"] + " as fromdate")
    todate = floor(datetime.now().timestamp())
    if "to" in request.args:
        try:
            todate = floor(parse(request.args["to"]).timestamp())
        except ValueError:
            print("Failed parse of string " + request.args["to"] + " as todate")
    cur = g.db.execute(
        'select description, duration, date from exercises where user_id=? and date<=? and date>=? order by date desc', (userid, todate, fromdate, )
    )
    resp = cur.fetchall()
    limit = len(resp)
    if "limit" in request.args:
        try:
            num = int(request.args["limit"])
            if num < limit and num > 0: limit = num
        except ValueError:
            print("Failed parse of string " + request.args["limit"] + " as limit");
    elist = []
    for i in range(limit):
        elist.append({
            "description": resp[i][0],
            "duration": resp[i][1],
            "date": datetime.fromtimestamp(resp[i][2]).strftime("%a %d %b %Y")
        })
    return jsonify({
        "_id": userid,
        "username": username,
        "count": limit,
        "log": elist
    })
  
@app.route('/api/exercise/new-user', methods=['POST'])
def adduser():
    #  Take in a username, respond with JSON object containing username and userId
    print(request.form)
    if not "name" in request.form:
        return jsonify({
           "error":"field 'username' required" 
        })
    name = request.form["name"]
    g.db = connect_db()
    cur = g.db.execute(
        'select name from users where name=?', (name, )
    )
    if len(cur.fetchall()) > 0:
        return jsonify({
            "error":"username already taken"
        })
    userid = str(uuid.uuid4()).split("-")[-1][:9]
    cur = g.db.execute(
        'select user_id from users where user_id=?', (userid, ) 
    )
    collisions = len(cur.fetchall())
    while collisions > 0:
        userid = str(uuid.uuid4()).split("-")[-1][:9]
        cur = g.db.execute(
            'select user_id from users where user_id=?', (userid, ) 
        )
        collisions = len(cur.fetchall())
    g.db.execute('insert into users (name, user_id) values (?, ?)', (name, userid, ))
    g.db.commit()
    g.db.close()
    return jsonify({
        "name": name,
        "user_id": userid,
    })

@app.route('/api/exercise/add', methods=['POST'])
def addExercise():
    # userId, description, date, duration
    if not 'user_id' in request.form:
        return jsonify({
          "error":"field 'userid' required"
        })
    userid = request.form['user_id']
    g.db = connect_db()
    cur = g.db.execute(
        'select name from users where user_id=?', (userid, )
    )
    users = cur.fetchall()
    if len(users) == 0:
        return jsonify({
            "error":"unknown userid"
        })
    username = users[0][0]
    if not 'duration' in request.form:
        return jsonify({
          "error":"field 'duration' required"
        })
    duration = request.form['duration']
    try:
        duration = int(duration)
    except ValueError:
        try:
            duration = float(duration)
        except:
            return jsonify({
                "error":"duration could not be parsed as a number"
            })
    if not 'description' in request.form:
        return jsonify({
            "error":"field 'description' required"
        })
    description = request.form['description']
    date = datetime.now()
    if 'date' in request.form and request.form['date'] != '':
        try:
            date = parse(request.form['date'])#.strftime("%a %d %b %Y") sdfsdf
        except ValueError:
            return jsonify({
                "error":"cannot parse date value as a date"
            })
    dateval = floor(date.timestamp())
    datestring = date.strftime("%a %d %b %Y")
    g.db.execute('insert into exercises (user_id, description, duration, date) values (?, ?, ?, ?)', (userid, description, duration, dateval, ))
    g.db.commit()
    g.db.close()
    return jsonify({
        "username" : username,
        "description" : description,
        "duration" : duration,
        "_id" : userid,
        "date" : datestring
    })
    
#   username	"fishtoo"
# description	"gdf"
# duration	2342
# _id	"SkYeVUv9E"
# date	"Fri Jun 03 2929"
  
  
if __name__ == '__main__':
    app.run()