import re
from flask import Flask, render_template, request, session
import requests
import ibm_db


app = Flask(__name__)

app.secret_key = 'a'
conn = ibm_db.connect(
    "DATABASE= bludb ;HOSTNAME=125f9f61-9715-46f9-9399-c8177b21803b.c1ogj3sd0tgtu0lqde00.databases.appdomain.cloud;PORT=30426;SECURITY=SSL;SSLCertificate=DigiCertificate.crt;UID=cqc31977;PWD=ImVje7lzKyapTC0b;", '', '')
print('connected')


@app.route('/')
@app.route('/login', methods=['POST', 'GET'])
def login():
    global userid
    msg = ''

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        sql = "SELECT * FROM EVS WHERE username =? AND password=?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt, 1, username)
        ibm_db.bind_param(stmt, 2, password)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)
        print(account)
        if account:

            session['loggedin'] = True
            session['USERID'] = account['USERID']
            session['id'] = account['USERNAME']
            userid = account['USERNAME']
            session['username'] = account['USERNAME']
            msg = 'logged in successfully !'
            return render_template('home.html', msg=msg)
        else:

            msg = 'Incorrect username/password'
    return render_template('login.html', msg=msg)


@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST':
        # print('hi----------------------')
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        # print(username)
        sql = "SELECT * FROM EVS WHERE username =?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt, 1, username)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)
        print(account)
        if account:
            msg = 'Account already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = "Invalid email address !"
        else:
            sql = "SELECT count(*) FROM EVS"
            stmt = ibm_db.prepare(conn, sql)
            ibm_db.execute(stmt)
            length = ibm_db.fetch_assoc(stmt)
            print(length)
            insert_sql = "INSERT INTO EVS VALUES (?,?,?,?)"
            prep_stmt = ibm_db.prepare(conn, insert_sql)
            ibm_db.bind_param(prep_stmt, 1, length['1']+1)
            ibm_db.bind_param(prep_stmt, 2, username)
            ibm_db.bind_param(prep_stmt, 3, email)
            ibm_db.bind_param(prep_stmt, 4, password)
            ibm_db.execute(prep_stmt)
            msg = 'you have successfully registered !'
            return render_template('login.html', msg=msg)
    elif request.method == 'POST':
        msg = 'Please fill out the form!'
    return render_template('signup.html', msg=msg)


@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return render_template('login.html')

@app.route("/home", methods=['POST', 'GET'])
def index2():
    return render_template("index.html")

@app.route("/address1", methods=['POST', 'GET'])
def index3():
    output=[]
    return render_template("home.html",output=output)

@app.route("/address", methods=['POST', 'GET'])
def address():
    outputs1=[]
    output=[]
    if request.method == 'POST':
        #     # process GET request
        #     return render_template('home.html')
        # else:
        # process POST request
        address = request.form['address']

        # make API requests to get latitude and longitude from address
        url = "https://address-from-to-latitude-longitude.p.rapidapi.com/geolocationapi"
        querystring = {"address": address}
        headers = {
            "X-RapidAPI-Key": "d73283ca42msh25142662f0dd1eap11bde4jsnbe1a5c63f516",
            "X-RapidAPI-Host": "address-from-to-latitude-longitude.p.rapidapi.com"
        }
        response = requests.get(url, headers=headers, params=querystring)
        outputs1 = response.json()
        print(outputs1)
        print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")

        # make API request to get charging stations from latitude and longitude
        if 'Results' in outputs1:
            latitude = outputs1['Results'][0]['latitude']
            longitude = outputs1['Results'][0]['longitude']
            url1 = "https://ev-charge-finder.p.rapidapi.com/search-by-coordinates-point"
            querystring1 = {"lat": latitude, "lng": longitude}
            headers1 = {
                "X-RapidAPI-Key": "bbba8d02edmshd26eaa86314e163p16f673jsnaca266aea033",
                "X-RapidAPI-Host": "ev-charge-finder.p.rapidapi.com"
            }
            response1 = requests.request("GET", url1, headers=headers1, params=querystring1)
            output = response1.json()
            print(output)
        else:
            output = []

        return render_template("home.html", outputs1=outputs1, output=output)


if __name__ == "__main__":
    app.run(debug=True)
