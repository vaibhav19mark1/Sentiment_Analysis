# pip install mysql-connector-python

from flask import Flask, render_template, request, redirect, session
import mysql.connector
from sentiments import second
import os

app = Flask(__name__)

# initializing the use cookie
app.secret_key = os.urandom(24)

# blueprint to call the second python file
app.register_blueprint(second)

# establishing connection with mysql database made in xampp
try:
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="users"
    )
    cursor = conn.cursor()
except:
    print("Connection cannot be established with the database")

# --------------------creating routes-----------------------------------

# 1. login template


@app.route('/')
def login():
    return render_template('login.html')


# 2. register template
@app.route('/register')
def register():
    return render_template('register.html')


# 3. home template
@app.route('/home')
def home():
    if 'user_id' in session:
        return render_template('home.html')
    else:
        return redirect('/')


# 4. login validation
@app.route('/login_validation', methods=['POST'])
def login_validation():
    email = request.form.get('email')
    password = request.form.get('password')

    cursor.execute(
        """ select * from `users` 
            where `email` like '{}' and `password` like '{}' """.format(email, password)
    )
    users = cursor.fetchall()
    # checking if already logged in
    if len(users) > 0:
        session['user_id'] = users[0][0]
        return redirect('/home')
    else:
        return redirect('/login')


# 5. addUser
@app.route('/add_user', methods=['POST'])
def add_user():

    # get user login data and pass it to database
    name = request.form.get('uname')
    email = request.form.get('uemail')
    password = request.form.get('upassword')
    cursor.execute(
        """insert into `users` (`username`,`email`,`password`)
           values ('{}','{}','{}')""".format(name, email, password)
    )
    conn.commit()
    cursor.execute(
        """select * from `users` where `email` like '{}'""".format(email)
    )
    myuser = cursor.fetchall()
    session['user_id'] = myuser[0][0]
    return redirect('/home')


# 6. logout
@app.route('/logout')
def logout():
    # closing the session
    session.pop('user_id')
    return redirect('/')


if __name__ == "__main__":
    app.run(debug=True)
