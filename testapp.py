import oracledb
from flask import Flask, render_template, url_for, request, redirect

app = Flask(__name__)
def get_credentials_from_file(profile):
    with open('config.txt', 'r') as f:
        lines = f.readlines()
        for line in lines:
            if profile in line:
                parsed = line.split('|')
                app.config['ORACLE_USER'] = parsed[1]
                app.config['ORACLE_PASSWORD'] = parsed[2]
                app.config['ORACLE_DSN'] = parsed[3]

def connect_db():
    #get_credentials_from_file('Default')
    try:
        connection = oracledb.connect(user='ADMIN',password='S0s-it-0racle',dsn='(description= (retry_count=20)(retry_delay=3)(address=(protocol=tcps)(port=1522)(host=adb.eu-frankfurt-1.oraclecloud.com))(connect_data=(service_name=g174432cd8ec6d2_basedatabase_low.adb.oraclecloud.com))(security=(ssl_server_dn_match=yes)))')
        return connection
    except Exception as e:
        return e

def disconnect_db(connection):
    connection.close()

def upload_data(data, connection, cursor):
    try:
        cursor.execute(data)
        connection.commit()
    except oracledb.Error as error:
        print(error)
        connection.rollback()

def get_data(data, cursor):
    try:
        toFetch = cursor.execute(data)
        fetched = toFetch.fetchall()
        return fetched
    except oracledb.Error as error:
        print(error)

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        app.config['ORACLE_USER'] = request.form['username']
        app.config['ORACLE_PASSWORD'] = request.form['password']
        app.config['ORACLE_DSN'] = request.form['dsn']
        #connection = connect_db()
        # if not connection:
        #     return redirect('/')
        # else:
        return redirect('/main')
    else:
        return render_template('login.html', tasks=[])

@app.route('/main', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        task_content = request.form['content']
        action = "INSERT INTO Tasks (task_name) VALUES ('{}')".format(task_content)
        connection = connect_db()
        cursor = connection.cursor()
        upload_data(action, connection, cursor)

        return redirect('/main')

    else:
        action = "SELECT * FROM Tasks"
        connection = connect_db()
        cursor = connection.cursor()
        data = get_data(action, cursor)

        return render_template('index.html', tasks=data)

@app.route('/delete/<int:task_id>')
def delete(task_id):
    action = "DELETE FROM Tasks WHERE task_id='{}'".format(task_id)
    connection = connect_db()
    cursor = connection.cursor()
    upload_data(action, connection, cursor)
    return redirect('/main')
@app.route('/edit/<int:task_id>', methods=['GET', 'POST'])
def edit(task_id):
    connection = connect_db()
    cursor = connection.cursor()
    action = "SELECT * FROM Tasks WHERE task_id='{}'".format(task_id)
    task = get_data(action, cursor)
    if request.method == 'POST':
        new_content = request.form['content']
        action = "UPDATE Tasks SET task_name='{}' WHERE task_id = '{}' ".format(new_content,task_id)
        upload_data(action, connection, cursor)
        return redirect('/main')
    else:
        return render_template('edit.html', task=task[0])

if __name__ == '__main__':
    app.run()