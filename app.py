from flask import Flask, request, Response, render_template, jsonify, redirect, url_for
from warrant import Cognito
import sys
import json
import mysql.connector
from mysql.connector import errorcode
import os

app = Flask(__name__)

# all configurations
os.environ['AWS_DEFAULT_REGION'] = "us-east-2"

mySQLConfig = {
	  'user': 'abhishek',
	  'password': '0000',
	  'host': '127.0.0.1',
	  'database': 'cs218imageportal_db',
	  'raise_on_warnings': True
	}

cognitoPoolID = 'us-east-2_4NELA3imh'
cognitoAppClient = '3kl9bhn4bst09fbpo3mc2s3mo6'
cognitoAccessKey = 'AKIA2VGGOTNNR26EU3XB'
cognitoSecretyKey = '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'

HEADER = {'Access-Control-Allow-Origin': '*'}

def printf(s):
	print(s, file=sys.stderr)

@app.route('/')
def index():
	printf ('In Home')
	return render_template('login.html')

@app.route('/signup', methods=['GET'])
def signUpPage():
	return render_template('signup.html')

@app.route('/signup', methods=['POST'])
def signUpProcess():
	printf ("In signup process")
	values = dict()
	email = request.form['email']
	username = request.form['username']
	password = request.form['password']
	print (username, email, password, file=sys.stderr)

	if username and email and password:
		printf ("Creating object for " + username)
		u = Cognito(cognitoPoolID,cognitoAppClient, access_key=cognitoAccessKey, 
			secret_key=cognitoSecretyKey)

		printf ("Cognito object created, trying to add user")
		u.add_base_attributes(email=email)
		try:
			u.register(username, password)
			values['success'] = "Account created for user " + username \
			+ ". Click on the link below to verify your email."
			printf ("Returning " + str(values))
			return jsonify(values)
		except Exception as e:
			printf ("Signup failed, Error: " +  str(e))
			values['error'] = str(e)
			return jsonify(values)


	printf ("Returning " + values)
	values['error'] = 'Please enter all the fields'
	return jsonify(values)

@app.route('/login', methods=['GET'])
def loginPage():
	return render_template('login.html')

@app.route('/login', methods=['POST'])
def loginProcess():
	printf("In login process")
	values = dict()
	username = request.form['username']
	password = request.form['password']
	printf("Username: " + username)
	u = Cognito(cognitoPoolID,cognitoAppClient, username=username)
	try:
		u.authenticate(password = password)
		printf("---------Authenticated-------------")
		values['success'] = "Logged in as " + username
		printf("ID_Token: " + u.id_token)
		return jsonify(values)
	except Exception as e:
		printf (e)
		values['error'] = str(e)
		return jsonify(values)

@app.route('/confirmUser')
def confirmUser():
	return render_template('confirmUser.html')

@app.route('/confirmUser', methods=['POST'])
def confirmUserProcess():
	printf("In confirm process")
	values = dict()
	username = request.form['username']
	code = request.form['code']
	u = Cognito(cognitoPoolID, cognitoAppClient)
	try:
		u.confirm_sign_up(code,username=username)
		printf("--------VERIFIED-----------")
		values['success'] = "Your account is verified, you can now log in"
		return jsonify(values)
	except Exception as e:
		printf (e)
		values['error'] = str(e)
		return jsonify(values)

@app.route('/check-status', methods=['GET'])
def verify():
	return 'service is up'
	
# @app.route('/welcome/<string:username>', methods=['GET'])
# def welcome(username):
# 	print('in Welcome',username, file=sys.stderr)
# 	values = {"Browser":"Chrome", "Names":username}
# 	return jsonify(values)
	
# @app.route('/welcome/add/<int:a>', methods=['POST'])
# def addNumbers():
# 	a = request.args.get('a', 0, type=int)
# 	b = request.args.get('a', 0, type=int)
# 	c = a+b
# 	print ("Sum is ",c, file=sys.stderr)
# 	values = {"result": c}
# 	return json.dumps(values)

# @app.route('/welcome/add/<int:a>', methods=['GET'])
# def addSelfNumbers(a):
# 	c = a + a
# 	print ("Sum is ",c, file=sys.stderr)
# 	values = {"sum": c}
# 	response = app.response_class(response=json.dumps(values),
#                                   status=200,
#                                   mimetype='application/json')
# 	return response
	
# @app.route('/process', methods=['POST'])
# def process():

# 	values = dict()
# 	email = request.form['email']
# 	name = request.form['name']

# 	if name and email:
# 		newName = name[::-1]
# 		values['name'] = newName
# 		print ("Returning", values, file=sys.stderr)
# 		#return json.dumps(values)
# 		return jsonify(values)

# 	print ("Returning", values, file=sys.stderr)
# 	values['error'] = 'Missing data!'
# 	return jsonify({'error' : 'Missing data!'})
# 	return json.dumps(values)

@app.route('/users', methods=['GET'])
def getUsers():

	try:
		cnx = mysql.connector.connect(**mySQLConfig)
		cursor = cnx.cursor()

	except mysql.connector.Error as err:
		if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
			printf("Invalid credentials")
		elif err.errno == errorcode.ER_BAD_DB_ERROR:
			printf("Database does not exist")
		else:
			printf(err)
		cnx.close()

	query = ("SELECT name,email FROM users")

	cursor.execute(query)

	values = dict()
	for name, email in cursor:
		values[name] = email

	response = app.response_class(response=json.dumps(values),
                                  status=200,
                                  mimetype='application/json')
	return response
	
# @app.route('/getCities', methods=['GET'])
# def getCities():
# 	import mysql.connector
# 	from mysql.connector import errorcode

# 	try:
# 	  cnx = mysql.connector.connect(**mySQLConfig)
# 	  cursor = cnx.cursor()

# 	except mysql.connector.Error as err:
# 	  if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
# 	    print("Something is wrong with your user name or password")
# 	  elif err.errno == errorcode.ER_BAD_DB_ERROR:
# 	    print("Database does not exist")
# 	  else:
# 	    print(err)
# 	  cnx.close()


# 	query = ("SELECT Name, CountryCode FROM city")

# 	cursor.execute(query)
# 	values = dict()

# 	for Name, CountryCode in cursor:
# 		values[Name] = CountryCode

# 	return jsonify(values)

if __name__ == '__main__':
	app.run(port='319', debug=True)