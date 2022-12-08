#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 15 15:33:08 2022

@author: ellazhang, Shiyuan Liu
"""

# Import Flask Library
from flask import Flask, render_template, request, session, url_for, redirect
import pymysql.cursors
import math
import matplotlib.pyplot as plt
import numpy as np
import base64
from io import BytesIO
import datetime
from dateutil.relativedelta import relativedelta
from werkzeug.security import generate_password_hash,check_password_hash
plt.switch_backend('Agg') 


#Initialize the app from Flask
app = Flask(__name__)
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(days=7)


#Configure MySQL
conn = pymysql.connect(host='localhost',
                       user='root',
                       password='',
                       db='Airline Ticket',
                       charset='utf8mb4',
                       cursorclass=pymysql.cursors.DictCursor)

# general 
@app.route('/')
def welcome():
    session.clear()
    return render_template('welcome.html')

@app.route('/login')
def login():
	return render_template('login.html')

@app.route("/loginAuth", methods=["GET", "POST"])
def loginAuth():
    username = request.form['username']
    password = request.form['password']
    role = request.form['role']

    cursor = conn.cursor()
    query_permission = "SELECT * from permission where staff_user_name = '{}'"
    cursor.execute(query_permission.format(username))
    permission_data = cursor.fetchall()

    query_main = "SELECT * FROM Airline_Staff WHERE staff_user_name = '{}' and staff_password = '{}'"
    cursor.execute(query_main.format(username, password))
    data = cursor.fetchall()[0]
    
    if(data):
        query_permission = "SELECT * from permission where staff_user_name = '{}'"
        cursor.execute(query_permission.format(username))
        permission_data = cursor.fetchall()
        session['username'] = username
        session['role'] = role
        if len(permission_data) == 2:
            session['permission'] = 'Admin_Operator'
            return redirect(url_for('airline_staff_home_admin_operator'))
        else:
            if permission_data[0]['permission_name'] == 'Admin':
                session['permission'] = 'Admin'
                return redirect(url_for('airline_staff_home_admin'))
            else:
                session['permission'] = 'Operator'
                return redirect(url_for('airline_staff_home_operator'))
    else:
        error = 'Invalid login or username'
        return render_template('login.html', error=error)


#airline_staff_home_admin_operator
@app.route('/airline_staff_home_admin_operator')
def airline_staff_home_admin_operator():
    username = session['username']
    cursor = conn.cursor()
    query_airline = "select airline_name FROM Airline_Staff where staff_user_name = '{}'"
    cursor.execute(query_airline.format(username))
    airline_name = cursor.fetchall()[0]['airline_name']

    end_date = datetime.date.today() + relativedelta(days=+30)
    begin_date = datetime.date.today()
    begin_date = datetime.datetime(begin_date.year, begin_date.month, begin_date.day, 0, 0, 0)
    end_date = datetime.datetime(end_date.year, end_date.month, end_date.day, 0, 0, 0)

    begin_date_3_month = datetime.date.today() + relativedelta(months=-3)
    end_date_3_month = datetime.date.today()
    begin_date_3_month = datetime.datetime(begin_date_3_month.year, begin_date_3_month.month, begin_date_3_month.day, 0, 0, 0)
    end_date_3_month = datetime.datetime(end_date_3_month.year, end_date_3_month.month, end_date_3_month.day, 0, 0, 0)

    begin_date_year = datetime.date.today() + relativedelta(months = -12)
    end_date_year = datetime.date.today()
    begin_date_year = datetime.datetime(begin_date_year.year, begin_date_year.month, begin_date_year.day, 0, 0, 0)
    end_date_year = datetime.datetime(end_date_year.year, end_date_year.month, end_date_year.day, 0, 0, 0)

    query = "SELECT * FROM Flight where airline_name = '{}' and status = 'upcoming'\
        and departure_time >= '{}.000' and  departure_time <= '{}.000'"
    cursor.execute(query.format(airline_name, begin_date, end_date))
    data = cursor.fetchall()
    for element in data:
        element['departure_time'] = str(element['departure_time'])
        element['arrival_time'] = str(element['arrival_time'])
    session['my_flight'] = data
    session['airline_name'] = airline_name


    query = "select airport_city, count(airport_city)\
                            from Flight, Airport\
                            where Flight.arrival_airport_name = Airport.airport_name and Flight.departure_time>= '{}' and Flight.departure_time<='{}' \
                            group by airport_city\
                            order by count(airport_city) desc limit 3"
    cursor.execute(query.format(begin_date_3_month, end_date_3_month))
    top_3_destinations_data_3_month = cursor.fetchall()
    num = 1
    for element in top_3_destinations_data_3_month:
        element['rank'] = num
        num += 1
    cursor.execute(query.format(begin_date_year, end_date_year))
    top_3_destinations_data_year = cursor.fetchall()
    num = 1
    for element in top_3_destinations_data_year:
        element['rank'] = num
        num += 1
    session['ranking_last_3_month'] = top_3_destinations_data_3_month
    session['ranking_last_year'] = top_3_destinations_data_year

    begin_date = datetime.date.today() + relativedelta(months = -12)
    end_date = datetime.date.today()
    begin_date = datetime.datetime(begin_date.year, begin_date.month, begin_date.day, 0, 0, 0)
    end_date = datetime.datetime(end_date.year, end_date.month, end_date.day, 0, 0, 0)

    query = "select booking_agent_id, booking_agent_email, sum(price*0.1) as commission_fee from (Ticket natural join Booking_Agent) natural join Flight where\
        airline_name = '{}' and booking_agent_email is not null and purchase_date >= '{}.000' and purchase_date <= '{}.000' group by booking_agent_id, booking_agent_email order by commission_fee desc limit 5"
    cursor.execute(query.format(airline_name, str(begin_date), str(end_date)))
    data_commission = cursor.fetchall()
    num = 1
    for element in data_commission:
        element['rank'] = num
        num += 1
    session['ranking_for_commission_received'] = data_commission

    query_frequent_customer = "select count(*) as purchase_num, customer_email, customer_name from Ticket natural join Customer where airline_name = '{}' and purchase_date >= '{}.000' and purchase_date <= '{}.000'\
        group by customer_email order by purchase_num desc limit 1"
    cursor.execute(query_frequent_customer.format(airline_name, str(begin_date), str(end_date)))
    data_frequent_customer = cursor.fetchall()
    frequent_customer_name = data_frequent_customer[0]['customer_name']
    frequent_customer_email = data_frequent_customer[0]['customer_email']
    session['frequent_customer_name'] = frequent_customer_name
    session['frequent_customer_email'] = frequent_customer_email
    cursor.close()

    if(data):
        return render_template('Airline_staff_home_admin_operator.html', my_flight = data, airline_name = airline_name, username = username, 
        ranking_last_3_month = session['ranking_last_3_month'], ranking_last_year = session['ranking_last_year'], 
        ranking_for_commission_received = session['ranking_for_commission_received'], frequent_customer_email = session['frequent_customer_email'], 
        frequent_customer_name = session['frequent_customer_name'])
    else:
        return render_template('Airline_staff_home_admin_operator.html', error0 = "Sorry, no flights are found. Please check your input again.", 
        airline_name = airline_name, username = username, ranking_last_3_month = session['ranking_last_3_month'], 
        ranking_last_year = session['ranking_last_year'], ranking_for_commission_received = session['ranking_for_commission_received'], 
        frequent_customer_email = session['frequent_customer_email'], frequent_customer_name = session['frequent_customer_name'])

@app.route("/airline_staff_home_admin_operator/view_my_flight", methods=["GET", "POST"])
def view_my_flight():
    username = session['username']
    cursor = conn.cursor()
    airline_name = session['airline_name']

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
    if request.form['flight_num']:
        flight_num = request.form['flight_num']
        appendix += "and flight_num = '"
        appendix += flight_num
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
        query = "SELECT * FROM Flight where airline_name = '{}'"
    else:
        query = "SELECT * FROM Flight where airline_name = '{}' and"
        query += appendix[3:]
    print(query)
    #cursor used to send queries
    cursor = conn.cursor()
    #executes query	
    cursor.execute(query.format(airline_name))
    #stores the results in a variable
    data = cursor.fetchall()
    for element in data:
        element['departure_time'] = str(element['departure_time'])
        element['arrival_time'] = str(element['arrival_time'])
    session['my_flight'] = data
    cursor.close()
    error = None
    if (data):
        #creates a session for the the user
        #session is a built in
        return render_template('Airline_staff_home_admin_operator.html', my_flight = data, airline_name = airline_name, username = username, 
        ranking_last_3_month = session['ranking_last_3_month'], ranking_last_year = session['ranking_last_year'], 
        ranking_for_commission_received = session['ranking_for_commission_received'], frequent_customer_email = session['frequent_customer_email'], 
        frequent_customer_name = session['frequent_customer_name'])   
    else:
        return render_template('airline_staff_home_admin_operator.html', error0 = "Sorry, no flights are found. Please check your input again.", 
        airline_name = airline_name, username = username, 
        ranking_last_3_month = session['ranking_last_3_month'], ranking_last_year = session['ranking_last_year'], 
        ranking_for_commission_received = session['ranking_for_commission_received'], frequent_customer_email = session['frequent_customer_email'], 
        frequent_customer_name = session['frequent_customer_name'])


@app.route('/airline_staff_home_admin_operator/customer_list_for_flights', methods=["GET", "POST"])
def customer_list_for_flights():
    username = session['username']
    cursor = conn.cursor()
    query_airline = "select airline_name FROM Airline_Staff where staff_user_name = '{}'"
    cursor.execute(query_airline.format(username))
    airline_name = cursor.fetchall()[0]['airline_name']

    if request.form['flight_num']:
        flight_num = request.form['flight_num']
        query =  "SELECT * FROM (Ticket natural join Customer) natural join Flight where flight_num = '{}' and airline_name = '{}'"
        cursor.execute(query.format(flight_num, airline_name))
        customer_list_data = cursor.fetchall()
        session['cutomer_list'] = customer_list_data
        cursor.close()
        if (customer_list_data):
            return render_template('airline_staff_home_admin_operator.html', customer_list = customer_list_data, 
            my_flight = session['my_flight'], airline_name = airline_name, username = username, 
            ranking_last_3_month = session['ranking_last_3_month'], ranking_last_year = session['ranking_last_year'], 
            ranking_for_commission_received = session['ranking_for_commission_received'], frequent_customer_email = session['frequent_customer_email'], 
            frequent_customer_name = session['frequent_customer_name'])
        else:
            return render_template('airline_staff_home_admin_operator.html', error1 = 'Sorry, wrong flight num. Pleas check your input again.',
            my_flight = session['my_flight'], airline_name = airline_name, username = username, 
            ranking_last_3_month = session['ranking_last_3_month'], ranking_last_year = session['ranking_last_year'], 
            ranking_for_commission_received = session['ranking_for_commission_received'], frequent_customer_email = session['frequent_customer_email'], 
            frequent_customer_name = session['frequent_customer_name'])
    else:
        cursor.close()
        return render_template('airline_staff_home_admin_operator.html', error1 = 'Please input a vaild flight number first.',
        my_flight = session['my_flight'], airline_name = airline_name, username = username, 
        ranking_last_3_month = session['ranking_last_3_month'], ranking_last_year = session['ranking_last_year'], 
        ranking_for_commission_received = session['ranking_for_commission_received'], frequent_customer_email = session['frequent_customer_email'], 
        frequent_customer_name = session['frequent_customer_name'])



@app.route("/airline_staff_home_admin_operator/create_new_flight")
def create_new_flight():
    username = session['username']
    airline_name = session['airline_name']
    cursor = conn.cursor()

    end_date = datetime.date.today() + relativedelta(days=+30)
    begin_date = datetime.date.today()
    begin_date = datetime.datetime(begin_date.year, begin_date.month, begin_date.day, 0, 0, 0)
    end_date = datetime.datetime(end_date.year, end_date.month, end_date.day, 0, 0, 0)

    query = "SELECT * FROM Flight where airline_name = '{}' and status = 'upcoming'\
        and departure_time >= '{}.000' and  departure_time <= '{}.000'"
    cursor.execute(query.format(airline_name, begin_date, end_date))
    data = cursor.fetchall()
    for element in data:
        element['departure_time'] = str(element['departure_time'])
        element['arrival_time'] = str(element['arrival_time'])
    session['create_flight_table'] = data
    cursor.close()

    if(data):
        return render_template('create_new_flight_admin_operator.html', create_flight_table = session['create_flight_table'], username = username)
    else:
        return render_template('create_new_flight_admin_operator.html', username = username, error0 = "Your airline doesn't have any upcoming flights in next 30 days. You can add one below.")

@app.route("/airline_staff_home_admin_operator/create_new_flight/action", methods=["GET", "POST"])
def create_new_flight_action():
    username = session['username']
    cursor = conn.cursor()
    query_airline = "select airline_name FROM Airline_Staff where staff_user_name = '{}'"
    cursor.execute(query_airline.format(username))
    airline_name = cursor.fetchall()[0]['airline_name']

    query_airport = "select airport_name from Airport"
    cursor.execute(query_airport)
    airport_name_list = cursor.fetchall()
    airport_list = []
    for airport_element in airport_name_list:
        airport_list.append(airport_element['airport_name'])

    query_airplane_id = "select airplane_id from Airplane where airline_name = '{}'"
    cursor.execute(query_airplane_id.format(airline_name))
    airplane_id_list = cursor.fetchall()
    airplane_list = []
    for airplane_element in airplane_id_list:
        airplane_list.append(airplane_element['airplane_id'])

    num = 0
    if request.form['airline_name']:
        airline_name_input = request.form['airline_name']
        num += 1
    if request.form['flight_num']:
        flight_num = request.form['flight_num']
        num += 1
    if request.form['departure_airport_name']:
        departure_airport_name = request.form['departure_airport_name']
        num += 1
    if request.form['arrival_airport_name']:
        arrival_airport_name = request.form['arrival_airport_name']
        num += 1
    if request.form['departure_time']:
        departure_time = request.form['departure_time']
        d_date = departure_time[0:10]
        d_time = departure_time[11:]
        departure_time = d_date + ' ' + d_time + ':00'
        num += 1
    if request.form['arrival_time']:
        arrival_time = request.form['arrival_time']
        a_date = arrival_time[0:10]
        a_time = arrival_time[11:]
        arrival_time = a_date + ' ' + a_time + ':00'
        num += 1
    if request.form['price']:
        price = request.form['price']
        num += 1
    if request.form['status']:
        status = request.form['status']
        num += 1
    if request.form['airplane_id']:
        airplane_id = request.form['airplane_id']
        num += 1
    if num == 9:
        if airline_name_input != airline_name:
            return render_template('create_new_flight_admin_operator.html', username = username, create_flight_table = session['create_flight_table'], error = 'You can only add new flight for your airline. Please try again.')
        if (departure_airport_name not in airport_list) or (arrival_airport_name not in airport_list):
            return render_template('create_new_flight_admin_operator.html', username = username, create_flight_table = session['create_flight_table'], error = 'Airport you input does not exist, please try again.')
        else:
            if departure_airport_name == arrival_airport_name:
                return render_template('create_new_flight_admin_operator.html', username = username, create_flight_table = session['create_flight_table'], error = 'Arrival and Departure Airport can not be the same. Please try again.')
        if airplane_id not in airplane_list:
            return render_template('create_new_flight_admin_operator.html', username = username, create_flight_table = session['create_flight_table'], error = 'Airplane you input does not exist, please try again.')
        if status not in ['upcoming', 'delayed', 'in-progress']:
            return render_template('create_new_flight_admin_operator.html', username = username, create_flight_table = session['create_flight_table'], error = 'Status should only be in-progress/upcoming/delayed. Please try again.')       
        query = "insert into Flight values ('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')"
        cursor.execute(query.format(airline_name, flight_num, departure_time, arrival_time, price,
        status, arrival_airport_name, departure_airport_name, airplane_id))
        conn.commit()

        end_date = datetime.date.today() + relativedelta(days=+30)
        begin_date = datetime.date.today()
        begin_date = datetime.datetime(begin_date.year, begin_date.month, begin_date.day, 0, 0, 0)
        end_date = datetime.datetime(end_date.year, end_date.month, end_date.day, 0, 0, 0)

        query = "SELECT * FROM Flight where airline_name = '{}' and status = 'upcoming'\
        and departure_time >= '{}.000' and  departure_time <= '{}.000'"
        cursor.execute(query.format(airline_name, begin_date, end_date))
        data = cursor.fetchall()
        for element in data:
            element['departure_time'] = str(element['departure_time'])
            element['arrival_time'] = str(element['arrival_time'])
        session['create_flight_table'] = data
        cursor.close()
        return render_template('create_new_flight_admin_operator.html', username = username, create_flight_table = session['create_flight_table'])
    else:
        return render_template('create_new_flight_admin_operator.html', username = username, error = 'Please add all the information. Please try again.', create_flight_table = session['create_flihgt_table'])


@app.route("/airline_staff_home_admin_operator/add_airplane")
def add_airplane():
    username = session['username']
    airline_name = session['airline_name']
    cursor = conn.cursor()

    query = "SELECT * FROM Airplane where airline_name = '{}'"
    cursor.execute(query.format(airline_name))
    data = cursor.fetchall()
    session['my_airplane'] = data
    cursor.close()

    if(data):
        return render_template('add_airplane_admin_operator.html', my_airplane = session['my_airplane'], username = username)
    else:
        return render_template('add_airplane_admin_operator.html', username = username, error0 = "Your airline doesn't have any airplane. You can add one below.")

@app.route("/airline_staff_home_admin_operator/add_airplane/action", methods=["GET", "POST"])
def add_airplane_action():
    username = session['username']
    airline_name = session['airline_name']
    cursor = conn.cursor()
    query_airplane_id = "select airplane_id from Airplane where airline_name = '{}'"
    cursor.execute(query_airplane_id.format(airline_name))
    airplane_id_list = cursor.fetchall()
    airplane_list = []
    for airplane_element in airplane_id_list:
        airplane_list.append(airplane_element['airplane_id'])

    num = 0
    if request.form['airline_name']:
        airline_name_input = request.form['airline_name']
        num += 1
    if request.form['airplane_id']:
        airplane_id = request.form['airplane_id']
        num += 1
    if request.form['seats']:
        seats = request.form['seats']
        num += 1

    if num == 3:
        if airline_name_input != airline_name:
            return render_template('add_airplane_admin_operator.html', username = username, my_airplane = session['my_airplane'], error = 'You can only add new airplane for your airline. Please try again.')
        if airplane_id in airplane_list:
            return render_template('add_airplane_admin_operator.html', username = username, my_airplane = session['my_airplane'], error = 'The airplane id is used in your airline. Please try again.')
        query = "insert into Airplane values ('{}', '{}', '{}')"
        cursor.execute(query.format(airplane_id ,airline_name, seats))
        print(query)
        conn.commit()

        query = "SELECT * FROM Airplane where airline_name = '{}'"
        cursor.execute(query.format(airline_name))
        data = cursor.fetchall()
        session['my_airplane'] = data
        cursor.close()
        return render_template('add_airplane_admin_operator.html', username = username, my_airplane = session['my_airplane'])
    else:
        return render_template('add_airplane_admin_operator.html', username = username, error = 'Please add all the information. Please try again.', my_airplane = session['my_airplane'])



@app.route("/airline_staff_home_admin_operator/change_status")
def change_status():
    return render_template('change_status_admin_operator.html')

@app.route("/airline_staff_home_admin_operator/change_status/action", methods=["GET", "POST"] )
def change_status_action():
    username = session['username']
    airline_name = session['airline_name']
    cursor = conn.cursor()
    query_flight_num = "select flight_num from Flight where airline_name = '{}'"
    cursor.execute(query_flight_num.format(airline_name))
    flight_num_list = cursor.fetchall()
    print(flight_num_list)
    flight_list = []
    for flight_element in flight_num_list:
        flight_list.append(flight_element['flight_num'])

    num = 0
    if request.form['airline_name']:
        airline_name_input = request.form['airline_name']
        num += 1
    if request.form['flight_num']:
        flight_num_input = request.form['flight_num']
        num += 1
    if request.form['status']:
        status_input = request.form['status']
        num += 1
    if num == 3:
        if airline_name_input != airline_name:
            return render_template('change_status_admin_operator.html', username = username, error = "You can only change status for the flight owned by your airline. Please try again.")
        if flight_num_input not in flight_list:
            return render_template('change_status_admin_operator.html', username = username, error = "The flight number you input is not vaild. Please try again.")
        if status_input not in ['upcoming', 'delayed', 'in-progress']:
            return render_template('change_status_admin_operator.html', username = username, error = 'Status should only be in-progress/upcoming/delayed. Please try again.')       
        query = "update Flight set status = '{}' where airline_name = '{}' and flight_num = '{}'"
        cursor.execute(query.format(status_input, airline_name_input, flight_num_input))
        conn.commit()
        cursor.close()
        return render_template('change_status_admin_operator.html', username = username, error = "You have successfully change a flight status!")
    else:
        return render_template('change_status_admin_operator.html', username = username, error = "Your airline doesn't have any airplane. You can add one below.")


@app.route("/airline_staff_home_admin_operator/add_airport")
def add_airport():
    username = session['username']
    airline_name = session['airline_name']
    cursor = conn.cursor()
    query = "select * from Airport"
    cursor.execute(query)
    data = cursor.fetchall()
    session['world_airport'] = data

    query_my_airport = "select * from Airport_for_Airline where airline_name = '{}'"
    cursor.execute(query_my_airport.format(airline_name))
    data_my_airport = cursor.fetchall()
    session['my_airport'] = data_my_airport
    cursor.close()

    if(data_my_airport):    
        return render_template('add_airport_admin_operator.html', world_airport = session['world_airport'], my_airport = session['my_airport'], username = username)
    else:
        return render_template('add_airport_admin_operator.html', world_airport = session['world_airport'], error0 = 'There is no airport for your airline now. You can add one below.', username = username)

@app.route("/airline_staff_home_admin_operator/add_airport/my_action", methods=["GET", "POST"])
def add_airport_my_action():
    username = session['username']
    airline_name = session['airline_name']
    cursor = conn.cursor()
    query = "select airport_name from Airport"
    cursor.execute(query)
    world_airport_dict = cursor.fetchall()
    world_airport_list = []
    for element in world_airport_dict:
        world_airport_list.append(element['airport_name'])

    query_world_airport = "select * from Airport"
    cursor.execute(query_world_airport)
    data_world_airport = cursor.fetchall()

    query_my_airport = "select * from Airport_for_Airline where airline_name = '{}'"
    cursor.execute(query_my_airport.format(airline_name))
    data_my_airport = cursor.fetchall()
    my_airport_list = []
    for element in data_my_airport:
        my_airport_list.append(element['airport_name'])

    num = 0
    if request.form['airport_name']:
        airport_name_input = request.form['airport_name']
        num += 1
    if request.form['airline_name']:
        airline_name_input = request.form['airline_name']
        num += 1
    
    if num == 2:
        if airline_name_input != airline_name:
             return render_template('add_airport_admin_operator.html', world_airport = session['world_airport'], my_airport = session['my_airport'], username = username, error2 = 'You can only add airport to your airline system. Please try again.') 
        if airport_name_input not in world_airport_list:
            return render_template('add_airport_admin_operator.html', world_airport = session['world_airport'], my_airport = session['my_airport'], username = username, error2 = 'The airport you input is not vaild. Please try again.') 
        if airport_name_input in my_airport_list:
            return render_template('add_airport_admin_operator.html', world_airport = session['world_airport'], my_airport = session['my_airport'], username = username, error2 = 'The airport you input is already in the system. Please try again.') 
        else:
            query = "insert into Airport_for_Airline values ('{}', '{}')"
            cursor.execute(query.format(airport_name_input, airline_name_input))
            conn.commit()

            query_my_airport = "select * from Airport_for_Airline where airline_name = '{}'"
            cursor.execute(query_my_airport.format(airline_name))
            data_my_airport = cursor.fetchall()
            session['my_airport'] = data_my_airport
            cursor.close()

            return render_template('add_airport_admin_operator.html', world_airport = session['world_airport'], my_airport = session['my_airport'], username = username)
    else:
         return render_template('add_airport_admin_operator.html', world_airport = session['world_airport'], my_airport = session['my_airport'], username = username, error2 = 'Please input all the information.') 


@app.route('/airline_staff_home_admin_operator/top_5_booking_agent_by_month', methods=["GET", "POST"])
def top_5_booking_agent_by_month():
    username = session['username']
    airline_name = session['airline_name']

    if request.form['month']:
        month = request.form['month']

    if(month):
        today = datetime.date.today()
        today = str(datetime.datetime(today.year, today.month, today.day, 0, 0, 0))
        if str(month) >= today[0:7]:
            return render_template('airline_staff_home_admin_operator.html', error2 = 'Only avaiable for past month. Please try again.',
            my_flight = session['my_flight'], airline_name = airline_name, username = username, 
            ranking_last_3_month = session['ranking_last_3_month'], ranking_last_year = session['ranking_last_year'], 
            ranking_for_commission_received = session['ranking_for_commission_received'], frequent_customer_email = session['frequent_customer_email'], 
            frequent_customer_name = session['frequent_customer_name'])
        else:
            begin_month = datetime.datetime(int(month[0:4]), int(month[5:7]), 1, 0, 0, 0)
            end_month = begin_month + relativedelta(months=+1)

            cursor = conn.cursor()
            query = "select booking_agent_id, booking_agent_email, count(ticket_id) as num_of_ticket FROM Ticket natural join Booking_Agent where airline_name = '{}' and purchase_date >= '{}.000' and purchase_date <= '{}.000' and booking_agent_email is not null\
                group by booking_agent_id, booking_agent_email order by count(ticket_id) desc limit 5"
            cursor.execute(query.format(airline_name, str(begin_month), str(end_month)))
            data = cursor.fetchall()
            num = 1
            for element in data:
                element['rank'] = num
                num += 1
            session['ranking_for_month'] = data
            cursor.close()
            if(data):
                return render_template('airline_staff_home_admin_operator.html', ranking_for_month = data,
                my_flight = session['my_flight'], airline_name = airline_name, username = username, 
                ranking_last_3_month = session['ranking_last_3_month'], ranking_last_year = session['ranking_last_year'], 
                ranking_for_commission_received = session['ranking_for_commission_received'], frequent_customer_email = session['frequent_customer_email'], 
                frequent_customer_name = session['frequent_customer_name'])         
            else:
                return render_template('airline_staff_home_admin_operator.html', error2 = 'No booking agents sold the ticket from your airline in that time period.', 
                my_flight = session['my_flight'], airline_name = airline_name, username = username, 
                ranking_last_3_month = session['ranking_last_3_month'], ranking_last_year = session['ranking_last_year'], 
                ranking_for_commission_received = session['ranking_for_commission_received'], frequent_customer_email = session['frequent_customer_email'], 
                frequent_customer_name = session['frequent_customer_name'])
    else:
        return render_template('airline_staff_home_admin_operator.html', error2 = 'Please give an input.', 
            my_flight = session['my_flight'], airline_name = airline_name, username = username, 
            ranking_last_3_month = session['ranking_last_3_month'], ranking_last_year = session['ranking_last_year'], 
            ranking_for_commission_received = session['ranking_for_commission_received'], frequent_customer_email = session['frequent_customer_email'], 
            frequent_customer_name = session['frequent_customer_name'])


@app.route('/airline_staff_home_admin_operator/top_5_booking_agent_by_year', methods=["GET", "POST"])
def top_5_booking_agent_by_year():
    username = session['username']
    airline_name = session['airline_name']

    if request.form['year']:
        year = request.form['year']
        print(year)
    if(year):
        today = datetime.date.today()
        today = str(datetime.datetime(today.year, today.month, today.day, 0, 0, 0))
        if str(year) > today[0:4]:
            return render_template('airline_staff_home_admin_operator.html', error3 = 'Only avaiable for past year. Please try again.',
            my_flight = session['my_flight'], airline_name = airline_name, username = username, 
            ranking_last_3_month = session['ranking_last_3_month'], ranking_last_year = session['ranking_last_year'], 
            ranking_for_commission_received = session['ranking_for_commission_received'], frequent_customer_email = session['frequent_customer_email'], 
            frequent_customer_name = session['frequent_customer_name'])
        else:
            begin_year = datetime.datetime(int(year), 1, 1, 0, 0, 0)
            end_year = begin_year + relativedelta(months=+12)

            cursor = conn.cursor()
            query = "select booking_agent_id, booking_agent_email, count(ticket_id) as num_of_ticket FROM Ticket natural join Booking_Agent where airline_name = '{}' and purchase_date >= '{}.000' and purchase_date <= '{}.000' and booking_agent_email is not null\
                group by booking_agent_id, booking_agent_email order by count(ticket_id) desc limit 5"
            cursor.execute(query.format(airline_name, str(begin_year), str(end_year)))
            data = cursor.fetchall()
            num = 1
            for element in data:
                element['rank'] = num
                num += 1
            session['ranking_for_year'] = data
            cursor.close()
            if(data):
                return render_template('airline_staff_home_admin_operator.html', ranking_for_year = data,
                my_flight = session['my_flight'], airline_name = airline_name, username = username, 
                ranking_last_3_month = session['ranking_last_3_month'], ranking_last_year = session['ranking_last_year'], 
                ranking_for_commission_received = session['ranking_for_commission_received'], frequent_customer_email = session['frequent_customer_email'], 
                frequent_customer_name = session['frequent_customer_name'])
            else:
                return render_template('airline_staff_home_admin_operator.html', error3 = 'No booking agents sold the ticket from your airline in that time period.',
                my_flight = session['my_flight'], airline_name = airline_name, username = username, 
                ranking_last_3_month = session['ranking_last_3_month'], ranking_last_year = session['ranking_last_year'], 
                ranking_for_commission_received = session['ranking_for_commission_received'], frequent_customer_email = session['frequent_customer_email'], 
                frequent_customer_name = session['frequent_customer_name'])
    else:
        return render_template('airline_staff_home_admin_operator.html', error3 = 'Please give an input.',
            my_flight = session['my_flight'], airline_name = airline_name, username = username, 
            ranking_last_3_month = session['ranking_last_3_month'], ranking_last_year = session['ranking_last_year'], 
            ranking_for_commission_received = session['ranking_for_commission_received'], frequent_customer_email = session['frequent_customer_email'], 
            frequent_customer_name = session['frequent_customer_name'])


@app.route('/airline_staff_home_admin_operator/frequent_custormer', methods=["GET", "POST"])
def frequent_customer():
    username = session['username']
    airline_name = session['airline_name']
    cursor = conn.cursor()

    if request.form['customer_email']:
        customer_email = request.form['customer_email']
    if(customer_email):
        query = "select * from (Flight natural join Ticket) natural join Customer where customer_email = '{}' and airline_name = '{}'"
        cursor.execute(query.format(customer_email, airline_name))
        data = cursor.fetchall()
        cursor.close()
        if(data):
            return render_template('Airline_staff_home_admin_operator.html', search_customer = data,
            my_flight = session['my_flight'], airline_name = airline_name, username = username, 
            ranking_last_3_month = session['ranking_last_3_month'], ranking_last_year = session['ranking_last_year'], 
            ranking_for_commission_received = session['ranking_for_commission_received'], frequent_customer_email = session['frequent_customer_email'], 
            frequent_customer_name = session['frequent_customer_name'])
        else:
            return render_template('Airline_staff_home_admin_operator.html', error5 = 'The customer email you input has not take any of the flights from your airline.',
            my_flight = session['my_flight'], airline_name = airline_name, username = username, 
            ranking_last_3_month = session['ranking_last_3_month'], ranking_last_year = session['ranking_last_year'], 
            ranking_for_commission_received = session['ranking_for_commission_received'], frequent_customer_email = session['frequent_customer_email'], 
            frequent_customer_name = session['frequent_customer_name'])
    else:
        return render_template('Airline_staff_home_admin_operator.html',error5 = 'Please enter the customer email first. Please try again.',my_flight = session['my_flight'], airline_name = airline_name, username = username, 
            ranking_last_3_month = session['ranking_last_3_month'], ranking_last_year = session['ranking_last_year'], 
            ranking_for_commission_received = session['ranking_for_commission_received'], frequent_customer_email = session['frequent_customer_email'], 
            frequent_customer_name = session['frequent_customer_name'])


@app.route("/airline_staff_home_admin_operator/grant_new_permissions")
def grant_new_permissions():
    username = session['username']
    airline_name = session['airline_name']
    cursor = conn.cursor()

    query = "SELECT * FROM Permission natural join Airline_Staff where airline_name = '{}'"
    cursor.execute(query.format(airline_name))
    data = cursor.fetchall()
    print(data)
    session['permission_table'] = data
    query_staff = "select staff_user_name from Airline_Staff where airline_name = '{}'"
    cursor.execute(query_staff.format(airline_name))
    data_staff = cursor.fetchall()
    session['staff_table'] = data_staff
    cursor.close()
    return render_template('grant_new_permission_admin_operator.html', permission_table = data, staff_table = data_staff, username = username)

@app.route("/airline_staff_home_admin_operator/grant_new_permissions/action", methods=["GET", "POST"])
def grant_new_permission_action():
    username = session['username']
    airline_name = session['airline_name']
    cursor = conn.cursor()
    query_staff = "select staff_user_name from Airline_Staff where airline_name = '{}'"
    cursor.execute(query_staff.format(airline_name))
    data_staff = cursor.fetchall()
    staff_list = []
    for element in data_staff:
        staff_list.append(element['staff_user_name'])


    num = 0
    if request.form['staff_user_name']:
        staff_user_name = request.form['stuff_user_name']
        num += 1
    if request.form['permission_name']:
        permission_name = request.form['permission_name']
        num += 1
    if num == 2:
        if staff_user_name not in staff_list:
            return render_template('grant_new_permission_admin_operator.html', username = username, permission_table = session['permission_table'], staff_table = session['staff_table'],  error = 'Your input is not valid, please try again.')
        if permission_name not in ['Admin', 'Operator']:
            return render_template('grant_new_permission_admin_operator.html', username = username, permission_table = session['permission_table'], staff_table = session['staff_table'] , error = 'You can only input either Admin or Operator in permission_name, please try again.')
        for element in session['permission_table']:
            if element[staff_user_name] == permission_name:
                return render_template('grant_new_permission_admin_operator.html', username = username, permission_table = session['permission_table'], staff_table = session['staff_table'], error = 'The staff has already got the permission, please try again.')
        query = "insert Permission values('{}', '{}')"
        query.execute(query.format(staff_user_name, permission_name))
        conn.commit()

        query = "SELECT * FROM Permission natural join Airline_Staff where airline_name = '{}'"
        cursor.execute(query.format(airline_name))
        data = cursor.fetchall()
        print(data)
        session['permission_table'] = data
        cursor.close()
        return render_template('grant_new_permission_admin_operator.html', username = username, permission_table = session['permission_table'], staff_table = session['staff_table'])
    else:
        return render_template('grant_new_permission_admin_operator.html', username = username, permission_table = session['permission_table'], staff_table = session['staff_table'], error = 'Please input all the information. Please try again.')

@app.route("/airline_staff_home_admin_operator/add_new_booking_agents")
def add_new_booking_agents():
    username = session['username']
    airline_name = session['airline_name']
    cursor = conn.cursor()

    query = "SELECT * FROM Booking_Agent_Work_For natural join Booking_Agent where airline_name = '{}'"
    cursor.execute(query.format(airline_name))
    data = cursor.fetchall()
    session['booking_agent_table'] = data
    return render_template('add_new_booking_agents_admin_operator.html', username = username, search_booking_agent = session['booking_agent_table'])


@app.route("/airline_staff_home_admin_operator/add_new_booking_agents/action", methods=["GET", "POST"])
def add_new_booking_agents_action():
    username = session['username']
    airline_name = session['airline_name']
    cursor = conn.cursor()
    query_booking_agents = 'select * from Booking_Agent'
    cursor.execute(query_booking_agents)
    data_booking_agents = cursor.fetchall()
    booking_agent_list = []
    for element in data_booking_agents:
        booking_agent_list.append(element['booking_agent_email'])
    print(booking_agent_list)
    
    my_booking_agent_list = []
    for element in session['booking_agent_table']:
        my_booking_agent_list.append(element['booking_agent_email'])
    
    if request.form['booking_agent_email']:
        booking_agent_email = request.form['booking_agent_email']

    if(booking_agent_email):
        if booking_agent_email not in booking_agent_list:
            return render_template('add_new_booking_agents_admin_operator.html', username = username, search_booking_agent = session['booking_agent_table'], error = 'The booking agent email you add is not vaild. Please try again.')
        if booking_agent_email in my_booking_agent_list:
            return render_template('add_new_booking_agents_admin_operator.html', username = username, search_booking_agent = session['booking_agent_table'], error = 'The booking agent email you add is already worked for your airline. Please try again.')
        query = "insert Booking_Agent_Work_For values('{}', '{}')"
        cursor.execute(query.format(booking_agent_email, airline_name))
        conn.commit()
        
        query = "SELECT * FROM Booking_Agent_Work_For natural join Booking_Agent where airline_name = '{}'"
        cursor.execute(query.format(airline_name))
        data = cursor.fetchall()
        session['booking_agent_table'] = data
        cursor.close()
        return render_template('add_new_booking_agents_admin_operator.html', username = username, search_booking_agent = session['booking_agent_table'])
    else:
        return render_template('add_new_booking_agents_admin_operator.html', username = username, search_booking_agent = session['booking_agent_table'], error = 'Please input all the information. Please try again.')

























#airline_staff_home_admin
@app.route('/airline_staff_home_admin')
def airline_staff_home_admin():
    username = session['username']
    cursor = conn.cursor()
    query_airline = "select airline_name FROM Airline_Staff where staff_user_name = '{}'"
    cursor.execute(query_airline.format(username))
    airline_name = cursor.fetchall()[0]['airline_name']

    end_date = datetime.date.today() + relativedelta(days=+30)
    begin_date = datetime.date.today()
    begin_date = datetime.datetime(begin_date.year, begin_date.month, begin_date.day, 0, 0, 0)
    end_date = datetime.datetime(end_date.year, end_date.month, end_date.day, 0, 0, 0)

    begin_date_3_month = datetime.date.today() + relativedelta(months=-3)
    end_date_3_month = datetime.date.today()
    begin_date_3_month = datetime.datetime(begin_date_3_month.year, begin_date_3_month.month, begin_date_3_month.day, 0, 0, 0)
    end_date_3_month = datetime.datetime(end_date_3_month.year, end_date_3_month.month, end_date_3_month.day, 0, 0, 0)

    begin_date_year = datetime.date.today() + relativedelta(months = -12)
    end_date_year = datetime.date.today()
    begin_date_year = datetime.datetime(begin_date_year.year, begin_date_year.month, begin_date_year.day, 0, 0, 0)
    end_date_year = datetime.datetime(end_date_year.year, end_date_year.month, end_date_year.day, 0, 0, 0)

    query = "SELECT * FROM Flight where airline_name = '{}' and status = 'upcoming'\
        and departure_time >= '{}.000' and  departure_time <= '{}.000'"
    cursor.execute(query.format(airline_name, begin_date, end_date))
    data = cursor.fetchall()
    for element in data:
        element['departure_time'] = str(element['departure_time'])
        element['arrival_time'] = str(element['arrival_time'])
    session['my_flight'] = data
    session['airline_name'] = airline_name


    query = "select airport_city, count(airport_city)\
                            from Flight, Airport\
                            where Flight.arrival_airport_name = Airport.airport_name and Flight.departure_time>= '{}' and Flight.departure_time<='{}' \
                            group by airport_city\
                            order by count(airport_city) desc limit 3"
    cursor.execute(query.format(begin_date_3_month, end_date_3_month))
    top_3_destinations_data_3_month = cursor.fetchall()
    num = 1
    for element in top_3_destinations_data_3_month:
        element['rank'] = num
        num += 1
    cursor.execute(query.format(begin_date_year, end_date_year))
    top_3_destinations_data_year = cursor.fetchall()
    num = 1
    for element in top_3_destinations_data_year:
        element['rank'] = num
        num += 1
    session['ranking_last_3_month'] = top_3_destinations_data_3_month
    session['ranking_last_year'] = top_3_destinations_data_year

    begin_date = datetime.date.today() + relativedelta(months = -12)
    end_date = datetime.date.today()
    begin_date = datetime.datetime(begin_date.year, begin_date.month, begin_date.day, 0, 0, 0)
    end_date = datetime.datetime(end_date.year, end_date.month, end_date.day, 0, 0, 0)

    query = "select booking_agent_id, booking_agent_email, sum(price*0.1) as commission_fee from (Ticket natural join Booking_Agent) natural join Flight where\
        airline_name = '{}' and booking_agent_email is not null and purchase_date >= '{}.000' and purchase_date <= '{}.000' group by booking_agent_id, booking_agent_email order by commission_fee desc limit 5"
    cursor.execute(query.format(airline_name, str(begin_date), str(end_date)))
    data_commission = cursor.fetchall()
    num = 1
    for element in data_commission:
        element['rank'] = num
        num += 1
    session['ranking_for_commission_received'] = data_commission

    query_frequent_customer = "select count(*) as purchase_num, customer_email, customer_name from Ticket natural join Customer where airline_name = '{}' and purchase_date >= '{}.000' and purchase_date <= '{}.000'\
        group by customer_email order by purchase_num desc limit 1"
    cursor.execute(query_frequent_customer.format(airline_name, str(begin_date), str(end_date)))
    data_frequent_customer = cursor.fetchall()
    frequent_customer_name = data_frequent_customer[0]['customer_name']
    frequent_customer_email = data_frequent_customer[0]['customer_email']
    session['frequent_customer_name'] = frequent_customer_name
    session['frequent_customer_email'] = frequent_customer_email
    cursor.close()

    if(data):
        return render_template('Airline_staff_home_admin.html', my_flight = data, airline_name = airline_name, username = username, 
        ranking_last_3_month = session['ranking_last_3_month'], ranking_last_year = session['ranking_last_year'], 
        ranking_for_commission_received = session['ranking_for_commission_received'], frequent_customer_email = session['frequent_customer_email'], 
        frequent_customer_name = session['frequent_customer_name'])
    else:
        return render_template('Airline_staff_home_admin.html', error0 = "Sorry, no flights are found. Please check your input again.", 
        airline_name = airline_name, username = username, ranking_last_3_month = session['ranking_last_3_month'], 
        ranking_last_year = session['ranking_last_year'], ranking_for_commission_received = session['ranking_for_commission_received'], 
        frequent_customer_email = session['frequent_customer_email'], frequent_customer_name = session['frequent_customer_name'])

@app.route("/airline_staff_home_admin/view_my_flight", methods=["GET", "POST"])
def view_my_flight():
    username = session['username']
    cursor = conn.cursor()
    airline_name = session['airline_name']

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
    if request.form['flight_num']:
        flight_num = request.form['flight_num']
        appendix += "and flight_num = '"
        appendix += flight_num
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
        query = "SELECT * FROM Flight where airline_name = '{}'"
    else:
        query = "SELECT * FROM Flight where airline_name = '{}' and"
        query += appendix[3:]
    print(query)
    #cursor used to send queries
    cursor = conn.cursor()
    #executes query	
    cursor.execute(query.format(airline_name))
    #stores the results in a variable
    data = cursor.fetchall()
    for element in data:
        element['departure_time'] = str(element['departure_time'])
        element['arrival_time'] = str(element['arrival_time'])
    session['my_flight'] = data
    cursor.close()
    error = None
    if (data):
        #creates a session for the the user
        #session is a built in
        return render_template('Airline_staff_home_admin.html', my_flight = data, airline_name = airline_name, username = username, 
        ranking_last_3_month = session['ranking_last_3_month'], ranking_last_year = session['ranking_last_year'], 
        ranking_for_commission_received = session['ranking_for_commission_received'], frequent_customer_email = session['frequent_customer_email'], 
        frequent_customer_name = session['frequent_customer_name'])   
    else:
        return render_template('airline_staff_home_admin.html', error0 = "Sorry, no flights are found. Please check your input again.", 
        airline_name = airline_name, username = username, 
        ranking_last_3_month = session['ranking_last_3_month'], ranking_last_year = session['ranking_last_year'], 
        ranking_for_commission_received = session['ranking_for_commission_received'], frequent_customer_email = session['frequent_customer_email'], 
        frequent_customer_name = session['frequent_customer_name'])


@app.route('/airline_staff_home_admin/customer_list_for_flights', methods=["GET", "POST"])
def customer_list_for_flights():
    username = session['username']
    cursor = conn.cursor()
    query_airline = "select airline_name FROM Airline_Staff where staff_user_name = '{}'"
    cursor.execute(query_airline.format(username))
    airline_name = cursor.fetchall()[0]['airline_name']

    if request.form['flight_num']:
        flight_num = request.form['flight_num']
        query =  "SELECT * FROM (Ticket natural join Customer) natural join Flight where flight_num = '{}' and airline_name = '{}'"
        cursor.execute(query.format(flight_num, airline_name))
        customer_list_data = cursor.fetchall()
        session['cutomer_list'] = customer_list_data
        cursor.close()
        if (customer_list_data):
            return render_template('airline_staff_home_admin.html', customer_list = customer_list_data, 
            my_flight = session['my_flight'], airline_name = airline_name, username = username, 
            ranking_last_3_month = session['ranking_last_3_month'], ranking_last_year = session['ranking_last_year'], 
            ranking_for_commission_received = session['ranking_for_commission_received'], frequent_customer_email = session['frequent_customer_email'], 
            frequent_customer_name = session['frequent_customer_name'])
        else:
            return render_template('airline_staff_home_admin.html', error1 = 'Sorry, wrong flight num. Pleas check your input again.',
            my_flight = session['my_flight'], airline_name = airline_name, username = username, 
            ranking_last_3_month = session['ranking_last_3_month'], ranking_last_year = session['ranking_last_year'], 
            ranking_for_commission_received = session['ranking_for_commission_received'], frequent_customer_email = session['frequent_customer_email'], 
            frequent_customer_name = session['frequent_customer_name'])
    else:
        cursor.close()
        return render_template('airline_staff_home_admin.html', error1 = 'Please input a vaild flight number first.',
        my_flight = session['my_flight'], airline_name = airline_name, username = username, 
        ranking_last_3_month = session['ranking_last_3_month'], ranking_last_year = session['ranking_last_year'], 
        ranking_for_commission_received = session['ranking_for_commission_received'], frequent_customer_email = session['frequent_customer_email'], 
        frequent_customer_name = session['frequent_customer_name'])



@app.route("/airline_staff_home_admin/create_new_flight")
def create_new_flight():
    username = session['username']
    airline_name = session['airline_name']
    cursor = conn.cursor()

    end_date = datetime.date.today() + relativedelta(days=+30)
    begin_date = datetime.date.today()
    begin_date = datetime.datetime(begin_date.year, begin_date.month, begin_date.day, 0, 0, 0)
    end_date = datetime.datetime(end_date.year, end_date.month, end_date.day, 0, 0, 0)

    query = "SELECT * FROM Flight where airline_name = '{}' and status = 'upcoming'\
        and departure_time >= '{}.000' and  departure_time <= '{}.000'"
    cursor.execute(query.format(airline_name, begin_date, end_date))
    data = cursor.fetchall()
    for element in data:
        element['departure_time'] = str(element['departure_time'])
        element['arrival_time'] = str(element['arrival_time'])
    session['create_flight_table'] = data
    cursor.close()

    if(data):
        return render_template('create_new_flight_admin.html', create_flight_table = session['create_flight_table'], username = username)
    else:
        return render_template('create_new_flight_admin.html', username = username, error0 = "Your airline doesn't have any upcoming flights in next 30 days. You can add one below.")

@app.route("/airline_staff_home_admin/create_new_flight/action", methods=["GET", "POST"])
def create_new_flight_action():
    username = session['username']
    cursor = conn.cursor()
    query_airline = "select airline_name FROM Airline_Staff where staff_user_name = '{}'"
    cursor.execute(query_airline.format(username))
    airline_name = cursor.fetchall()[0]['airline_name']

    query_airport = "select airport_name from Airport"
    cursor.execute(query_airport)
    airport_name_list = cursor.fetchall()
    airport_list = []
    for airport_element in airport_name_list:
        airport_list.append(airport_element['airport_name'])

    query_airplane_id = "select airplane_id from Airplane where airline_name = '{}'"
    cursor.execute(query_airplane_id.format(airline_name))
    airplane_id_list = cursor.fetchall()
    airplane_list = []
    for airplane_element in airplane_id_list:
        airplane_list.append(airplane_element['airplane_id'])

    num = 0
    if request.form['airline_name']:
        airline_name_input = request.form['airline_name']
        num += 1
    if request.form['flight_num']:
        flight_num = request.form['flight_num']
        num += 1
    if request.form['departure_airport_name']:
        departure_airport_name = request.form['departure_airport_name']
        num += 1
    if request.form['arrival_airport_name']:
        arrival_airport_name = request.form['arrival_airport_name']
        num += 1
    if request.form['departure_time']:
        departure_time = request.form['departure_time']
        d_date = departure_time[0:10]
        d_time = departure_time[11:]
        departure_time = d_date + ' ' + d_time + ':00'
        num += 1
    if request.form['arrival_time']:
        arrival_time = request.form['arrival_time']
        a_date = arrival_time[0:10]
        a_time = arrival_time[11:]
        arrival_time = a_date + ' ' + a_time + ':00'
        num += 1
    if request.form['price']:
        price = request.form['price']
        num += 1
    if request.form['status']:
        status = request.form['status']
        num += 1
    if request.form['airplane_id']:
        airplane_id = request.form['airplane_id']
        num += 1
    if num == 9:
        if airline_name_input != airline_name:
            return render_template('create_new_flight_admin.html', username = username, create_flight_table = session['create_flight_table'], error = 'You can only add new flight for your airline. Please try again.')
        if (departure_airport_name not in airport_list) or (arrival_airport_name not in airport_list):
            return render_template('create_new_flight_admin.html', username = username, create_flight_table = session['create_flight_table'], error = 'Airport you input does not exist, please try again.')
        else:
            if departure_airport_name == arrival_airport_name:
                return render_template('create_new_flight_admin.html', username = username, create_flight_table = session['create_flight_table'], error = 'Arrival and Departure Airport can not be the same. Please try again.')
        if airplane_id not in airplane_list:
            return render_template('create_new_flight_admin.html', username = username, create_flight_table = session['create_flight_table'], error = 'Airplane you input does not exist, please try again.')
        if status not in ['upcoming', 'delayed', 'in-progress']:
            return render_template('create_new_flight_admin.html', username = username, create_flight_table = session['create_flight_table'], error = 'Status should only be in-progress/upcoming/delayed. Please try again.')       
        query = "insert into Flight values ('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')"
        cursor.execute(query.format(airline_name, flight_num, departure_time, arrival_time, price,
        status, arrival_airport_name, departure_airport_name, airplane_id))
        conn.commit()

        end_date = datetime.date.today() + relativedelta(days=+30)
        begin_date = datetime.date.today()
        begin_date = datetime.datetime(begin_date.year, begin_date.month, begin_date.day, 0, 0, 0)
        end_date = datetime.datetime(end_date.year, end_date.month, end_date.day, 0, 0, 0)

        query = "SELECT * FROM Flight where airline_name = '{}' and status = 'upcoming'\
        and departure_time >= '{}.000' and  departure_time <= '{}.000'"
        cursor.execute(query.format(airline_name, begin_date, end_date))
        data = cursor.fetchall()
        for element in data:
            element['departure_time'] = str(element['departure_time'])
            element['arrival_time'] = str(element['arrival_time'])
        session['create_flight_table'] = data
        cursor.close()
        return render_template('create_new_flight_admin.html', username = username, create_flight_table = session['create_flight_table'])
    else:
        return render_template('create_new_flight_admin.html', username = username, error = 'Please add all the information. Please try again.', create_flight_table = session['create_flihgt_table'])


@app.route("/airline_staff_home_admin/add_airplane")
def add_airplane():
    username = session['username']
    airline_name = session['airline_name']
    cursor = conn.cursor()

    query = "SELECT * FROM Airplane where airline_name = '{}'"
    cursor.execute(query.format(airline_name))
    data = cursor.fetchall()
    session['my_airplane'] = data
    cursor.close()

    if(data):
        return render_template('add_airplane_admin.html', my_airplane = session['my_airplane'], username = username)
    else:
        return render_template('add_airplane_admin.html', username = username, error0 = "Your airline doesn't have any airplane. You can add one below.")

@app.route("/airline_staff_home_admin/add_airplane/action", methods=["GET", "POST"])
def add_airplane_action():
    username = session['username']
    airline_name = session['airline_name']
    cursor = conn.cursor()
    query_airplane_id = "select airplane_id from Airplane where airline_name = '{}'"
    cursor.execute(query_airplane_id.format(airline_name))
    airplane_id_list = cursor.fetchall()
    airplane_list = []
    for airplane_element in airplane_id_list:
        airplane_list.append(airplane_element['airplane_id'])

    num = 0
    if request.form['airline_name']:
        airline_name_input = request.form['airline_name']
        num += 1
    if request.form['airplane_id']:
        airplane_id = request.form['airplane_id']
        num += 1
    if request.form['seats']:
        seats = request.form['seats']
        num += 1

    if num == 3:
        if airline_name_input != airline_name:
            return render_template('add_airplane_admin.html', username = username, my_airplane = session['my_airplane'], error = 'You can only add new airplane for your airline. Please try again.')
        if airplane_id in airplane_list:
            return render_template('add_airplane_admin.html', username = username, my_airplane = session['my_airplane'], error = 'The airplane id is used in your airline. Please try again.')
        query = "insert into Airplane values ('{}', '{}', '{}')"
        cursor.execute(query.format(airplane_id ,airline_name, seats))
        print(query)
        conn.commit()

        query = "SELECT * FROM Airplane where airline_name = '{}'"
        cursor.execute(query.format(airline_name))
        data = cursor.fetchall()
        session['my_airplane'] = data
        cursor.close()
        return render_template('add_airplane_admin.html', username = username, my_airplane = session['my_airplane'])
    else:
        return render_template('add_airplane_admin.html', username = username, error = 'Please add all the information. Please try again.', my_airplane = session['my_airplane'])

@app.route("/airline_staff_home_admin/add_airport")
def add_airport():
    username = session['username']
    airline_name = session['airline_name']
    cursor = conn.cursor()
    query = "select * from Airport"
    cursor.execute(query)
    data = cursor.fetchall()
    session['world_airport'] = data

    query_my_airport = "select * from Airport_for_Airline where airline_name = '{}'"
    cursor.execute(query_my_airport.format(airline_name))
    data_my_airport = cursor.fetchall()
    session['my_airport'] = data_my_airport
    cursor.close()

    if(data_my_airport):    
        return render_template('add_airport_admin.html', world_airport = session['world_airport'], my_airport = session['my_airport'], username = username)
    else:
        return render_template('add_airport_admin.html', world_airport = session['world_airport'], error0 = 'There is no airport for your airline now. You can add one below.', username = username)

@app.route("/airline_staff_home_admin/add_airport/my_action", methods=["GET", "POST"])
def add_airport_my_action():
    username = session['username']
    airline_name = session['airline_name']
    cursor = conn.cursor()
    query = "select airport_name from Airport"
    cursor.execute(query)
    world_airport_dict = cursor.fetchall()
    world_airport_list = []
    for element in world_airport_dict:
        world_airport_list.append(element['airport_name'])

    query_world_airport = "select * from Airport"
    cursor.execute(query_world_airport)
    data_world_airport = cursor.fetchall()

    query_my_airport = "select * from Airport_for_Airline where airline_name = '{}'"
    cursor.execute(query_my_airport.format(airline_name))
    data_my_airport = cursor.fetchall()
    my_airport_list = []
    for element in data_my_airport:
        my_airport_list.append(element['airport_name'])

    num = 0
    if request.form['airport_name']:
        airport_name_input = request.form['airport_name']
        num += 1
    if request.form['airline_name']:
        airline_name_input = request.form['airline_name']
        num += 1
    
    if num == 2:
        if airline_name_input != airline_name:
             return render_template('add_airport_admin.html', world_airport = session['world_airport'], my_airport = session['my_airport'], username = username, error2 = 'You can only add airport to your airline system. Please try again.') 
        if airport_name_input not in world_airport_list:
            return render_template('add_airport_admin.html', world_airport = session['world_airport'], my_airport = session['my_airport'], username = username, error2 = 'The airport you input is not vaild. Please try again.') 
        if airport_name_input in my_airport_list:
            return render_template('add_airport_admin.html', world_airport = session['world_airport'], my_airport = session['my_airport'], username = username, error2 = 'The airport you input is already in the system. Please try again.') 
        else:
            query = "insert into Airport_for_Airline values ('{}', '{}')"
            cursor.execute(query.format(airport_name_input, airline_name_input))
            conn.commit()

            query_my_airport = "select * from Airport_for_Airline where airline_name = '{}'"
            cursor.execute(query_my_airport.format(airline_name))
            data_my_airport = cursor.fetchall()
            session['my_airport'] = data_my_airport
            cursor.close()

            return render_template('add_airport_admin.html', world_airport = session['world_airport'], my_airport = session['my_airport'], username = username)
    else:
         return render_template('add_airport_admin.html', world_airport = session['world_airport'], my_airport = session['my_airport'], username = username, error2 = 'Please input all the information.') 


@app.route('/airline_staff_home_admin/top_5_booking_agent_by_month', methods=["GET", "POST"])
def top_5_booking_agent_by_month():
    username = session['username']
    airline_name = session['airline_name']

    if request.form['month']:
        month = request.form['month']

    if(month):
        today = datetime.date.today()
        today = str(datetime.datetime(today.year, today.month, today.day, 0, 0, 0))
        if str(month) >= today[0:7]:
            return render_template('airline_staff_home_admin.html', error2 = 'Only avaiable for past month. Please try again.',
            my_flight = session['my_flight'], airline_name = airline_name, username = username, 
            ranking_last_3_month = session['ranking_last_3_month'], ranking_last_year = session['ranking_last_year'], 
            ranking_for_commission_received = session['ranking_for_commission_received'], frequent_customer_email = session['frequent_customer_email'], 
            frequent_customer_name = session['frequent_customer_name'])
        else:
            begin_month = datetime.datetime(int(month[0:4]), int(month[5:7]), 1, 0, 0, 0)
            end_month = begin_month + relativedelta(months=+1)

            cursor = conn.cursor()
            query = "select booking_agent_id, booking_agent_email, count(ticket_id) as num_of_ticket FROM Ticket natural join Booking_Agent where airline_name = '{}' and purchase_date >= '{}.000' and purchase_date <= '{}.000' and booking_agent_email is not null\
                group by booking_agent_id, booking_agent_email order by count(ticket_id) desc limit 5"
            cursor.execute(query.format(airline_name, str(begin_month), str(end_month)))
            data = cursor.fetchall()
            num = 1
            for element in data:
                element['rank'] = num
                num += 1
            session['ranking_for_month'] = data
            cursor.close()
            if(data):
                return render_template('airline_staff_home_admin.html', ranking_for_month = data,
                my_flight = session['my_flight'], airline_name = airline_name, username = username, 
                ranking_last_3_month = session['ranking_last_3_month'], ranking_last_year = session['ranking_last_year'], 
                ranking_for_commission_received = session['ranking_for_commission_received'], frequent_customer_email = session['frequent_customer_email'], 
                frequent_customer_name = session['frequent_customer_name'])         
            else:
                return render_template('airline_staff_home_admin.html', error2 = 'No booking agents sold the ticket from your airline in that time period.', 
                my_flight = session['my_flight'], airline_name = airline_name, username = username, 
                ranking_last_3_month = session['ranking_last_3_month'], ranking_last_year = session['ranking_last_year'], 
                ranking_for_commission_received = session['ranking_for_commission_received'], frequent_customer_email = session['frequent_customer_email'], 
                frequent_customer_name = session['frequent_customer_name'])
    else:
        return render_template('airline_staff_home_admin.html', error2 = 'Please give an input.', 
            my_flight = session['my_flight'], airline_name = airline_name, username = username, 
            ranking_last_3_month = session['ranking_last_3_month'], ranking_last_year = session['ranking_last_year'], 
            ranking_for_commission_received = session['ranking_for_commission_received'], frequent_customer_email = session['frequent_customer_email'], 
            frequent_customer_name = session['frequent_customer_name'])


@app.route('/airline_staff_home_admin/top_5_booking_agent_by_year', methods=["GET", "POST"])
def top_5_booking_agent_by_year():
    username = session['username']
    airline_name = session['airline_name']

    if request.form['year']:
        year = request.form['year']
        print(year)
    if(year):
        today = datetime.date.today()
        today = str(datetime.datetime(today.year, today.month, today.day, 0, 0, 0))
        if str(year) > today[0:4]:
            return render_template('airline_staff_home_admin.html', error3 = 'Only avaiable for past year. Please try again.',
            my_flight = session['my_flight'], airline_name = airline_name, username = username, 
            ranking_last_3_month = session['ranking_last_3_month'], ranking_last_year = session['ranking_last_year'], 
            ranking_for_commission_received = session['ranking_for_commission_received'], frequent_customer_email = session['frequent_customer_email'], 
            frequent_customer_name = session['frequent_customer_name'])
        else:
            begin_year = datetime.datetime(int(year), 1, 1, 0, 0, 0)
            end_year = begin_year + relativedelta(months=+12)

            cursor = conn.cursor()
            query = "select booking_agent_id, booking_agent_email, count(ticket_id) as num_of_ticket FROM Ticket natural join Booking_Agent where airline_name = '{}' and purchase_date >= '{}.000' and purchase_date <= '{}.000' and booking_agent_email is not null\
                group by booking_agent_id, booking_agent_email order by count(ticket_id) desc limit 5"
            cursor.execute(query.format(airline_name, str(begin_year), str(end_year)))
            data = cursor.fetchall()
            num = 1
            for element in data:
                element['rank'] = num
                num += 1
            session['ranking_for_year'] = data
            cursor.close()
            if(data):
                return render_template('airline_staff_home_admin.html', ranking_for_year = data,
                my_flight = session['my_flight'], airline_name = airline_name, username = username, 
                ranking_last_3_month = session['ranking_last_3_month'], ranking_last_year = session['ranking_last_year'], 
                ranking_for_commission_received = session['ranking_for_commission_received'], frequent_customer_email = session['frequent_customer_email'], 
                frequent_customer_name = session['frequent_customer_name'])
            else:
                return render_template('airline_staff_home_admin.html', error3 = 'No booking agents sold the ticket from your airline in that time period.',
                my_flight = session['my_flight'], airline_name = airline_name, username = username, 
                ranking_last_3_month = session['ranking_last_3_month'], ranking_last_year = session['ranking_last_year'], 
                ranking_for_commission_received = session['ranking_for_commission_received'], frequent_customer_email = session['frequent_customer_email'], 
                frequent_customer_name = session['frequent_customer_name'])
    else:
        return render_template('airline_staff_home_admin.html', error3 = 'Please give an input.',
            my_flight = session['my_flight'], airline_name = airline_name, username = username, 
            ranking_last_3_month = session['ranking_last_3_month'], ranking_last_year = session['ranking_last_year'], 
            ranking_for_commission_received = session['ranking_for_commission_received'], frequent_customer_email = session['frequent_customer_email'], 
            frequent_customer_name = session['frequent_customer_name'])


@app.route('/airline_staff_home_admin/frequent_custormer', methods=["GET", "POST"])
def frequent_customer():
    username = session['username']
    airline_name = session['airline_name']
    cursor = conn.cursor()

    if request.form['customer_email']:
        customer_email = request.form['customer_email']
    if(customer_email):
        query = "select * from (Flight natural join Ticket) natural join Customer where customer_email = '{}' and airline_name = '{}'"
        cursor.execute(query.format(customer_email, airline_name))
        data = cursor.fetchall()
        cursor.close()
        if(data):
            return render_template('Airline_staff_home_admin.html', search_customer = data,
            my_flight = session['my_flight'], airline_name = airline_name, username = username, 
            ranking_last_3_month = session['ranking_last_3_month'], ranking_last_year = session['ranking_last_year'], 
            ranking_for_commission_received = session['ranking_for_commission_received'], frequent_customer_email = session['frequent_customer_email'], 
            frequent_customer_name = session['frequent_customer_name'])
        else:
            return render_template('Airline_staff_home_admin.html', error5 = 'The customer email you input has not take any of the flights from your airline.',
            my_flight = session['my_flight'], airline_name = airline_name, username = username, 
            ranking_last_3_month = session['ranking_last_3_month'], ranking_last_year = session['ranking_last_year'], 
            ranking_for_commission_received = session['ranking_for_commission_received'], frequent_customer_email = session['frequent_customer_email'], 
            frequent_customer_name = session['frequent_customer_name'])
    else:
        return render_template('Airline_staff_home_admin.html',error5 = 'Please enter the customer email first. Please try again.',my_flight = session['my_flight'], airline_name = airline_name, username = username, 
            ranking_last_3_month = session['ranking_last_3_month'], ranking_last_year = session['ranking_last_year'], 
            ranking_for_commission_received = session['ranking_for_commission_received'], frequent_customer_email = session['frequent_customer_email'], 
            frequent_customer_name = session['frequent_customer_name'])


@app.route("/airline_staff_home_admin/grant_new_permissions")
def grant_new_permissions():
    username = session['username']
    airline_name = session['airline_name']
    cursor = conn.cursor()

    query = "SELECT * FROM Permission natural join Airline_Staff where airline_name = '{}'"
    cursor.execute(query.format(airline_name))
    data = cursor.fetchall()
    print(data)
    session['permission_table'] = data
    query_staff = "select staff_user_name from Airline_Staff where airline_name = '{}'"
    cursor.execute(query_staff.format(airline_name))
    data_staff = cursor.fetchall()
    session['staff_table'] = data_staff
    cursor.close()
    return render_template('grant_new_permission_admin.html', permission_table = data, staff_table = data_staff, username = username)

@app.route("/airline_staff_home_admin/grant_new_permissions/action", methods=["GET", "POST"])
def grant_new_permission_action():
    username = session['username']
    airline_name = session['airline_name']
    cursor = conn.cursor()
    query_staff = "select staff_user_name from Airline_Staff where airline_name = '{}'"
    cursor.execute(query_staff.format(airline_name))
    data_staff = cursor.fetchall()
    staff_list = []
    for element in data_staff:
        staff_list.append(element['staff_user_name'])


    num = 0
    if request.form['staff_user_name']:
        staff_user_name = request.form['stuff_user_name']
        num += 1
    if request.form['permission_name']:
        permission_name = request.form['permission_name']
        num += 1
    if num == 2:
        if staff_user_name not in staff_list:
            return render_template('grant_new_permission_admin.html', username = username, permission_table = session['permission_table'], staff_table = session['staff_table'],  error = 'Your input is not valid, please try again.')
        if permission_name not in ['Admin', 'Operator']:
            return render_template('grant_new_permission_admin.html', username = username, permission_table = session['permission_table'], staff_table = session['staff_table'] , error = 'You can only input either Admin or Operator in permission_name, please try again.')
        for element in session['permission_table']:
            if element[staff_user_name] == permission_name:
                return render_template('grant_new_permission_admin.html', username = username, permission_table = session['permission_table'], staff_table = session['staff_table'], error = 'The staff has already got the permission, please try again.')
        query = "insert Permission values('{}', '{}')"
        query.execute(query.format(staff_user_name, permission_name))
        conn.commit()

        query = "SELECT * FROM Permission natural join Airline_Staff where airline_name = '{}'"
        cursor.execute(query.format(airline_name))
        data = cursor.fetchall()
        print(data)
        session['permission_table'] = data
        cursor.close()
        return render_template('grant_new_permission_admin.html', username = username, permission_table = session['permission_table'], staff_table = session['staff_table'])
    else:
        return render_template('grant_new_permission_admin.html', username = username, permission_table = session['permission_table'], staff_table = session['staff_table'], error = 'Please input all the information. Please try again.')

@app.route("/airline_staff_home_admin/add_new_booking_agents")
def add_new_booking_agents():
    username = session['username']
    airline_name = session['airline_name']
    cursor = conn.cursor()

    query = "SELECT * FROM Booking_Agent_Work_For natural join Booking_Agent where airline_name = '{}'"
    cursor.execute(query.format(airline_name))
    data = cursor.fetchall()
    session['booking_agent_table'] = data
    return render_template('add_new_booking_agents_admin.html', username = username, search_booking_agent = session['booking_agent_table'])


@app.route("/airline_staff_home_admin/add_new_booking_agents/action", methods=["GET", "POST"])
def add_new_booking_agents_action():
    username = session['username']
    airline_name = session['airline_name']
    cursor = conn.cursor()
    query_booking_agents = 'select * from Booking_Agent'
    cursor.execute(query_booking_agents)
    data_booking_agents = cursor.fetchall()
    booking_agent_list = []
    for element in data_booking_agents:
        booking_agent_list.append(element['booking_agent_email'])
    print(booking_agent_list)
    
    my_booking_agent_list = []
    for element in session['booking_agent_table']:
        my_booking_agent_list.append(element['booking_agent_email'])
    
    if request.form['booking_agent_email']:
        booking_agent_email = request.form['booking_agent_email']

    if(booking_agent_email):
        if booking_agent_email not in booking_agent_list:
            return render_template('add_new_booking_agents_admin.html', username = username, search_booking_agent = session['booking_agent_table'], error = 'The booking agent email you add is not vaild. Please try again.')
        if booking_agent_email in my_booking_agent_list:
            return render_template('add_new_booking_agents_admin.html', username = username, search_booking_agent = session['booking_agent_table'], error = 'The booking agent email you add is already worked for your airline. Please try again.')
        query = "insert Booking_Agent_Work_For values('{}', '{}')"
        cursor.execute(query.format(booking_agent_email, airline_name))
        conn.commit()
        
        query = "SELECT * FROM Booking_Agent_Work_For natural join Booking_Agent where airline_name = '{}'"
        cursor.execute(query.format(airline_name))
        data = cursor.fetchall()
        session['booking_agent_table'] = data
        cursor.close()
        return render_template('add_new_booking_agents_admin.html', username = username, search_booking_agent = session['booking_agent_table'])
    else:
        return render_template('add_new_booking_agents_admin.html', username = username, search_booking_agent = session['booking_agent_table'], error = 'Please input all the information. Please try again.')




















#airline_staff_home_opeartor
@app.route('/airline_staff_home_opeartor')
def airline_staff_home_opeartor():
    username = session['username']
    cursor = conn.cursor()
    query_airline = "select airline_name FROM Airline_Staff where staff_user_name = '{}'"
    cursor.execute(query_airline.format(username))
    airline_name = cursor.fetchall()[0]['airline_name']

    end_date = datetime.date.today() + relativedelta(days=+30)
    begin_date = datetime.date.today()
    begin_date = datetime.datetime(begin_date.year, begin_date.month, begin_date.day, 0, 0, 0)
    end_date = datetime.datetime(end_date.year, end_date.month, end_date.day, 0, 0, 0)

    begin_date_3_month = datetime.date.today() + relativedelta(months=-3)
    end_date_3_month = datetime.date.today()
    begin_date_3_month = datetime.datetime(begin_date_3_month.year, begin_date_3_month.month, begin_date_3_month.day, 0, 0, 0)
    end_date_3_month = datetime.datetime(end_date_3_month.year, end_date_3_month.month, end_date_3_month.day, 0, 0, 0)

    begin_date_year = datetime.date.today() + relativedelta(months = -12)
    end_date_year = datetime.date.today()
    begin_date_year = datetime.datetime(begin_date_year.year, begin_date_year.month, begin_date_year.day, 0, 0, 0)
    end_date_year = datetime.datetime(end_date_year.year, end_date_year.month, end_date_year.day, 0, 0, 0)

    query = "SELECT * FROM Flight where airline_name = '{}' and status = 'upcoming'\
        and departure_time >= '{}.000' and  departure_time <= '{}.000'"
    cursor.execute(query.format(airline_name, begin_date, end_date))
    data = cursor.fetchall()
    for element in data:
        element['departure_time'] = str(element['departure_time'])
        element['arrival_time'] = str(element['arrival_time'])
    session['my_flight'] = data
    session['airline_name'] = airline_name


    query = "select airport_city, count(airport_city)\
                            from Flight, Airport\
                            where Flight.arrival_airport_name = Airport.airport_name and Flight.departure_time>= '{}' and Flight.departure_time<='{}' \
                            group by airport_city\
                            order by count(airport_city) desc limit 3"
    cursor.execute(query.format(begin_date_3_month, end_date_3_month))
    top_3_destinations_data_3_month = cursor.fetchall()
    num = 1
    for element in top_3_destinations_data_3_month:
        element['rank'] = num
        num += 1
    cursor.execute(query.format(begin_date_year, end_date_year))
    top_3_destinations_data_year = cursor.fetchall()
    num = 1
    for element in top_3_destinations_data_year:
        element['rank'] = num
        num += 1
    session['ranking_last_3_month'] = top_3_destinations_data_3_month
    session['ranking_last_year'] = top_3_destinations_data_year

    begin_date = datetime.date.today() + relativedelta(months = -12)
    end_date = datetime.date.today()
    begin_date = datetime.datetime(begin_date.year, begin_date.month, begin_date.day, 0, 0, 0)
    end_date = datetime.datetime(end_date.year, end_date.month, end_date.day, 0, 0, 0)

    query = "select booking_agent_id, booking_agent_email, sum(price*0.1) as commission_fee from (Ticket natural join Booking_Agent) natural join Flight where\
        airline_name = '{}' and booking_agent_email is not null and purchase_date >= '{}.000' and purchase_date <= '{}.000' group by booking_agent_id, booking_agent_email order by commission_fee desc limit 5"
    cursor.execute(query.format(airline_name, str(begin_date), str(end_date)))
    data_commission = cursor.fetchall()
    num = 1
    for element in data_commission:
        element['rank'] = num
        num += 1
    session['ranking_for_commission_received'] = data_commission

    query_frequent_customer = "select count(*) as purchase_num, customer_email, customer_name from Ticket natural join Customer where airline_name = '{}' and purchase_date >= '{}.000' and purchase_date <= '{}.000'\
        group by customer_email order by purchase_num desc limit 1"
    cursor.execute(query_frequent_customer.format(airline_name, str(begin_date), str(end_date)))
    data_frequent_customer = cursor.fetchall()
    frequent_customer_name = data_frequent_customer[0]['customer_name']
    frequent_customer_email = data_frequent_customer[0]['customer_email']
    session['frequent_customer_name'] = frequent_customer_name
    session['frequent_customer_email'] = frequent_customer_email
    cursor.close()

    if(data):
        return render_template('Airline_staff_home_opeartor.html', my_flight = data, airline_name = airline_name, username = username, 
        ranking_last_3_month = session['ranking_last_3_month'], ranking_last_year = session['ranking_last_year'], 
        ranking_for_commission_received = session['ranking_for_commission_received'], frequent_customer_email = session['frequent_customer_email'], 
        frequent_customer_name = session['frequent_customer_name'])
    else:
        return render_template('Airline_staff_home_opeartor.html', error0 = "Sorry, no flights are found. Please check your input again.", 
        airline_name = airline_name, username = username, ranking_last_3_month = session['ranking_last_3_month'], 
        ranking_last_year = session['ranking_last_year'], ranking_for_commission_received = session['ranking_for_commission_received'], 
        frequent_customer_email = session['frequent_customer_email'], frequent_customer_name = session['frequent_customer_name'])

@app.route("/airline_staff_home_opeartor/view_my_flight", methods=["GET", "POST"])
def view_my_flight():
    username = session['username']
    cursor = conn.cursor()
    airline_name = session['airline_name']

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
    if request.form['flight_num']:
        flight_num = request.form['flight_num']
        appendix += "and flight_num = '"
        appendix += flight_num
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
        query = "SELECT * FROM Flight where airline_name = '{}'"
    else:
        query = "SELECT * FROM Flight where airline_name = '{}' and"
        query += appendix[3:]
    print(query)
    #cursor used to send queries
    cursor = conn.cursor()
    #executes query	
    cursor.execute(query.format(airline_name))
    #stores the results in a variable
    data = cursor.fetchall()
    for element in data:
        element['departure_time'] = str(element['departure_time'])
        element['arrival_time'] = str(element['arrival_time'])
    session['my_flight'] = data
    cursor.close()
    error = None
    if (data):
        #creates a session for the the user
        #session is a built in
        return render_template('Airline_staff_home_opeartor.html', my_flight = data, airline_name = airline_name, username = username, 
        ranking_last_3_month = session['ranking_last_3_month'], ranking_last_year = session['ranking_last_year'], 
        ranking_for_commission_received = session['ranking_for_commission_received'], frequent_customer_email = session['frequent_customer_email'], 
        frequent_customer_name = session['frequent_customer_name'])   
    else:
        return render_template('airline_staff_home_opeartor.html', error0 = "Sorry, no flights are found. Please check your input again.", 
        airline_name = airline_name, username = username, 
        ranking_last_3_month = session['ranking_last_3_month'], ranking_last_year = session['ranking_last_year'], 
        ranking_for_commission_received = session['ranking_for_commission_received'], frequent_customer_email = session['frequent_customer_email'], 
        frequent_customer_name = session['frequent_customer_name'])


@app.route('/airline_staff_home_opeartor/customer_list_for_flights', methods=["GET", "POST"])
def customer_list_for_flights():
    username = session['username']
    cursor = conn.cursor()
    query_airline = "select airline_name FROM Airline_Staff where staff_user_name = '{}'"
    cursor.execute(query_airline.format(username))
    airline_name = cursor.fetchall()[0]['airline_name']

    if request.form['flight_num']:
        flight_num = request.form['flight_num']
        query =  "SELECT * FROM (Ticket natural join Customer) natural join Flight where flight_num = '{}' and airline_name = '{}'"
        cursor.execute(query.format(flight_num, airline_name))
        customer_list_data = cursor.fetchall()
        session['cutomer_list'] = customer_list_data
        cursor.close()
        if (customer_list_data):
            return render_template('airline_staff_home_opeartor.html', customer_list = customer_list_data, 
            my_flight = session['my_flight'], airline_name = airline_name, username = username, 
            ranking_last_3_month = session['ranking_last_3_month'], ranking_last_year = session['ranking_last_year'], 
            ranking_for_commission_received = session['ranking_for_commission_received'], frequent_customer_email = session['frequent_customer_email'], 
            frequent_customer_name = session['frequent_customer_name'])
        else:
            return render_template('airline_staff_home_opeartor.html', error1 = 'Sorry, wrong flight num. Pleas check your input again.',
            my_flight = session['my_flight'], airline_name = airline_name, username = username, 
            ranking_last_3_month = session['ranking_last_3_month'], ranking_last_year = session['ranking_last_year'], 
            ranking_for_commission_received = session['ranking_for_commission_received'], frequent_customer_email = session['frequent_customer_email'], 
            frequent_customer_name = session['frequent_customer_name'])
    else:
        cursor.close()
        return render_template('airline_staff_home_opeartor.html', error1 = 'Please input a vaild flight number first.',
        my_flight = session['my_flight'], airline_name = airline_name, username = username, 
        ranking_last_3_month = session['ranking_last_3_month'], ranking_last_year = session['ranking_last_year'], 
        ranking_for_commission_received = session['ranking_for_commission_received'], frequent_customer_email = session['frequent_customer_email'], 
        frequent_customer_name = session['frequent_customer_name'])



@app.route("/airline_staff_home_opeartor/create_new_flight")
def create_new_flight():
    username = session['username']
    airline_name = session['airline_name']
    cursor = conn.cursor()

    end_date = datetime.date.today() + relativedelta(days=+30)
    begin_date = datetime.date.today()
    begin_date = datetime.datetime(begin_date.year, begin_date.month, begin_date.day, 0, 0, 0)
    end_date = datetime.datetime(end_date.year, end_date.month, end_date.day, 0, 0, 0)

    query = "SELECT * FROM Flight where airline_name = '{}' and status = 'upcoming'\
        and departure_time >= '{}.000' and  departure_time <= '{}.000'"
    cursor.execute(query.format(airline_name, begin_date, end_date))
    data = cursor.fetchall()
    for element in data:
        element['departure_time'] = str(element['departure_time'])
        element['arrival_time'] = str(element['arrival_time'])
    session['create_flight_table'] = data
    cursor.close()

    if(data):
        return render_template('create_new_flight_opeartor.html', create_flight_table = session['create_flight_table'], username = username)
    else:
        return render_template('create_new_flight_opeartor.html', username = username, error0 = "Your airline doesn't have any upcoming flights in next 30 days. You can add one below.")

@app.route("/airline_staff_home_opeartor/create_new_flight/action", methods=["GET", "POST"])
def create_new_flight_action():
    username = session['username']
    cursor = conn.cursor()
    query_airline = "select airline_name FROM Airline_Staff where staff_user_name = '{}'"
    cursor.execute(query_airline.format(username))
    airline_name = cursor.fetchall()[0]['airline_name']

    query_airport = "select airport_name from Airport"
    cursor.execute(query_airport)
    airport_name_list = cursor.fetchall()
    airport_list = []
    for airport_element in airport_name_list:
        airport_list.append(airport_element['airport_name'])

    query_airplane_id = "select airplane_id from Airplane where airline_name = '{}'"
    cursor.execute(query_airplane_id.format(airline_name))
    airplane_id_list = cursor.fetchall()
    airplane_list = []
    for airplane_element in airplane_id_list:
        airplane_list.append(airplane_element['airplane_id'])

    num = 0
    if request.form['airline_name']:
        airline_name_input = request.form['airline_name']
        num += 1
    if request.form['flight_num']:
        flight_num = request.form['flight_num']
        num += 1
    if request.form['departure_airport_name']:
        departure_airport_name = request.form['departure_airport_name']
        num += 1
    if request.form['arrival_airport_name']:
        arrival_airport_name = request.form['arrival_airport_name']
        num += 1
    if request.form['departure_time']:
        departure_time = request.form['departure_time']
        d_date = departure_time[0:10]
        d_time = departure_time[11:]
        departure_time = d_date + ' ' + d_time + ':00'
        num += 1
    if request.form['arrival_time']:
        arrival_time = request.form['arrival_time']
        a_date = arrival_time[0:10]
        a_time = arrival_time[11:]
        arrival_time = a_date + ' ' + a_time + ':00'
        num += 1
    if request.form['price']:
        price = request.form['price']
        num += 1
    if request.form['status']:
        status = request.form['status']
        num += 1
    if request.form['airplane_id']:
        airplane_id = request.form['airplane_id']
        num += 1
    if num == 9:
        if airline_name_input != airline_name:
            return render_template('create_new_flight_opeartor.html', username = username, create_flight_table = session['create_flight_table'], error = 'You can only add new flight for your airline. Please try again.')
        if (departure_airport_name not in airport_list) or (arrival_airport_name not in airport_list):
            return render_template('create_new_flight_opeartor.html', username = username, create_flight_table = session['create_flight_table'], error = 'Airport you input does not exist, please try again.')
        else:
            if departure_airport_name == arrival_airport_name:
                return render_template('create_new_flight_opeartor.html', username = username, create_flight_table = session['create_flight_table'], error = 'Arrival and Departure Airport can not be the same. Please try again.')
        if airplane_id not in airplane_list:
            return render_template('create_new_flight_opeartor.html', username = username, create_flight_table = session['create_flight_table'], error = 'Airplane you input does not exist, please try again.')
        if status not in ['upcoming', 'delayed', 'in-progress']:
            return render_template('create_new_flight_opeartor.html', username = username, create_flight_table = session['create_flight_table'], error = 'Status should only be in-progress/upcoming/delayed. Please try again.')       
        query = "insert into Flight values ('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')"
        cursor.execute(query.format(airline_name, flight_num, departure_time, arrival_time, price,
        status, arrival_airport_name, departure_airport_name, airplane_id))
        conn.commit()

        end_date = datetime.date.today() + relativedelta(days=+30)
        begin_date = datetime.date.today()
        begin_date = datetime.datetime(begin_date.year, begin_date.month, begin_date.day, 0, 0, 0)
        end_date = datetime.datetime(end_date.year, end_date.month, end_date.day, 0, 0, 0)

        query = "SELECT * FROM Flight where airline_name = '{}' and status = 'upcoming'\
        and departure_time >= '{}.000' and  departure_time <= '{}.000'"
        cursor.execute(query.format(airline_name, begin_date, end_date))
        data = cursor.fetchall()
        for element in data:
            element['departure_time'] = str(element['departure_time'])
            element['arrival_time'] = str(element['arrival_time'])
        session['create_flight_table'] = data
        cursor.close()
        return render_template('create_new_flight_opeartor.html', username = username, create_flight_table = session['create_flight_table'])
    else:
        return render_template('create_new_flight_opeartor.html', username = username, error = 'Please add all the information. Please try again.', create_flight_table = session['create_flihgt_table'])


@app.route("/airline_staff_home_opeartor/add_airplane")
def add_airplane():
    username = session['username']
    airline_name = session['airline_name']
    cursor = conn.cursor()

    query = "SELECT * FROM Airplane where airline_name = '{}'"
    cursor.execute(query.format(airline_name))
    data = cursor.fetchall()
    session['my_airplane'] = data
    cursor.close()

    if(data):
        return render_template('add_airplane_opeartor.html', my_airplane = session['my_airplane'], username = username)
    else:
        return render_template('add_airplane_opeartor.html', username = username, error0 = "Your airline doesn't have any airplane. You can add one below.")

@app.route("/airline_staff_home_opeartor/add_airplane/action", methods=["GET", "POST"])
def add_airplane_action():
    username = session['username']
    airline_name = session['airline_name']
    cursor = conn.cursor()
    query_airplane_id = "select airplane_id from Airplane where airline_name = '{}'"
    cursor.execute(query_airplane_id.format(airline_name))
    airplane_id_list = cursor.fetchall()
    airplane_list = []
    for airplane_element in airplane_id_list:
        airplane_list.append(airplane_element['airplane_id'])

    num = 0
    if request.form['airline_name']:
        airline_name_input = request.form['airline_name']
        num += 1
    if request.form['airplane_id']:
        airplane_id = request.form['airplane_id']
        num += 1
    if request.form['seats']:
        seats = request.form['seats']
        num += 1

    if num == 3:
        if airline_name_input != airline_name:
            return render_template('add_airplane_opeartor.html', username = username, my_airplane = session['my_airplane'], error = 'You can only add new airplane for your airline. Please try again.')
        if airplane_id in airplane_list:
            return render_template('add_airplane_opeartor.html', username = username, my_airplane = session['my_airplane'], error = 'The airplane id is used in your airline. Please try again.')
        query = "insert into Airplane values ('{}', '{}', '{}')"
        cursor.execute(query.format(airplane_id ,airline_name, seats))
        print(query)
        conn.commit()

        query = "SELECT * FROM Airplane where airline_name = '{}'"
        cursor.execute(query.format(airline_name))
        data = cursor.fetchall()
        session['my_airplane'] = data
        cursor.close()
        return render_template('add_airplane_opeartor.html', username = username, my_airplane = session['my_airplane'])
    else:
        return render_template('add_airplane_opeartor.html', username = username, error = 'Please add all the information. Please try again.', my_airplane = session['my_airplane'])



@app.route("/airline_staff_home_opeartor/change_status")
def change_status():
    return render_template('change_status_opeartor.html')

@app.route("/airline_staff_home_opeartor/change_status/action", methods=["GET", "POST"] )
def change_status_action():
    username = session['username']
    airline_name = session['airline_name']
    cursor = conn.cursor()
    query_flight_num = "select flight_num from Flight where airline_name = '{}'"
    cursor.execute(query_flight_num.format(airline_name))
    flight_num_list = cursor.fetchall()
    print(flight_num_list)
    flight_list = []
    for flight_element in flight_num_list:
        flight_list.append(flight_element['flight_num'])

    num = 0
    if request.form['airline_name']:
        airline_name_input = request.form['airline_name']
        num += 1
    if request.form['flight_num']:
        flight_num_input = request.form['flight_num']
        num += 1
    if request.form['status']:
        status_input = request.form['status']
        num += 1
    if num == 3:
        if airline_name_input != airline_name:
            return render_template('change_status_opeartor.html', username = username, error = "You can only change status for the flight owned by your airline. Please try again.")
        if flight_num_input not in flight_list:
            return render_template('change_status_opeartor.html', username = username, error = "The flight number you input is not vaild. Please try again.")
        if status_input not in ['upcoming', 'delayed', 'in-progress']:
            return render_template('change_status_opeartor.html', username = username, error = 'Status should only be in-progress/upcoming/delayed. Please try again.')       
        query = "update Flight set status = '{}' where airline_name = '{}' and flight_num = '{}'"
        cursor.execute(query.format(status_input, airline_name_input, flight_num_input))
        conn.commit()
        cursor.close()
        return render_template('change_status_opeartor.html', username = username, error = "You have successfully change a flight status!")
    else:
        return render_template('change_status_opeartor.html', username = username, error = "Your airline doesn't have any airplane. You can add one below.")


@app.route("/airline_staff_home_opeartor/add_airport")
def add_airport():
    username = session['username']
    airline_name = session['airline_name']
    cursor = conn.cursor()
    query = "select * from Airport"
    cursor.execute(query)
    data = cursor.fetchall()
    session['world_airport'] = data

    query_my_airport = "select * from Airport_for_Airline where airline_name = '{}'"
    cursor.execute(query_my_airport.format(airline_name))
    data_my_airport = cursor.fetchall()
    session['my_airport'] = data_my_airport
    cursor.close()

    if(data_my_airport):    
        return render_template('add_airport_opeartor.html', world_airport = session['world_airport'], my_airport = session['my_airport'], username = username)
    else:
        return render_template('add_airport_opeartor.html', world_airport = session['world_airport'], error0 = 'There is no airport for your airline now. You can add one below.', username = username)

@app.route("/airline_staff_home_opeartor/add_airport/my_action", methods=["GET", "POST"])
def add_airport_my_action():
    username = session['username']
    airline_name = session['airline_name']
    cursor = conn.cursor()
    query = "select airport_name from Airport"
    cursor.execute(query)
    world_airport_dict = cursor.fetchall()
    world_airport_list = []
    for element in world_airport_dict:
        world_airport_list.append(element['airport_name'])

    query_world_airport = "select * from Airport"
    cursor.execute(query_world_airport)
    data_world_airport = cursor.fetchall()

    query_my_airport = "select * from Airport_for_Airline where airline_name = '{}'"
    cursor.execute(query_my_airport.format(airline_name))
    data_my_airport = cursor.fetchall()
    my_airport_list = []
    for element in data_my_airport:
        my_airport_list.append(element['airport_name'])

    num = 0
    if request.form['airport_name']:
        airport_name_input = request.form['airport_name']
        num += 1
    if request.form['airline_name']:
        airline_name_input = request.form['airline_name']
        num += 1
    
    if num == 2:
        if airline_name_input != airline_name:
             return render_template('add_airport_opeartor.html', world_airport = session['world_airport'], my_airport = session['my_airport'], username = username, error2 = 'You can only add airport to your airline system. Please try again.') 
        if airport_name_input not in world_airport_list:
            return render_template('add_airport_opeartor.html', world_airport = session['world_airport'], my_airport = session['my_airport'], username = username, error2 = 'The airport you input is not vaild. Please try again.') 
        if airport_name_input in my_airport_list:
            return render_template('add_airport_opeartor.html', world_airport = session['world_airport'], my_airport = session['my_airport'], username = username, error2 = 'The airport you input is already in the system. Please try again.') 
        else:
            query = "insert into Airport_for_Airline values ('{}', '{}')"
            cursor.execute(query.format(airport_name_input, airline_name_input))
            conn.commit()

            query_my_airport = "select * from Airport_for_Airline where airline_name = '{}'"
            cursor.execute(query_my_airport.format(airline_name))
            data_my_airport = cursor.fetchall()
            session['my_airport'] = data_my_airport
            cursor.close()

            return render_template('add_airport_opeartor.html', world_airport = session['world_airport'], my_airport = session['my_airport'], username = username)
    else:
         return render_template('add_airport_opeartor.html', world_airport = session['world_airport'], my_airport = session['my_airport'], username = username, error2 = 'Please input all the information.') 


@app.route('/airline_staff_home_opeartor/top_5_booking_agent_by_month', methods=["GET", "POST"])
def top_5_booking_agent_by_month():
    username = session['username']
    airline_name = session['airline_name']

    if request.form['month']:
        month = request.form['month']

    if(month):
        today = datetime.date.today()
        today = str(datetime.datetime(today.year, today.month, today.day, 0, 0, 0))
        if str(month) >= today[0:7]:
            return render_template('airline_staff_home_opeartor.html', error2 = 'Only avaiable for past month. Please try again.',
            my_flight = session['my_flight'], airline_name = airline_name, username = username, 
            ranking_last_3_month = session['ranking_last_3_month'], ranking_last_year = session['ranking_last_year'], 
            ranking_for_commission_received = session['ranking_for_commission_received'], frequent_customer_email = session['frequent_customer_email'], 
            frequent_customer_name = session['frequent_customer_name'])
        else:
            begin_month = datetime.datetime(int(month[0:4]), int(month[5:7]), 1, 0, 0, 0)
            end_month = begin_month + relativedelta(months=+1)

            cursor = conn.cursor()
            query = "select booking_agent_id, booking_agent_email, count(ticket_id) as num_of_ticket FROM Ticket natural join Booking_Agent where airline_name = '{}' and purchase_date >= '{}.000' and purchase_date <= '{}.000' and booking_agent_email is not null\
                group by booking_agent_id, booking_agent_email order by count(ticket_id) desc limit 5"
            cursor.execute(query.format(airline_name, str(begin_month), str(end_month)))
            data = cursor.fetchall()
            num = 1
            for element in data:
                element['rank'] = num
                num += 1
            session['ranking_for_month'] = data
            cursor.close()
            if(data):
                return render_template('airline_staff_home_opeartor.html', ranking_for_month = data,
                my_flight = session['my_flight'], airline_name = airline_name, username = username, 
                ranking_last_3_month = session['ranking_last_3_month'], ranking_last_year = session['ranking_last_year'], 
                ranking_for_commission_received = session['ranking_for_commission_received'], frequent_customer_email = session['frequent_customer_email'], 
                frequent_customer_name = session['frequent_customer_name'])         
            else:
                return render_template('airline_staff_home_opeartor.html', error2 = 'No booking agents sold the ticket from your airline in that time period.', 
                my_flight = session['my_flight'], airline_name = airline_name, username = username, 
                ranking_last_3_month = session['ranking_last_3_month'], ranking_last_year = session['ranking_last_year'], 
                ranking_for_commission_received = session['ranking_for_commission_received'], frequent_customer_email = session['frequent_customer_email'], 
                frequent_customer_name = session['frequent_customer_name'])
    else:
        return render_template('airline_staff_home_opeartor.html', error2 = 'Please give an input.', 
            my_flight = session['my_flight'], airline_name = airline_name, username = username, 
            ranking_last_3_month = session['ranking_last_3_month'], ranking_last_year = session['ranking_last_year'], 
            ranking_for_commission_received = session['ranking_for_commission_received'], frequent_customer_email = session['frequent_customer_email'], 
            frequent_customer_name = session['frequent_customer_name'])


@app.route('/airline_staff_home_opeartor/top_5_booking_agent_by_year', methods=["GET", "POST"])
def top_5_booking_agent_by_year():
    username = session['username']
    airline_name = session['airline_name']

    if request.form['year']:
        year = request.form['year']
        print(year)
    if(year):
        today = datetime.date.today()
        today = str(datetime.datetime(today.year, today.month, today.day, 0, 0, 0))
        if str(year) > today[0:4]:
            return render_template('airline_staff_home_opeartor.html', error3 = 'Only avaiable for past year. Please try again.',
            my_flight = session['my_flight'], airline_name = airline_name, username = username, 
            ranking_last_3_month = session['ranking_last_3_month'], ranking_last_year = session['ranking_last_year'], 
            ranking_for_commission_received = session['ranking_for_commission_received'], frequent_customer_email = session['frequent_customer_email'], 
            frequent_customer_name = session['frequent_customer_name'])
        else:
            begin_year = datetime.datetime(int(year), 1, 1, 0, 0, 0)
            end_year = begin_year + relativedelta(months=+12)

            cursor = conn.cursor()
            query = "select booking_agent_id, booking_agent_email, count(ticket_id) as num_of_ticket FROM Ticket natural join Booking_Agent where airline_name = '{}' and purchase_date >= '{}.000' and purchase_date <= '{}.000' and booking_agent_email is not null\
                group by booking_agent_id, booking_agent_email order by count(ticket_id) desc limit 5"
            cursor.execute(query.format(airline_name, str(begin_year), str(end_year)))
            data = cursor.fetchall()
            num = 1
            for element in data:
                element['rank'] = num
                num += 1
            session['ranking_for_year'] = data
            cursor.close()
            if(data):
                return render_template('airline_staff_home_opeartor.html', ranking_for_year = data,
                my_flight = session['my_flight'], airline_name = airline_name, username = username, 
                ranking_last_3_month = session['ranking_last_3_month'], ranking_last_year = session['ranking_last_year'], 
                ranking_for_commission_received = session['ranking_for_commission_received'], frequent_customer_email = session['frequent_customer_email'], 
                frequent_customer_name = session['frequent_customer_name'])
            else:
                return render_template('airline_staff_home_opeartor.html', error3 = 'No booking agents sold the ticket from your airline in that time period.',
                my_flight = session['my_flight'], airline_name = airline_name, username = username, 
                ranking_last_3_month = session['ranking_last_3_month'], ranking_last_year = session['ranking_last_year'], 
                ranking_for_commission_received = session['ranking_for_commission_received'], frequent_customer_email = session['frequent_customer_email'], 
                frequent_customer_name = session['frequent_customer_name'])
    else:
        return render_template('airline_staff_home_opeartor.html', error3 = 'Please give an input.',
            my_flight = session['my_flight'], airline_name = airline_name, username = username, 
            ranking_last_3_month = session['ranking_last_3_month'], ranking_last_year = session['ranking_last_year'], 
            ranking_for_commission_received = session['ranking_for_commission_received'], frequent_customer_email = session['frequent_customer_email'], 
            frequent_customer_name = session['frequent_customer_name'])


@app.route('/airline_staff_home_opeartor/frequent_custormer', methods=["GET", "POST"])
def frequent_customer():
    username = session['username']
    airline_name = session['airline_name']
    cursor = conn.cursor()

    if request.form['customer_email']:
        customer_email = request.form['customer_email']
    if(customer_email):
        query = "select * from (Flight natural join Ticket) natural join Customer where customer_email = '{}' and airline_name = '{}'"
        cursor.execute(query.format(customer_email, airline_name))
        data = cursor.fetchall()
        cursor.close()
        if(data):
            return render_template('Airline_staff_home_opeartor.html', search_customer = data,
            my_flight = session['my_flight'], airline_name = airline_name, username = username, 
            ranking_last_3_month = session['ranking_last_3_month'], ranking_last_year = session['ranking_last_year'], 
            ranking_for_commission_received = session['ranking_for_commission_received'], frequent_customer_email = session['frequent_customer_email'], 
            frequent_customer_name = session['frequent_customer_name'])
        else:
            return render_template('Airline_staff_home_opeartor.html', error5 = 'The customer email you input has not take any of the flights from your airline.',
            my_flight = session['my_flight'], airline_name = airline_name, username = username, 
            ranking_last_3_month = session['ranking_last_3_month'], ranking_last_year = session['ranking_last_year'], 
            ranking_for_commission_received = session['ranking_for_commission_received'], frequent_customer_email = session['frequent_customer_email'], 
            frequent_customer_name = session['frequent_customer_name'])
    else:
        return render_template('Airline_staff_home_opeartor.html',error5 = 'Please enter the customer email first. Please try again.',my_flight = session['my_flight'], airline_name = airline_name, username = username, 
            ranking_last_3_month = session['ranking_last_3_month'], ranking_last_year = session['ranking_last_year'], 
            ranking_for_commission_received = session['ranking_for_commission_received'], frequent_customer_email = session['frequent_customer_email'], 
            frequent_customer_name = session['frequent_customer_name'])


@app.route("/airline_staff_home_opeartor/grant_new_permissions")
def grant_new_permissions():
    username = session['username']
    airline_name = session['airline_name']
    cursor = conn.cursor()

    query = "SELECT * FROM Permission natural join Airline_Staff where airline_name = '{}'"
    cursor.execute(query.format(airline_name))
    data = cursor.fetchall()
    print(data)
    session['permission_table'] = data
    query_staff = "select staff_user_name from Airline_Staff where airline_name = '{}'"
    cursor.execute(query_staff.format(airline_name))
    data_staff = cursor.fetchall()
    session['staff_table'] = data_staff
    cursor.close()
    return render_template('grant_new_permission_opeartor.html', permission_table = data, staff_table = data_staff, username = username)

@app.route("/airline_staff_home_opeartor/grant_new_permissions/action", methods=["GET", "POST"])
def grant_new_permission_action():
    username = session['username']
    airline_name = session['airline_name']
    cursor = conn.cursor()
    query_staff = "select staff_user_name from Airline_Staff where airline_name = '{}'"
    cursor.execute(query_staff.format(airline_name))
    data_staff = cursor.fetchall()
    staff_list = []
    for element in data_staff:
        staff_list.append(element['staff_user_name'])


    num = 0
    if request.form['staff_user_name']:
        staff_user_name = request.form['stuff_user_name']
        num += 1
    if request.form['permission_name']:
        permission_name = request.form['permission_name']
        num += 1
    if num == 2:
        if staff_user_name not in staff_list:
            return render_template('grant_new_permission_opeartor.html', username = username, permission_table = session['permission_table'], staff_table = session['staff_table'],  error = 'Your input is not valid, please try again.')
        if permission_name not in ['Admin', 'Operator']:
            return render_template('grant_new_permission_opeartor.html', username = username, permission_table = session['permission_table'], staff_table = session['staff_table'] , error = 'You can only input either Admin or Operator in permission_name, please try again.')
        for element in session['permission_table']:
            if element[staff_user_name] == permission_name:
                return render_template('grant_new_permission_opeartor.html', username = username, permission_table = session['permission_table'], staff_table = session['staff_table'], error = 'The staff has already got the permission, please try again.')
        query = "insert Permission values('{}', '{}')"
        query.execute(query.format(staff_user_name, permission_name))
        conn.commit()

        query = "SELECT * FROM Permission natural join Airline_Staff where airline_name = '{}'"
        cursor.execute(query.format(airline_name))
        data = cursor.fetchall()
        print(data)
        session['permission_table'] = data
        cursor.close()
        return render_template('grant_new_permission_opeartor.html', username = username, permission_table = session['permission_table'], staff_table = session['staff_table'])
    else:
        return render_template('grant_new_permission_opeartor.html', username = username, permission_table = session['permission_table'], staff_table = session['staff_table'], error = 'Please input all the information. Please try again.')

@app.route("/airline_staff_home_opeartor/add_new_booking_agents")
def add_new_booking_agents():
    username = session['username']
    airline_name = session['airline_name']
    cursor = conn.cursor()

    query = "SELECT * FROM Booking_Agent_Work_For natural join Booking_Agent where airline_name = '{}'"
    cursor.execute(query.format(airline_name))
    data = cursor.fetchall()
    session['booking_agent_table'] = data
    return render_template('add_new_booking_agents_opeartor.html', username = username, search_booking_agent = session['booking_agent_table'])


@app.route("/airline_staff_home_opeartor/add_new_booking_agents/action", methods=["GET", "POST"])
def add_new_booking_agents_action():
    username = session['username']
    airline_name = session['airline_name']
    cursor = conn.cursor()
    query_booking_agents = 'select * from Booking_Agent'
    cursor.execute(query_booking_agents)
    data_booking_agents = cursor.fetchall()
    booking_agent_list = []
    for element in data_booking_agents:
        booking_agent_list.append(element['booking_agent_email'])
    print(booking_agent_list)
    
    my_booking_agent_list = []
    for element in session['booking_agent_table']:
        my_booking_agent_list.append(element['booking_agent_email'])
    
    if request.form['booking_agent_email']:
        booking_agent_email = request.form['booking_agent_email']

    if(booking_agent_email):
        if booking_agent_email not in booking_agent_list:
            return render_template('add_new_booking_agents_opeartor.html', username = username, search_booking_agent = session['booking_agent_table'], error = 'The booking agent email you add is not vaild. Please try again.')
        if booking_agent_email in my_booking_agent_list:
            return render_template('add_new_booking_agents_opeartor.html', username = username, search_booking_agent = session['booking_agent_table'], error = 'The booking agent email you add is already worked for your airline. Please try again.')
        query = "insert Booking_Agent_Work_For values('{}', '{}')"
        cursor.execute(query.format(booking_agent_email, airline_name))
        conn.commit()
        
        query = "SELECT * FROM Booking_Agent_Work_For natural join Booking_Agent where airline_name = '{}'"
        cursor.execute(query.format(airline_name))
        data = cursor.fetchall()
        session['booking_agent_table'] = data
        cursor.close()
        return render_template('add_new_booking_agents_opeartor.html', username = username, search_booking_agent = session['booking_agent_table'])
    else:
        return render_template('add_new_booking_agents_opeartor.html', username = username, search_booking_agent = session['booking_agent_table'], error = 'Please input all the information. Please try again.')


app.secret_key = 'some key that you will never guess'
if __name__ == "__main__":
    app.run('127.0.0.1', 5000, debug = True)