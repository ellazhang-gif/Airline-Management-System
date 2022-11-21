#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 15 15:33:08 2022

@author: ellazhang
"""

# Import Flask Library
from flask import Flask, render_template, request, session, url_for, redirect
import pymysql.cursors
import math
import datetime
import matplotlib.pyplot as plt
import numpy as np
import base64
from io import BytesIO
from werkzeug.security import generate_password_hash,check_password_hash
plt.switch_backend('Agg') 


#Initialize the app from Flask
app = Flask(__name__)
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(days=7)


#Configure MySQL
conn = pymysql.connect(host='localhost',
                       user='root',
                       password='',
                       db='Air Ticket Reservation System',
                       charset='utf8mb4',
                       cursorclass=pymysql.cursors.DictCursor)

# general 
@app.route('/')
def welcome():
    session.clear()
    return render_template('welcome.html')


@app.route('/upcoming_flight',methods=['GET', 'POST'])
def upcoming_flight():
    cursor = conn.cursor()
    query = "SELECT * FROM flight where flight_status = 'upcoming'"
    cursor.execute(query)
    data = cursor.fetchall()
    cursor.close()
    try:
        # coming from other homepage
        if session['username']:
            username = session["username"]
            role = session["role"]
            print(role)
            return render_template("upcoming_flight.html", upcoming_flight = data, role = role,username = username)
        # have not initialize 
        else:
            return render_template("upcoming_flight.html", upcoming_flight=data, role =session["role"],username = session["username"])
    except KeyError:
        return render_template('upcoming_flight.html', upcoming_flight = data)


@app.route('/upcoming_flight/search',methods=['GET', 'POST'])
def upcoming_flight_search():
    query = "SELECT * FROM flight where flight_status = 'upcoming' and"
    appendix = ""
    if request.form['departure_date']:
        d_date = request.form['departure_date']
        d_start = datetime.datetime.strptime(d_date,'%Y-%m-%d')
        d_end = d_start + datetime.timedelta(days=1)
        add = "and '"+ str(d_start)[:10] +"' <=departure_time  and departure_time <='"+ str(d_end)[:10]+"'"
        appendix += add 
    if request.form['arrival_date']:
        a_date = request.form['arrival_date']
        a_start = datetime.datetime.strptime(a_date, '%Y-%m-%d')
        a_end = a_start + datetime.timedelta(days=1)
        add = "and '"+ str(a_start)[:10] +"' >=arrival_time  and arrival_time <='"+ str(a_end)[:10]+"'"
        appendix += add
    if request.form['departure_airport']:
        d_airport = request.form['departure_airport']
        appendix += "and departure_airport = '"
        appendix += d_airport
        appendix += "'"
    if request.form['arrival_airport'] :
        a_airport = request.form['arrival_airport'] 
        appendix += "and arrival_airport = '"
        appendix += a_airport
        appendix += "'"
    if request.form['departure_city']:
        d_city = request.form['departure_city'] 
        add = "and departure_airport in (select airport_name from airport where airport_city ='"+ d_city +"')"
        appendix += add
    if request.form['arrival_city']:
        a_city = request.form['arrival_city'] 
        add = "and arrival_airport in (select airport_name from airport where airport_city = '"+ a_city +"')"
        appendix += add
    if appendix ==  "":
        query = "SELECT * from flight"
    else:
        query += appendix[3:]
    print(query)
    #cursor used to send queries
    cursor = conn.cursor()
    #executes query	
    cursor.execute(query)
    #stores the results in a variable
    data = cursor.fetchall()
    cursor.close()
    error = None
    print(data)
    if (data):
        #creates a session for the the user
        #session is a built in
        return render_template('upcoming_flight.html', upcoming_flight = data)
    else:
        return render_template('upcoming_flight.html', error1 = "Sorry, no flights are found. Please check your input again.")


app.secret_key = 'some key that you will never guess'
if __name__ == "__main__":
    app.run('127.0.0.1', 5000, debug = True)