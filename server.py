from flask import Flask, request, redirect, render_template, session, flash
from mysqlconnection import MySQLConnector
import re
import md5
app = Flask(__name__)    
app.secret_key = 'KeepItSecretKeepItSafe'
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
NAME_REGEX = re.compile(r'^[a-zA-Z]+$')
mysql = MySQLConnector(app,'thewall')

@app.route('/')         
def index_page():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    login_count=0
    if len(request.form['login_email']) <1:
        flash("Email Cannot Be Empty!")
        return redirect('/')
    elif not EMAIL_REGEX.match(request.form['login_email']):
        flash("Invalid Email!")
        return redirect('/')
    else: 
        login_email = request.form['login_email']
        login_count+=1
        # print "Got Info", login_email
    
    if len(request.form['login_password']) <2:
        flash("Invalid Password!")
        return redirect('/')
    else:
        login_password = md5.new(request.form['login_password']).hexdigest()
        query = "SELECT * FROM users WHERE users.email = :login_email AND users.password = :login_password"
        data = {
            'login_email': login_email,
            'login_password': login_password
        }
        check = mysql.query_db(query, data)
        if len(check) >0:
            login_count+=1
            # print "Got Info", login_password
            if login_count == 2:
                session['login_email']=request.form['login_email']
                query = "SELECT users.id from users WHERE users.email = :login_email"
                data = {
                    'login_email': login_email
                    }
                session['user_id'] = mysql.query_db(query, data)
                return redirect('/wall')
        else: 
            flash("Incorrect Password!")
            return redirect('/')

@app.route('/register', methods=['POST'])
def register():
    count =0
    if len(request.form['first_name']) <2:
        flash("First Name Cannot Be Empty!")
        return redirect('/')
    elif not NAME_REGEX.match(request.form['first_name']):
        flash("Invalid First Name!")
        return redirect('/')
    else:
        first_name = request.form['first_name']
        count += 1
        # print "Got Info", first_name   

    if len(request.form['last_name']) <2:
        flash("Last Name Cannot Be Empty!")
        return redirect('/')
    elif not NAME_REGEX.match(request.form['last_name']):
        flash("Invalid Last Name!")
        return redirect('/')
    else:
        last_name = request.form['last_name']
        count += 1
        # print "Got Info", last_name

    if len(request.form['email']) <1:
        flash("Email Cannot Be Empty!")
        return redirect('/')
    elif not EMAIL_REGEX.match(request.form['email']):
        flash("Invalid Email!")
        return redirect('/')
    else: 
        email = request.form['email']
        count += 1
        # print "Got Info", email

    if len(request.form['password']) <8:
        flash("Invalid Password!")
        return redirect('/')
    else:
        print "Got Info"

    if request.form['password_confirm'] == request.form['password']:
        password = md5.new(request.form['password']).hexdigest()
        count += 1
    else:
        flash("Password does not match!")
        return redirect('/')

    if count == 4:
        query = "INSERT INTO users(id, first_name, last_name, email, password, created_at, updated_at) VALUES(ID, :first_name,:last_name,:email,:password,NOW(),NOW())"
        data = {
                'first_name': first_name,
                'last_name': last_name,
                'email': email,
                'password': password
            }
        mysql.query_db(query, data)
        flash("Successfully Registered!")
        return redirect('/')

@app.route('/wall')
def user_wall():
    user_id=session['user_id'][0]['id']
    print user_id
    query1 = "SELECT messages.id, messages.message,messages.created_at, CONCAT(users.first_name,' ', users.last_name) AS name FROM messages JOIN users ON users.id = messages.users_id"
    query2 = "SELECT comments.messages_id, comments.id, comments.comment,DATE_FORMAT(comments.created_at, '%M %d %Y')as date,CONCAT(users.first_name,' ', users.last_name) AS name FROM comments JOIN users ON users.id = comments.users_id"
    query3 = "SELECT CONCAT(users.first_name,' ', users.last_name) as name FROM users WHERE users.id = :user_id"
    data = {
        'user_id': user_id
    }
    user_message = mysql.query_db(query1)
    user_comment = mysql.query_db(query2)
    user_name = mysql.query_db(query3, data)
    print user_name[0]['name']
    return render_template('wall.html', message_list=user_message, comment_list=user_comment, user_name=user_name[0]['name'])

@app.route('/add_message', methods=['POST'])
def add():
    message_box = request.form['message_box']
    id_check = session['user_id'][0]['id']
    query = "INSERT INTO messages(message,created_at,updated_at,users_id) VALUES( :message_box,NOW(),NOW(),:id)"
    data = {
            'message_box': message_box,
            'id': id_check
            }
    user_message = mysql.query_db(query, data)
    return redirect('/wall')

@app.route('/add_comment', methods=['POST'])
def insert():
    comment_box = request.form['comment_box']
    # print comment_box
    id_check = session['user_id'][0]['id']
    # print id_check
    query = "INSERT INTO comments(comment,created_at,updated_at,users_id,messages_id) VALUES( :comment_box,NOW(),NOW(),:id,:m_id)"
    data = {
            'comment_box': comment_box,
            'id': id_check,
            'm_id':request.form['m_id']
            }
    mysql.query_db(query, data)
    return redirect('/wall')

@app.route('/logoff')
def logout():
    return redirect('/')

app.run(debug=True)