#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 15 15:33:08 2022

@author: ellazhang
"""

# Import Flask Library
from __future__ import print_function
import logging
from flask import Flask, render_template, request, session, url_for, redirect
import pymysql.cursors
import math
import datetime
import matplotlib.pyplot as plt
import numpy as np
import base64
from io import BytesIO
from werkzeug.security import generate_password_hash,check_password_hash
import sys
plt.switch_backend('Agg') 

from flask import Flask as _Flask
from flask.json import JSONEncoder as _JSONEncoder
 
class JSONEncoder(_JSONEncoder):
    def default(self, o):
        import decimal
        if isinstance(o, decimal.Decimal):
 
            return float(o)
 
        super(JSONEncoder, self).default(o)
 
class Flask(_Flask):
    json_encoder = JSONEncoder


#Initialize the app from Flask
app = Flask(__name__)
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(days=7)


#Configure MySQL
conn = pymysql.connect(host='localhost',
                       user='root',
                       password='',
                       db='A8',
                       charset='utf8mb4',
                       cursorclass=pymysql.cursors.DictCursor)

# =============================================================================
# # general 
# @app.route('/')
# def welcome():
#     session.clear()
#     return render_template('welcome.html')
# =============================================================================

@app.route('/')
def welcome():
    session.clear()
    return render_template('welcome.html')

@app.route('/upcoming_flight',methods=['GET', 'POST'])
def upcoming_flight():
    cursor = conn.cursor()
    query = "SELECT * FROM flight where status = 'upcoming'"
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
    query = "SELECT * FROM flight where status = 'upcoming' and"
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
        add = "and '"+ str(a_start)[:10] +"' <=arrival_time  and arrival_time <='"+ str(a_end)[:10]+"'"
        appendix += add
    if request.form['departure_airport']:
        d_airport = request.form['departure_airport']
        appendix += "and departure_airport_name = '"
        appendix += d_airport
        appendix += "'"
    if request.form['arrival_airport'] :
        a_airport = request.form['arrival_airport'] 
        appendix += "and arrival_airport_name = '"
        appendix += a_airport
        appendix += "'"
    if request.form['flight_num']:
        f_number = request.form['flight_num'] 
        appendix += "and flight_num = '"
        appendix += f_number
        appendix += "'"
    if appendix ==  "":
        query = "SELECT * from flight"
    else:
        query += appendix[3:]
    #cursor used to send queries
    cursor = conn.cursor()
    #executes query	
    cursor.execute(query)
    #stores the results in a variable
    data = cursor.fetchall()
    cursor.close()
    error = None
    if (data):
        # return redirect(url_for('upcoming_flight'))
        return render_template('upcoming_flight.html', upcoming_flight = data)
    else:
        return render_template('upcoming_flight.html', error1 = "Sorry, no flights are found. Please check your input again.")
        
#Define route for login
# login as an existed user
@app.route('/login',methods=['GET', 'POST'])
def login():
    session.clear()
    return render_template('login.html')

def logout():
	session.pop('username')
	return redirect('/')

# Define route for register
# create a new account for customer
@app.route('/customer_register',methods=['GET', 'POST'])
def register_customer():
    return render_template('customer_register.html')

# create a new account for booking agent
@app.route('/agent_register',methods=['GET', 'POST'])
def register_agent():
    return render_template('agent_register.html')

# create a new account for airline staff
@app.route('/staff_register',methods=['GET', 'POST'])
def register_staff():
    query = "select airline_name from airline"
    cursor = conn.cursor()
    cursor.execute(query)
    airline = cursor.fetchall()
    cursor.close()
    airlines = []
    for i in airline:
        airlines.append(i['airline_name'])
    print(airlines)
    return render_template('staff_register.html',airlines = airlines)

#Authenticates the register
@app.route('/registerAuth_customer', methods=['GET', 'POST'])
def registerAuth_customer():
    #grabs information from the forms
    email = request.form['email']
    password = request.form['password']
    password2 = request.form['password2']
    #cursor used to send queries
    cursor = conn.cursor()
    #executes query
    query = 'SELECT * FROM customer WHERE customer_email = %s'
    cursor.execute(query, (email))
    #stores the results in a variable
    data = cursor.fetchone()
    print(data)
    #use fetchall() if you are expecting more than 1 data row
    error = None
    if password != password2:
        error = "Password does not match"
        return render_template('customer_register.html', error = error)
    elif(data):
        #If the previous query returns data, then user exists
        error = "This user already exists"
        return render_template('customer_register.html', error = error)
    else:
        username = request.form["username"]
        birthday = request.form["birthday"]
        state = request.form["state"]
        city = request.form["city"]
        street = request.form["street"]
        building = request.form["building"]
        passport_num = request.form["passport number"]
        passport_country = request.form["Passport Country"]
        expiration = request.form["expiration date"]
        phone = int(request.form["phone"])
        ins = 'INSERT INTO customer VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
        password = generate_password_hash(password)
        cursor.execute(ins, (email, username, password,building, street, city,state, phone,passport_num,expiration,passport_country,birthday))
        conn.commit()
        cursor.close()
        return render_template('customer_register.html',success = username)

#Looks okay============
@app.route('/registerAuth_agent', methods=['GET', 'POST'])
def registerAuth_agent():
    #grabs information from the forms
    email = request.form['email']
    password = request.form['password']
    password2 = request.form['password2']
    cursor = conn.cursor()
    query_email = 'SELECT * FROM booking_agent WHERE booking_agent_email = %s'
    cursor.execute(query_email, (email))
    data1 = cursor.fetchone()
    error = None

    if data1 != None:
        error = 'User already exists.'
        return render_template('agent_register.html', error = error)
    if password != password2:
        error = "Password does not match"
        return render_template('agent_register.html', error = error)
    else:
        query = "select max(booking_agent_id) from booking_agent"
        cursor.execute(query)
        booking_agent_id = cursor.fetchone()
        print(booking_agent_id)

        if booking_agent_id[max(booking_agent_id)]:
            id = booking_agent_id[max(booking_agent_id)] + 1
        else:
            id = 1
        print(email,password,id)
        password = generate_password_hash(password)
        ins1 = 'INSERT INTO booking_agent VALUES(%s, %s, %s)'
        cursor.execute(ins1, (email, password, id))
        conn.commit()
        cursor.close()
        return render_template('agent_register.html',id = id) 

@app.route('/registerAuth_staff', methods=['GET', 'POST'])
def registerAuth_staff():
    query = "select airline_name from airline"
    cursor = conn.cursor()
    cursor.execute(query)
    airline = cursor.fetchall()
    cursor.close()
    airlines = []
    for i in airline:
        airlines.append(i['airline_name'])

    # try:
    #grabs information from the forms
    #Here username is this person's email
    username = request.form['email']
    password = request.form['password']
    password2 = request.form['password2']
    airline_name = request.form["airline_name"]
    print("airline_name: ",airline_name)

    #cursor used to send queries
    cursor = conn.cursor()
    #executes query
    #here username is this person's email
    query = 'SELECT * FROM airline_staff WHERE staff_user_name = %s'
    cursor.execute(query, (username))
    #stores the results in a variable
    data = cursor.fetchone()
    #use fetchall() if you are expecting more than 1 data row

    query_airline = 'SELECT * FROM airline WHERE airline_name = %s'
    cursor.execute(query_airline, airline_name)
    print(airline_name)
    data2 = cursor.fetchone()

    error = None

    if data2 == None:
        error = 'Airline name does not exist in the database.'
        return render_template('staff_register.html', error = error,airlines = airlines)

    if password != password2:
        error = "Password does not match"
        return render_template('staff_register.html', error = error,airlines = airlines)

    if(data):
        #If the previous query returns data, then user exists
        error = "This user already exists"
        return render_template('staff_register.html', error = error,airlines = airlines)

    else:
        firstName = request.form["first_name"]
        lastName = request.form["last_name"]
        d_birth = request.form['date_of_birth']
        birthday = datetime.datetime.strptime(d_birth,'%Y-%m-%d')
        password = generate_password_hash(password)
        ins1 = 'INSERT INTO airline_staff VALUES(%s, %s, %s, %s, %s, %s)'
        cursor.execute(ins1, (username, password, firstName, lastName, birthday, airline_name))

        conn.commit()
        cursor.close()
        return render_template('staff_register.html',success = username,airlines = airlines)
    # except:
    #     return render_template('staff_register.html', error = "Invalid Input",airlines = airlines )


# Authenticates the login account
@app.route('/loginAuth', methods=['GET', 'POST'])
def loginAuth():
    username = request.form['username']
    print(username)
    password = request.form['password']
    role = request.form['role']

    if role == "Customer":
        cursor = conn.cursor()
        query = 'SELECT customer_password FROM Customer WHERE customer_email = %s'
        cursor.execute(query, (username))
        db_pw = cursor.fetchone()
        cursor.close()
        error = None
        if(db_pw):
            db_pw = db_pw["customer_password"]
            flag = check_password_hash(db_pw,password)
            if password == db_pw:
                session['username'] = username
                session['role'] = role
                session.permanent = True
                return redirect(url_for('customer_home',customer_email = username))
            else:
                error = 'Wrong password'
            return render_template('login.html', error=error)
        else:
            error = 'Invalid login name'
            return render_template('login.html', error=error)
    
    elif role =="Booking agent":
        #cursor used to send queries
        cursor = conn.cursor()
        #executes query
        query = 'SELECT * FROM booking_agent WHERE booking_agent_email = %s '
        cursor.execute(query, username)
        #stores the results in a variable
        db_pw = cursor.fetchone()
        #use fetchall() if you are expecting more than 1 data row
        cursor.close()
        error = None
        if(db_pw):
            db_pw = db_pw["booking_agent_password"]
            # flag = check_password_hash(db_pw,password)
            if password == db_pw:
                #creates a session for the the user
                #session is a built in
                session['username'] = username
                session['role'] = role
                session.permanent = True
    
                # get the company that the agent works for
                cursor = conn.cursor()
                #executes query
                query = 'SELECT airline_name from works_for WHERE booking_agent_email = %s'
                cursor.execute(query, (username))
                #stores the results in a variable
                companyAll = cursor.fetchall()
                #use fetchall() if you are expecting more than 1 data row
                cursor.close()
                session['company'] = []
                for i in companyAll:
                    session['company'].append(i['airline_name'])
                # print('HERE!!', session['company'])
                return redirect(url_for('agent_home', agent_email = username))
            else:
                error = 'Wrong password'
                return render_template('login.html', error=error)
        else:
            #returns an error message to the html page
            error = 'Invalid login or username'
            return render_template('login.html', error=error)
    else:
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

@app.route("/customer_home/<customer_email>", defaults={'error':''}, methods=["GET", "POST"])
@app.route("/customer_home/<customer_email>/<error>", methods=["GET", "POST"])
def customer_home(customer_email,error):
    month = ["Jan","Feb","Mar","Apr","May","June","July","Aug","Sep","Oct","Nov","Dec"]
    if session['username'] != customer_email:
        print("case1")
        return render_template("login.html", error="Bad Request")
    # default view my flights
    query = 'select * from flight where status ="upcoming" and (airline_name,flight_num) in (select airline_name, flight_num from ticket where customer_email = %s)'
    cursor = conn.cursor()
    cursor.execute(query,session['username'])
    data =  cursor.fetchall()
    print(data)
    cursor.close()

    # default spending  
    cur = datetime.date.today()
    year_ago  = cur - datetime.timedelta(days=365)
    print(cur,year_ago)
    query = 'select * from flight where (airline_name,flight_num) in (select airline_name, flight_num from ticket where customer_email = %s and purchase_date <= %s and purchase_date >= %s) '
    cursor = conn.cursor()
    cursor.execute(query,(session['username'],cur,year_ago))
    money =  cursor.fetchall()
    cursor.close()

    year_money = 0
    for i in money:
        year_money += i['price']
            
    # default draw an image
    query = "SELECT price, purchase_date FROM ticket NATURAL JOIN flight WHERE customer_email = '%s'"
    cursor = conn.cursor()
    cursor.execute(query % session['username'])
    info = cursor.fetchall()
    cursor.close()

    half_ago = cur - datetime.timedelta(days=180)
    last_month = cur.month
    begin_month = last_month-6
    spent = [0 for i in range(6)]
    for record in info:
        if cur > record['purchase_date'] >= half_ago:
            print("1")
            mon = record['purchase_date'].month
            print(mon)
            if last_month >= mon:
                spent[(5-last_month+mon)%6] += record['price']
            else:
                spent[(-12-last_month+mon)%6] += record['price']
                

    x_axis = [month[i] for i in range(begin_month,begin_month+6)]
    plt.clf()
    plt.bar(x_axis,spent, color = '#009879')
    plt.title('Monthly spent for last six months')
    plt.xlabel('Month')
    plt.ylabel('Spent')
    for a,b in zip(x_axis,spent):
        plt.text(a,b, b, ha='center', va= 'bottom',fontsize=7)
    # save as binary file
    buffer = BytesIO()
    plt.savefig(buffer)
    plot_data = buffer.getvalue()
    imb = base64.b64encode(plot_data)
    ims = imb.decode()
    image = "data:image/png;base64," + ims
    plt.close()
    
    session['data'] = data
    session['yearmoney'] = year_money
    session['barchart'] = image
    
    # return the form of checking spending 
    try:
        if request.form["begin_date"]:
            begin = request.form['begin_date']
            begin = datetime.datetime.strptime(begin,'%Y-%m-%d')
            year2 = begin.year
            month2 = begin.month
        if request.form['end_date']:
            end = request.form['end_date']
            end = datetime.datetime.strptime(end,'%Y-%m-%d')
            year1 = end.year
            month1 = end.month
        else:
            year1 = cur.year
            month1 = cur.month
        delta_month = (year1-year2)*12+(month1-month2)+1
        ago = cur - datetime.timedelta(days=delta_month*30)
        last_month = cur.month
        begin_month = last_month-delta_month
        spent = [0 for i in range(delta_month)]
        for record in info:
            if cur > record['purchase_date'] >= ago:
                mon = record['purchase_date'].month
                year = record['purchase_date'].year
                cur_delta_month = (year1-year)*12+(month1-mon)
                spent[(delta_month -1- cur_delta_month)% delta_month] += record['price']
        x_axis = [month[i] for i in range(begin_month,begin_month+delta_month)]
        print(spent,x_axis)
        plt.clf()
        plt.bar(x_axis,spent)
        plt.title('Monthly spent for last 6 months')
        plt.xlabel('Month')
        plt.ylabel('Spent')
        for a,b in zip(x_axis,spent):
            plt.text(a,b, b, ha='center', va= 'bottom',fontsize=7)
        buffer1 = BytesIO()
        plt.savefig(buffer1)
        plot_data = buffer1.getvalue()
        imb = base64.b64encode(plot_data)
        ims = imb.decode()
        image = "data:image/png;base64," + ims
        plt.close()
    except:
            print("Not form Track spending or no start date")
    try:
        # return the form of checking flights 
        query = 'select * from flight where status ="upcoming" and (airline_name,flight_num) in (select airline_name, flight_num from ticket where customer_email = %s) '
        appendix = ""
        
        if request.form['departure_date']:
            d_date = request.form['departure_date']
            d_start = datetime.datetime.strptime(d_date,'%Y-%m-%d')
            d_end = d_start + datetime.timedelta(days=1)
            add = "and '"+ str(d_start)[:10] +"' <=departure_time  and departure_time <='"+ str(d_end)[:10]+"' "
            appendix += add 
        if request.form['arrival_date']:
            a_date = request.form['arrival_date']
            a_start = datetime.datetime.strptime(a_date, '%Y-%m-%d')
            a_end = a_start + datetime.timedelta(days=1)
            add = "and '"+ str(a_start)[:10] +"' <=arrival_time  and arrival_time <='"+ str(a_end)[:10]+"' "
            appendix += add
        if request.form['flight'] :
            flight_num = request.form['flight'] 
            appendix += "and flight_num = '" + flight_num +"' "
        if request.form['departure_airport']:
            d_airport = request.form['departure_airport']
            appendix += "and departure_airport_name = '"
            appendix += d_airport
            appendix += "' "
        if request.form['arrival_airport'] :
            a_airport = request.form['arrival_airport'] 
            appendix += "and arrival_airport_name = '"
            appendix += a_airport
            appendix += "' "
    
        query += appendix
        #cursor used to send queries
        cursor = conn.cursor()
        #executes query	
        cursor.execute(query,session['username'])
        print("succesfully executed")
        data = cursor.fetchall()
        cursor.close()
        return render_template("customer_home.html",search_flight = data,year_money = year_money,bar_chart = image)
    except:
        return render_template("customer_home.html",search_flight = data,year_money = year_money,bar_chart = image)

@app.route("/customer/flight_purchase/<customer_email>/<flight_num>/<airline_name>",methods=["GET", "POST"])
def customer_purchase(customer_email,flight_num, airline_name):
    print(session["username"],customer_email)
    if session['username'] != customer_email:
        print("case1")
        return render_template("upcoming_flight.html", error1="Bad Request: username does not match")

    # if I had already buy the ticket
    query = """select * from ticket 
        where ticket.customer_email = %s 
        and ticket.flight_num = %s 
        and ticket.airline_name = %s"""
    cursor = conn.cursor()
    cursor.execute(query,(customer_email,flight_num, airline_name))
    data =  cursor.fetchall()
    cursor.close()


    # if there is no seats left
    query = """select seats from airplane where airline_name = %s
    and airplane_id in (select airplane_id from flight where airline_name = %s and flight_num = %s)"""
    cursor = conn.cursor()
    cursor.execute(query,(airline_name, airline_name, flight_num))
    totalSeats =  cursor.fetchone()
    totS = totalSeats['seats']
    cursor.close()

    query = """SELECT count(*)
        FROM ticket
        WHERE airline_name = %s
        AND flight_num = %s"""
    cursor = conn.cursor()
    cursor.execute(query,(airline_name, flight_num))
    soldSeats =  cursor.fetchone()
    sldS = soldSeats['count(*)']
    cursor.close()
    
    if sldS == totS:
        print('NO SEATS: soldSeats == totalSeats')
        return render_template("upcoming_flight.html", search_flight = session['data'], error1 = "No seats left for the flight.")
#        return render_template("upcoming_flight.html", search_flight = session['data'], year_data = session['yearmoney'], bar_chart = session['barchart'], error1 = "No seats left for the flight.")
    elif data:
        print("Now we are here Customer purchase")
        return render_template("customer_home.html", search_flight = session['data'], status = "You have already bought the ticket")
#        return render_template("upcoming_flight.html", search_flight = session['data'], year_data = session['yearmoney'], bar_chart = session['barchart'], status = "You have already bought the ticket")
    else: # if I haven't buy the ticket

        query = "select max(ticket_id) from ticket"
        cursor = conn.cursor()
        cursor.execute(query)
        data = cursor.fetchall()
        cursor.close()

        # if this ticket id already exists
        if data[0]["max(ticket_id)"]:
            ticket_id = data[0]["max(ticket_id)"]+1

        else:
            ticket_id = 1
        cursor = conn.cursor()
        query1 = "insert into ticket values(%s, %s, %s, %s, %s, %s)"
        cursor.execute(query1,(ticket_id,airline_name,flight_num, customer_email, None, datetime.datetime.now().strftime('%Y-%m-%d')))
        cursor.close()
        conn.commit()
        return render_template("customer_home.html", search_flight = session['data'], status = "You have successfully buy the ticket!")
#        return render_template("upcoming_flight.html", search_flight = session['data'], year_data = session['yearmoney'], bar_chart = session['barchart'], status = "You have successfully buy the ticket!")
# Agent
@app.route("/agent_home/<agent_email>", defaults={'error':''}, methods=["GET", "POST"])
@app.route("/home_agent/<agent_email>/<error>", methods=["GET", "POST"])
def agent_home(agent_email, error):
    month = ["Jan","Feb","Mar","Apr","May","June","July","Aug","Sep","Oct","Nov","Dec"]
    if session['username'] != agent_email:
        print("case1")
        return render_template("login.html", error="Bad Request")
    
    # default view my flights
    #status: Upcoming, Delay, In progress
    query = """select flight.airline_name, flight.flight_num, flight.departure_time, flight.arrival_time, flight.price, flight.status, flight.arrival_airport_name, flight.departure_airport_name, flight.airplane_id, ticket.customer_email
    from flight natural join ticket
    where status ="upcoming" and booking_agent_email = %s"""
    cursor = conn.cursor()
    cursor.execute(query,session['username'])
    data =  cursor.fetchall()
    cursor.close()
    
    # default commission  
    cur = datetime.date.today()
    month_ago  = cur - datetime.timedelta(days=30)
    query = '''select * from flight 
        where (airline_name,flight_num) in 
        (select airline_name, flight_num from ticket where 
        purchase_date <= %s and purchase_date >= %s and
        booking_agent_email = %s )'''
    cursor = conn.cursor()
    cursor.execute(query,(cur, month_ago, session['username']))
    money =  cursor.fetchall()
    tnum = len(money)
    cursor.close()
    month_money = 0
    for i in money:
        month_money += i['price']
    average_commission = "{0:.2f}".format(month_money/tnum)
    # default draw an image
    #Top customers in past half-year: num of tickets
    half_ago = cur - datetime.timedelta(days=183)
    year_ago = cur - datetime.timedelta(days=365)
    query = """select count(flight.price) AS 'totnum', ticket.customer_email
        from flight join ticket
        where flight.airline_name = ticket.airline_name
        AND flight.flight_num = ticket.flight_num
        AND ticket.booking_agent_email = %s
        AND ticket.purchase_date >= %s
        AND ticket.purchase_date <= %s
        GROUP BY ticket.customer_email
        ORDER by totnum desc
        LIMIT 5"""
    cursor = conn.cursor()
    cursor.execute(query, (session['username'], half_ago, cur))
    halfdata = cursor.fetchall()
    cursor.close()
    name1 = []
    value1 = []
    for i in halfdata:
        name1.append(i['customer_email'])
        value1.append(i['totnum'])
    plt.clf()
    plt.bar(name1, value1, color = '#009879')
    plt.title('Top customers (num of tickets sold) in last 6 months')
    plt.ylabel('Number of Tickets')
    plt.xticks(rotation=10)
    for a,b in zip(name1, value1):
        plt.text(a,b, b, ha='center', va= 'bottom',fontsize=8)
    
    buffer = BytesIO()
    plt.savefig(buffer)
    plot_data1 = buffer.getvalue()
    imb = base64.b64encode(plot_data1)
    ims = imb.decode()
    image1 = "data:image/png;base64," + ims
    
    #Top customers in past year: total commission
    query = """select sum(flight.price) AS 'totprice', ticket.customer_email
        from flight join ticket
        where flight.airline_name = ticket.airline_name
        AND flight.flight_num = ticket.flight_num
        AND ticket.booking_agent_email = %s
        AND ticket.purchase_date >= %s
        AND ticket.purchase_date <= %s
        GROUP BY ticket.customer_email
        ORDER by totprice desc
        LIMIT 5"""
    cursor = conn.cursor()
    cursor.execute(query, (session['username'], year_ago, cur))
    yeardata = cursor.fetchall()
    cursor.close()
    for i in yeardata: 
        i['totprice'] = float(i['totprice'])
    session['yeardata'] = yeardata
    name2 = []
    value2 = []
    for i in yeardata:
        name2.append(i['customer_email'])
        value2.append(i['totprice'])
    
    plt.clf()
    plt.xticks(rotation=10)
    plt.bar(name2, value2, color = '#009879')
    plt.title('Top customers (amount of commission received) last year')
    plt.ylabel('Commission')
    for a,b in zip(name2, value2):
        plt.text(a,b, b, ha='center', va= 'bottom',fontsize=8)
    buffer2 = BytesIO()
    plt.savefig(buffer2)
    plot_data2 = buffer2.getvalue()
    imb2 = base64.b64encode(plot_data2)
    ims2 = imb2.decode()
    image2 = "data:image/png;base64," + ims2

#    session['agentdata'] = data
#    session['monthmoney'] = month_money
#    session['tnum'] = tnum
#    session['averagecommission'] = average_commission
#    session['halfdata'] = halfdata
#    session['yeardata'] = yeardata
#    session['image1'] = image1
#    session['image2'] = image2
    
    # if user specify time span in View Commission
    try:
        end = datetime.date.today()
        begin = end-datetime.timedelta(days=30)
        if request.form['begin_date']:
            begin = request.form['begin_date']
            begin = datetime.datetime.strptime(begin,'%Y-%m-%d')
        if request.form['end_date']:
            end = request.form['end_date']
            end = datetime.datetime.strptime(end,'%Y-%m-%d')
        #get a list of info within the input time span===================
    
        query = """select * from flight 
            where (airline_name,flight_num) in 
            (select airline_name, flight_num from ticket where purchase_date <= %s 
            and purchase_date >= %s
            and booking_agent_email = %s)"""
        cursor = conn.cursor()
        cursor.execute(query,(end, begin, session['username']))
        inputdata =  cursor.fetchall()
        inputnum = len(inputdata)
        cursor.close()
        inputmoney = 0
        for i in inputdata:
            inputmoney += i['price']
        return render_template("agent_home.html", search_flight = data, 
                               inputnum = inputnum, inputmoney=inputmoney,image1 = image1, image2 = image2)
    except:
        print("Do something")
    
    
    try:
        # return the form of checking flights 
        query = 'select * from flight where status ="upcoming" and (airline_name,flight_num) in (select airline_name, flight_num from ticket where booking_agent_email = %s) '
        appendix = ""
        
        if request.form['departure_date']:
            d_date = request.form['departure_date']
            d_start = datetime.datetime.strptime(d_date,'%Y-%m-%d')
            d_end = d_start + datetime.timedelta(days=1)
            add = "and '"+ str(d_start)[:10] +"' <=departure_time  and departure_time <='"+ str(d_end)[:10]+"' "
            appendix += add 
        if request.form['arrival_date']:
            a_date = request.form['arrival_date']
            a_start = datetime.datetime.strptime(a_date, '%Y-%m-%d')
            a_end = a_start + datetime.timedelta(days=1)
            add = "and '"+ str(a_start)[:10] +"' <=arrival_time  and arrival_time <='"+ str(a_end)[:10]+"' "
            appendix += add
        if request.form['flight'] :
            flight_num = request.form['flight'] 
            appendix += "and flight_num = '" + flight_num +"' "
        if request.form['departure_airport']:
            d_airport = request.form['departure_airport']
            appendix += "and departure_airport_name = '"
            appendix += d_airport
            appendix += "' "
        if request.form['arrival_airport'] :
            a_airport = request.form['arrival_airport'] 
            appendix += "and arrival_airport_name = '"
            appendix += a_airport
            appendix += "' "
    
        query += appendix
        #cursor used to send queries
        cursor = conn.cursor()
        #executes query	
        cursor.execute(query,session['username'])
        data = cursor.fetchall()
        cursor.close()
        return render_template("agent_home.html",search_flight = data, month_money = month_money, tnum = tnum, average_commission = average_commission,
            halfdata = halfdata, yeardata = yeardata, image1 = image1, image2 = image2)
    except:
        return render_template("agent_home.html",search_flight = data, month_money = month_money, tnum = tnum, average_commission = average_commission,
            halfdata = halfdata, yeardata = yeardata, image1 = image1, image2 = image2)

@app.route("/agent/flight_purchase/<agent_email>/<flight_num>/<airline_name>",methods=["GET", "POST"])
def agent_purchase(agent_email, flight_num, airline_name):
    
    if session['username'] != agent_email:
        return render_template("upcoming_flight.html", error1="Bad Request: username does not match")

    if airline_name not in session['company']:
        return render_template("upcoming_flight.html", error1="Bad Request: You do not have permission to buy ticket from this airline.")

    # get the customer email
    customer_email = request.form["customer_email"]

    #check if it is a valid email
    query = """select customer_email from customer WHERE customer_email = %s"""
    cursor = conn.cursor()
    cursor.execute(query, (customer_email))
    fetchemail =  cursor.fetchone()
    
    if not (fetchemail):
        return render_template("upcoming_flight.html", error1="Bad Request: customer does not exist")

    #get booking agent id
    query = """select booking_agent_id from booking_agent WHERE booking_agent_email = %s"""
    cursor = conn.cursor()
    cursor.execute(query, (agent_email))
    agent_id =  cursor.fetchone()
    agent_id = agent_id["booking_agent_id"]

    # if I had already buy the ticket
    query = """select * from ticket 
        where flight_num = %s
        AND customer_email = %s"""
    cursor = conn.cursor()
    cursor.execute(query, (flight_num, customer_email))
    data =  cursor.fetchall()
    cursor.close()

    # if there is no seats left
    query = """select seats from airplane where airline_name = %s
    and airplane_id in (select airplane_id from flight where airline_name = %s and flight_num = %s)"""
    cursor = conn.cursor()
    cursor.execute(query,(airline_name, airline_name, flight_num))
    totalSeats =  cursor.fetchone()
    totS = totalSeats['seats']
    cursor.close()

    query = """SELECT count(*)
        FROM ticket
        WHERE airline_name = %s
        AND flight_num = %s"""
    cursor = conn.cursor()
    cursor.execute(query,(airline_name, flight_num))
    soldSeats =  cursor.fetchone()
    sldS = soldSeats['count(*)']
    cursor.close()
    
    if sldS == totS:
        print('NO SEATS: soldSeats == totalSeats')
        return render_template("upcoming_flight.html", search_flight = session['agentdata'], error1 = "No seats left for the flight.")
#      return render_template("upcoming_flight.html", search_flight = session['agentdata'], month_money = session['month_money'], tnum = session['tnum'], average_commission = session['averagecommission'],
#           halfdata = session['halfdata'], yeardata = session['yeardata'], image1 = session['image1'], image2 = session['image2'], error1 = "No seats left for the flight.")
    elif data:
        print("Now we are here 5")
        return render_template('agent_home.html', search_flight = session['agentdata'], status = "You have already bought the ticket")
#return render_template("upcoming_flight.html", search_flight = session['agentdata'], month_money = session['month_money'], tnum = session['tnum'], average_commission = session['averagecommission'],
#           halfdata = session['halfdata'], yeardata = session['yeardata'], image1 = session['image1'], image2 = session['image2'], status = "You have already bought the ticket")
    else:
        # if I haven't buy the ticket
        query = "select max(ticket_id) from ticket"
        cursor = conn.cursor()
        cursor.execute(query)
        data = cursor.fetchall()
        cursor.close()
        if data:
            ticket_id = data[0]["max(ticket_id)"]+1
        else:
            ticket_id = 1
        cursor = conn.cursor()
        query1 = "insert into ticket values(%s, %s, %s, %s, %s, %s)"
        cursor.execute(query1,(ticket_id, airline_name, flight_num, customer_email, agent_email, datetime.datetime.now().strftime('%Y-%m-%d')))
        cursor.close()
        conn.commit()
        return render_template('agent_home.html', search_flight = session['agentdata'], status = "You have successfully buy the ticket!")
#       return render_template("upcoming_flight.html", search_flight = session['agentdata'], month_money = session['month_money'], tnum = session['tnum'], average_commission = session['averagecommission'],
#           halfdata = session['halfdata'], yeardata = session['yeardata'], image1 = session['image1'], image2 = session['image2'], status = "You have successfully buy the ticket!")

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
@app.route('/airline_staff_home_admin',methods=["GET", "POST"])
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
    
    
    