import os
from flask import Flask, render_template, url_for,flash, redirect, request, session,jsonify
from flask_sqlalchemy import SQLAlchemy
import mysql.connector




# Config files for the app
app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_DATABASE'] = 'zoo'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '1234'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:1234@localhost/zoo'
db = SQLAlchemy(app)
app.secret_key = os.urandom(24)


def connect():
    conn = mysql.connector.connect(
        host=app.config['MYSQL_HOST'],
        database=app.config['MYSQL_DATABASE'],
        user=app.config['MYSQL_USER'],
        password=app.config['MYSQL_PASSWORD']
    )
    return conn
class addanimal(db.Model):
    animalid = db.Column(db.Integer, primary_key=True)
    AnimalName = db.Column(db.String(20), nullable=False)
    Scientificname = db.Column(db.String(20), nullable=False)
    Diet = db.Column(db.String(120), nullable=False)
    Avglifespan = db.Column(db.Integer, nullable=True)
    Size = db.Column(db.Integer, nullable=False)
    Weight=db.Column(db.Integer, nullable=False)
    About=db.Column(db.String(20), nullable=False)
    Behavior=db.Column(db.String(20), nullable=False)
    Facts=db.Column(db.String(20), nullable=False)
    Imageurl=db.Column(db.String(20), nullable=False)
    Sourceofinfoentered=db.Column(db.String(20), nullable=False)

class login3(db.Model):
    username = db.Column(db.String(20), primary_key=True)
    password = db.Column(db.Integer, nullable=False)
class doctor(db.Model):
    doct_id = db.Column(db.Integer, primary_key=True)
    doct_name = db.Column(db.String(20), nullable=False)
    animalid = db.Column(db.Integer, nullable=False)
    phone_no = db.Column(db.Integer, nullable=False)

class ticket(db.Model):
    cust_id = db.Column(db.Integer, primary_key=True)
    cust_name = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(20), nullable=False)
    phone_no = db.Column(db.Integer, nullable=False)
    username=db.Column(db.String(20), nullable=False)


# Route for Default view
@app.route("/")
@app.route("/welcome")
def welcome():
    return render_template('welcome.html')

@app.route('/home')
def home():
    # Variable animals set for displaying actual number from db 
    #animals=mongo.db.animals.count()
    username=session.get('username')
    if username=="Default":
        conn = connect()
        cursor = conn.cursor()
        query = "SELECT COUNT(*) FROM addanimal;"  # Replace 'your_table' with your table's name
        cursor.execute(query)
        row_count = cursor.fetchone()[0]
        username="Default"
        conn.close()
        return render_template('index.html',title='Home',row_count=row_count,username=username)
    else:
        conn = connect()
        cursor = conn.cursor()
        query = "SELECT COUNT(*) FROM addanimal;"  # Replace 'your_table' with your table's name
        cursor.execute(query)
        row_count = cursor.fetchone()[0]
        conn.close()
        return render_template('index.html',title='Home',row_count=row_count,username=username)     

   

#----- CRUD OPERATIONS -----

# Create #
# Route for new animal view- for adding new animal to the mongoDB   
@app.route('/new',methods=['GET','POST'])
def new_animal():
    username=session.get('username')
    if username!='Default' :
                if(request.method=='POST'):
                        animalid = request.form.get('animalid')
                        common_name = request.form.get('common_name')
                        scientific_name = request.form.get('scientific_name')
                        diet = request.form.get('diet')
                        avg_lifespan = request.form.get('avg_lifespan')
                        size = request.form.get('size')
                        weight=request.form.get('weight')
                        about=request.form.get('about')
                        behavior=request.form.get('behavior')
                        facts=request.form.get('facts')
                        img=request.form.get('img')
                        source=request.form.get('source')
                        data=addanimal(animalid=animalid,AnimalName=common_name,Scientificname=scientific_name,Diet=diet, Avglifespan= avg_lifespan,Size=size,Weight=weight,About=about,Behavior=behavior,Facts=facts,Imageurl=img,Sourceofinfoentered=source)
                        db.session.add(data)
                        db.session.commit()
                return render_template('new_animal.html',title='Add new Animal')
    else:
                  return render_template('new_animal.html',title='Add new Animal')
            
   

## READ ##
#  Route for Animals view with all animals pulled from mongoDB displayed
@app.route('/animals',methods=['GET','POST','DELETE'])
def animals():
    if request.method == 'POST':
        try:
            # Handle the DELETE request for deleting a doctor
            conn = connect()
            cursor = conn.cursor()

            data = request.get_json()
            animalid = data['animalid']
            query = "DELETE FROM addanimal WHERE animalid = %s;"
            cursor.execute(query, (animalid,))
            conn.commit()
            conn.close()
            return jsonify({'message': 'ANIMAL DELETED'})

        except Exception as e:
            # Handle any exceptions that might occur during deletion
            return jsonify({'message': 'Error deleting ANIMAL', 'error': str(e)}), 500
    
    else:
        # Handle the GET request to display doctors
        try:
            conn = connect()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM addanimal")
            rows = cursor.fetchall()
            column_names = [desc[0] for desc in cursor.description]
            conn.close()
            return render_template('animals.html', rows=rows, column_names=column_names)

        except Exception as e:
            # Handle any exceptions that might occur during data retrieval
    
            return jsonify({'message': 'Error retrieving doctors', 'error': str(e)}), 500

# Route for viewing a single animal page
@app.route('/animal/<animal_id>')
def animal():
	return render_template('animal.html', animal=animal, title=animal['common_name'])

## UPDATE ##
#  Route for editing existing animal
#  After selecting edit-animal, id-based data are transfered from mongo and populated in the form ready for editing
@app.route('/edit_animal/<animal_id>')
def edit_animal():
    return render_template('edit_animal.html', animal=animal,title='Edit Animal')

# Function called after submitting form for updating animal in mongoDB
@app.route('/update_animal/<animal_id>', methods=['GET','POST'])
def update_animal():

    flash(f'Successfuly Updated!', 'success')
    return redirect(url_for('animals'))

## REMOVE ##
#  Route for removing animal from the database
@app.route('/delete_animal/<animal_id>')
def delete_animal(animal_id):
    flash(f'Successfuly Removed!', 'danger')
    return redirect(url_for('animals'))

#  Form from forms.py used for both login and register page
def contains_digit(s):
    return any(char.isdigit() for char in s)

def is_valid_username(username):
    return len(username) <= 10 and contains_digit(username)
# For registering new users
# Use of bcrypt for hashing passwords (hashed password stored in db)
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not is_valid_username(username):
            session['username'] = "Default"
            session['error']="Not fit for trigger"
            return render_template('login.html')

        conn = connect()
        cursor = conn.cursor()

        query = f"SELECT * FROM login3 WHERE username = '{username}' AND password = '{password}'"
        cursor.execute(query)
        result = cursor.fetchone()
        conn.close()

        if result:
            session['username'] = username
            session['error']="login successfull"
        else:
            session['username'] = "Default"
            session['error']="Not found in database"

        return render_template('login.html')
    else:
        session['username']="Default"
        session['error']="Not found in database"
        return render_template('login.html')
@app.route('/register', methods=['GET','POST'])
def register():
    if(request.method=='POST'):
        username= request.form.get('username')
        password = request.form.get('password')
        if not is_valid_username(username):
            session['username'] = "Default"
            session['error']="Not fit for trigger"
            return render_template('register.html')
        data=login3(username=username,password=password)
        db.session.add(data)
        db.session.commit()

    return render_template('register.html')

# Account page with user info tbc.....
       # Route for handling doctors
@app.route('/doctors', methods=['GET', 'POST', 'DELETE'])
def doctors():
    if request.method == 'POST':
        try:
            # Handle the DELETE request for deleting a doctor
            conn = connect()
            cursor = conn.cursor()

            data = request.get_json()
            doct_id = data['doct_id']
            query = "DELETE FROM doctor WHERE doct_id = %s;"
            cursor.execute(query, (doct_id,))
            conn.commit()
            conn.close()
            return jsonify({'message': 'Doctor deleted successfully'})

        except Exception as e:
            # Handle any exceptions that might occur during deletion
            return jsonify({'message': 'Error deleting doctor', 'error': str(e)}), 500
    
    else:
        # Handle the GET request to display doctors
        try:
            conn = connect()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM doctor")
            rows = cursor.fetchall()
            column_names = [desc[0] for desc in cursor.description]
            conn.close()
            return render_template('doctors.html', rows=rows, column_names=column_names)

        except Exception as e:
            # Handle any exceptions that might occur during data retrieval
            return jsonify({'message': 'Error retrieving doctors', 'error': str(e)}), 500

@app.route('/account')
def account():
    return render_template('account.html',title='Your Account')   

@app.route('/tickets',methods=['POST','GET'])
def tickets():
    if(request.method=='POST'):
        cust_id = request.form.get('cust_id')
        name = request.form.get('name')
        email = request.form.get('email')
        phno=request.form.get('phno')
        username=session.get('username')
        data=ticket(cust_id=cust_id,cust_name=name,email=email,phone_no=phno,username=username)
        db.session.add(data)
        db.session.commit()

    return render_template('ticket.html') 

@app.route('/done')
def book():
    return render_template('bookinddone.html')  
@app.route('/relations')
def relation():
                conn = connect()
                cursor = conn.cursor()
                doct_name='Dr.Smith'
                query = "SELECT d.doct_id, a.animalid, d.doct_name, a.animalname FROM addanimal a INNER JOIN doctor d ON a.animalid = d.animalid WHERE d.doct_name like %s"
                cursor.execute(query, (doct_name,))
                rows = cursor.fetchall()
                column_names = [desc[0] for desc in cursor.description]
                conn.close()
                return render_template('relations.html', rows=rows, column_names=column_names)     


@app.route('/ticket-info')
def ticket():
                conn = connect()
                cursor = conn.cursor()
                query = "SELECT username, cust_id, cust_name, email FROM ticket WHERE username IN (SELECT username FROM login3);"
                cursor.execute(query)
                rows = cursor.fetchall()
                column_names = [desc[0] for desc in cursor.description]
                conn.close()
                return render_template('ticket-info.html', rows=rows, column_names=column_names)     

@app.route('/status')
def status():
                conn = connect()
                cursor = conn.cursor()
                query = "SELECT a.AnimalName, a.Scientificname, c.caretaker_name, c.phone_no FROM addanimal a JOIN caretaker c ON a.animalid = c.animalid;"
                cursor.execute(query)
                rows = cursor.fetchall()
                column_names = [desc[0] for desc in cursor.description]
                conn.close()
                return render_template('status.html', rows=rows, column_names=column_names)  

@app.route('/reviews')
def reviews():
                conn = connect()
                cursor = conn.cursor()
                query = "SELECT a.AnimalName, a.Avglifespan, r.reviews FROM addanimal a JOIN Reviews1 r ON a.animalid = r.cust_id WHERE a.Avglifespan between 10 and 60;"
                cursor.execute(query)
                rows = cursor.fetchall()
                column_names = [desc[0] for desc in cursor.description]
                conn.close()
                return render_template('reviews.html', rows=rows, column_names=column_names)  

@app.route('/count')
def count():
                conn = connect()
                cursor = conn.cursor()
                query = "SELECT a.AnimalName, COUNT(r.reviews) AS review_count FROM addanimal a LEFT JOIN Reviews1 r ON a.animalid = r.cust_id GROUP BY a.AnimalName;"
                cursor.execute(query)
                rows = cursor.fetchall()
                column_names = [desc[0] for desc in cursor.description]
                conn.close()
                return render_template('count.html', rows=rows, column_names=column_names)
@app.route('/caretaker', methods=['POST','GET','DELETE'])
def caretaker():
    if request.method == 'POST':
            try:
            # Handle the DELETE request for deleting a doctor
                conn = connect()
                cursor = conn.cursor()

                data = request.get_json()
                animalid = data['animalid']
                query = "DELETE FROM caretaker WHERE animalid = %s;"
                cursor.execute(query, (animalid,))
                conn.commit()
                conn.close()
                return jsonify({'message': 'Doctor deleted successfully'})

            except Exception as e:
            # Handle any exceptions that might occur during deletion
                return jsonify({'message': 'Error deleting doctor', 'error': str(e)}), 500
    
    else:
        # Handle the GET request to display doctors
        try:
            conn = connect()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM caretaker")
            rows = cursor.fetchall()
            column_names = [desc[0] for desc in cursor.description]
            conn.close()
            return render_template('caretaker.html', rows=rows, column_names=column_names)

        except Exception as e:
            # Handle any exceptions that might occur during data retrieval
            return jsonify({'message': 'Error retrieving doctors', 'error': str(e)}), 500

    
        

if __name__ == '__main__':
    app.run(host=os.getenv('IP'), port=os.getenv('PORT'), debug=True)  