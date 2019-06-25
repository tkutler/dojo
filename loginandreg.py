from flask import Flask, render_template, request, redirect, session, flash
from mysqlconnection import connectToMySQL
from flask_bcrypt import Bcrypt 
app = Flask(__name__)
bcrypt= Bcrypt(app)
import re
app.secret_key = "I am a secret key" 
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
db ="dojoreads"



@app.route('/')
def index():
    return render_template("index.html")
@app.route('/register', methods= ["POST"])
def register():
    mysql = connectToMySQL(db)
        
    if len(request.form['first']) < 1:
    	flash("Please enter a valid first name")
    if len(request.form['last']) <1:
        flash("Please enter valid last name") 
    if len(request.form["password"]) < 1:
        flash("password lenth must be more than 0 ")
    if len(request.form["passwordconfirm"]) < 1:
        flash("password lenth must be more than 0 ")
    if request.form['password'] != request.form['passwordconfirm']:
        flash ("passsword does not match")
    if not EMAIL_REGEX.match(request.form['email']):
        flash("Invalid email address!")
    if '_flashes' in session.keys():
        return redirect("/")
    if not '_flashes' in session.keys(): 
        pw_hash = bcrypt.generate_password_hash(request.form['password'])
        
        query = "INSERT INTO users (first, last, email, password) VALUES (%(first)s, %(last)s, %(email)s, %(pw)s); "
        data = {
            "first": request.form["first"],
            "last": request.form["last"],
            "email": request.form["email"],
            "pw": pw_hash
        }
        userid = mysql.query_db(query,data)
        session['userid'] = userid
        mysql = connectToMySQL(db)
        query = "SELECT first FROM users WHERE iduser =" + str(userid)+";"
        username = mysql.query_db(query,data)
        session["username"] = username[0]['first']
        return redirect ("/success")
@app.route("/login", methods = ["POST"]) 
def login():
    mysql = connectToMySQL(db)
    query = "SELECT * FROM users WHERE email = %(email)s;"
    data = {
        "email" : request.form['userlogin']
    }
    users = mysql.query_db(query, data)
    
    
    if users: 
        if bcrypt.check_password_hash(users[0]['password'], request.form['passwordlogin']):
            session['userid'] = users[0]['iduser']
            session['username'] = users[0]['first']
            print("password found")
            return redirect ('/success')
        else: 
            flash("not successful")
            print("password not found")
            return redirect ("/")
    else: 
        flash("not successful") 
        print("email not found")  
        return redirect ("/")    

@app.route("/success")
def success():
    mysql = connectToMySQL(db)
    query = "SELECT * FROM reviews JOIN users on iduser = reviewer_id join books on idbook = book_id"
    allreviews= mysql.query_db(query)

    return render_template("login.html", allreviews = allreviews) 
@app.route('/logout')
def logout():
    session.clear()
    print('you are logged out')
    return redirect ('/') 
@app.route('/toaddpage')
def showaddpage():
    return render_template("add.html")
@app.route("/add", methods = ["POST"])
def addbook():
    mysql = connectToMySQL(db)
    query = "INSERT into books (title, author, submitter) values (%(title)s, %(author)s, %(submitter)s);"
    data = {
        "title" : request.form["title"],
        "author" : request.form["author"],
        "submitter": request.form["submitter"]
    }
    newbook = mysql.query_db(query,data)
    print(newbook)
    mysql = connectToMySQL(db)
    query = "insert into reviews(review, rating,book_id, reviewer_id) Values (%(review)s, %(rating)s, %(books_id)s,%(reviewer_id)s)"
    data = {
        "review": request.form["review"],
        "rating": request.form["rating"],
        "books_id": newbook,
        "reviewer_id": request.form["reviewerid"]
    }
    newreview = mysql.query_db(query,data)
    return redirect ("/book/" + str(newbook))

@app.route("/book/<id>")
def bookinfo(id):
    print("bookid route")
    mysql = connectToMySQL(db) 
    query = "select * from books where idbook = "+ id + ";" 
    bookpick = mysql.query_db(query) 
    print (bookpick)
    mysql = connectToMySQL(db)  
    query = "select * from reviews join users on iduser =reviewer_id where book_id = "+ id + ";"
    bookreviews = mysql.query_db(query)
    print(bookreviews)
    return render_template("info.html", bookpick = bookpick[0], bookreviews = bookreviews) 

@app.route('/addreview', methods = ["POST"])
def addreview(): 
    mysql = connectToMySQL(db) 
    query = "insert into reviews (review, rating,book_id, reviewer_id) values (%(review)s, %(rating)s, %(book_id)s,%(reviewer_id)s);"
    data = {
        "review": request.form['review'],
        "rating" : request.form ["rating"],
        "book_id" : request.form ["bookid"],
        "reviewer_id" : request.form ['reviewerid']
    }
    formreview = mysql.query_db(query,data)
    return redirect ('/toaddpage')
@app.route('/user/<id>')
def userpage(id): 
    mysql = connectToMySQL(db)
    query = "SELECT * FROM reviews JOIN users on iduser = reviewer_id join books on idbook = book_id where iduser =" + id + ";"
    userinfo = mysql.query_db(query)
    rnum =len(userinfo)
    return render_template ("userinfo.html", userinfo = userinfo, rnum= rnum)




    


    

















if __name__ == "__main__":
    app.run(debug=True)