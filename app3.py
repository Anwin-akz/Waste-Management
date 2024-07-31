from flask import Flask, render_template, request, redirect, url_for
from flask_pymongo import PyMongo

app = Flask(__name__)
app.config['MONGO_URI'] = 'mongodb://localhost:27017/delivary'
mongo = PyMongo(app)
users_collection = mongo.db.users
employee_collection = mongo.db.employee
admin_collection = mongo.db.admin
update_collection = mongo.db.update
feedback_collection = mongo.db.feedback
tasks_collection = mongo.db.tasks


class DeliveryData:
    def __init__(self, status, date,house_number,ward_number,name):
        self.status = status
        self.date = date
        self.house_number = house_number
        self.ward_number = ward_number
        self.name = name


@app.route('/')
def home():
    return render_template('index.html')
    
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Search for the user in the appropriate collection based on their role
        user = mongo.db.users.find_one({'username': username, 'password': password})
        if not user:  # If user not found in 'users' collection
            user = mongo.db.employee.find_one({'username': username, 'password': password})
        if not user:  # If user not found in 'employee' collection
            user = mongo.db.admin.find_one({'username': username, 'password': password})
            
        if user:
            role = user.get('role')  # Retrieve the role of the user
            if role == 'admin':
                return redirect(url_for('admin_dashboard'))
            elif role == 'employee':
                return redirect(url_for('employee_dashboard'))
            else:
                return redirect(url_for('user_dashboard'))
        else:
            return 'Invalid username or password'# Your login logic here
    else:
        return render_template('registration.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        role = request.form['role']  # Get the selected role from the form
        if password != confirm_password:
            return 'Passwords do not match'
        existing_user = mongo.db.users.find_one({'username': username})
        if existing_user:
            return 'Username already exists'
        
        # Insert the user into the appropriate collection based on their role
        if role == 'admin':
            mongo.db.admin.insert_one({'name': name, 'username': username, 'password': password, 'role': role})
        elif role == 'employee':
            mongo.db.employee.insert_one({'name': name, 'username': username, 'password': password, 'role': role})
        else:
            mongo.db.users.insert_one({'name': name, 'username': username, 'password': password, 'role': role})
        
        return redirect(url_for('login'))# Your signup logic here
    else:
        return render_template('signup.html')

@app.route('/admin')
def admin_dashboard():
    return render_template('admin.html')

@app.route('/employee')
def employee_dashboard():
    return render_template('employee.html')

@app.route('/user')
def user_dashboard():
    return render_template('user.html')

@app.route('/update')
def update_form():
    return render_template('update.html')

@app.route('/Responses')
def Responses():
    return render_template('responsemp.html')

@app.route('/Employee')
def Employee_Tasks():
    return render_template('task.html')


@app.route('/')
def update():
    return render_template('update.html')

@app.route('/submit', methods=['POST'])
def submit():
    status = request.form['status']
    date = request.form['date']
    house_number = request.form['house_number']
    ward_number = request.form['ward_number']
    name = request.form['name']

  # Create a DeliveryData object with the form data
    delivery_data = DeliveryData(status, date, house_number, ward_number, name)
        
        # Insert data into MongoDB
    update_collection.insert_one(delivery_data.__dict__)
        
    return 'Form submitted successfully!'




@app.route('/')
def responsemp():
    return render_template('responsemp.html')

@app.route('/submit_feedback', methods=['POST'])
def submit_feedback():
    name = request.form['name']
    email = request.form['email']
    feedback = request.form['feedback']
    complaint = request.form['complaint']

    # Insert data into MongoDB
    feedback_collection.insert_one({
        'name': name,
        'email': email,
        'feedback': feedback,
        'complaint': complaint
    })

    return 'Feedback submitted successfully!'



@app.route('/')
def task():
    return render_template('task.html')

@app.route('/schedule_task', methods=['POST'])
def schedule_task():
    task_name = request.form['task-name']
    employee = request.form['employee']
    due_date = request.form['due-date']

    # Insert data into MongoDB
    tasks_collection.insert_one({
        'task_name': task_name,
        'employee': employee,
        'due_date': due_date
    })

    return 'Task scheduled successfully!'



@app.route('/user_details')
def user_details():
    # Retrieve updates from the database as a list
    updates = list(update_collection.find())

    # Render the updates on the admin webpage
    return render_template('user_details.html', updates=updates)


@app.route('/responses')
def responses():
    # Retrieve feedback from the database
    feedback = list(feedback_collection.find())

    # Render the feedback on the admin webpage
    return render_template('responses.html', feedback=feedback)



@app.route('/schedules')
def schedules():
    # Retrieve tasks from the database
    tasks = tasks_collection.find()

    # Render the schedules on the employee webpage
    return render_template('schedules.html', tasks=tasks)






if __name__ == '__main__':
    app.run(debug=True)
