from flask import Blueprint, render_template, request, flash, url_for, redirect, session, jsonify, Markup
import sqlite3, json, os, requests, smtplib, uuid
from datetime import datetime
from bs4 import BeautifulSoup
from email.message import EmailMessage
from random import randint

auth = Blueprint('auth', __name__)
views = Blueprint('views',__name__)
otp=randint(000000,999999)


a = None
b = None
c = None
d = None
e = None


def email_alert(subject, body, to):
    msg = EmailMessage()
    msg.set_content(body)
    msg['subject'] = subject
    msg['to'] = to

    user = "fomostockmarket@gmail.com"
    msg['from'] = user
    password ="uwgudpbwnicdcuti"

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(user, password)
    server.send_message(msg)

    server.quit()

def email_support(subject, body, to):
    msg = EmailMessage()
    msg.set_content(body)
    msg['subject'] = subject
    msg['to'] = to

    user = "fomosspp@gmail.com"
    msg['from'] = user
    password ="hpqjvkcghufninji"

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(user, password)
    server.send_message(msg)

    server.quit()

@auth.route('/form', methods=["GET", "POST"])
def form():

    if request.method == 'POST':

        name = request.form.get("name")
        email = request.form.get("email")
        message = request.form.get("message")

        if len(email) < 4:
            flash("Please enter valid email.", category="e")
        
        else:
            email_alert("FOMO Support", "Thank you for reaching us! Dear "+str(name), email)
            email_support("Concern of our Dear"+str(name)+", "+str(email), str(message), "fomostockmarket@gmail.com")
        
        return redirect(url_for("views.index"))

    return render_template("landing-page.html")

@auth.route('/signup', methods = ['GET', 'POST'])
def signup():


    with sqlite3.connect("system.db") as con:
            cur = con.cursor()
            

    if request.method == 'POST':

        email = request.form.get('email')
        username = request.form.get('username')
        password =  request.form.get('password')
        password1 = request.form.get('password1')


        statement = f"SELECT * FROM User WHERE email='{email}';"
        cur.execute(statement)
        data = cur.fetchone()

        statement1 = f"SELECT * FROM User WHERE username='{username}';"
        cur.execute(statement1)
        data1 = cur.fetchone()
        
        if data:
            flash("This email was already taken.", category="e")
        
        elif data1:
            flash("This username was already taken.", category="e")
        
        elif len(username) < 6:
            flash("Username must be 6 characters.", category="e")

        elif len(email) < 4:
            flash("Please enter valid email.", category="e")

        elif len(password)< 8:
            flash("Password must be 8 characters.", category="e")

        elif not any(char.isupper() for char in password):
            flash('Password should have at least one uppercase letter.', category="e")

        elif not any(char.isdigit() for char in password):
            flash('Password should have at least one numeral.', category="e")
            
        elif password != password1:
            flash("Password does not match.", category="e")
        
        else:
            
            if not data:
                global a, b, c, d
                a = email
                b = password
                c = password1
                d = username

                email_alert("OTP", "Thank you for signing up, "+d+"!\nBelow is your OTP: \n"+str(int(otp)), email)             
                return redirect(url_for('auth.verify'))

        return redirect(url_for("auth.signup"))
    
    return render_template("signup.html")

@auth.route('/verify', methods = ['GET', 'POST'])
def verify():
    

    return render_template("verify.html")

@auth.route('/validate',methods = ['POST'])
def validate():
    con = sqlite3.connect('system.db')  
    con.row_factory = sqlite3.Row  
    cur = con.cursor()  

    user_otp=request.form['otp']
    global a, b, c, d

    if user_otp==str(otp):
        cur.execute("INSERT into User (email, password, password1, username) values (?,?,?,?)",(a,b,c,d))
        con.commit()
        flash("Successfully Registered.", category='s')
        return redirect(url_for('auth.login'))

    else:
        flash("Wrong OTP, please try again.", category="e")

    return render_template('verify.html')

@auth.route('/login', methods = ['GET', 'POST'])
def login():

    with sqlite3.connect("system.db") as con:
        cur = con.cursor()

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if request.form.get("username") == "admin@admin" and request.form.get("password") == "admin":
            session["admin"] = username
            
            return redirect(url_for("auth.dashboard"))

        statement = f"SELECT * FROM blockUser WHERE username='{username}';"
        cur.execute(statement)

        if cur.fetchone():
            flash(Markup('Sorry, your account has been blocked!, contact our support <a href="/#contact" class="alert-link">here</a>'), category="e")
            return redirect(url_for("auth.login"))
        
        statement = f"SELECT * FROM user WHERE username='{username}' AND password='{password}';"
        cur.execute(statement)


        if not cur.fetchone():
            flash("Your email or password was incorrect.", category="e")    
            return redirect(url_for("auth.login"))

        else: 
            session["email"] = username
            return redirect(url_for("auth.assets"))
        
    return render_template("login.html")

@auth.route('/forgot', methods = ["GET", "POST"])
def forgot():

    con = sqlite3.connect('system.db')  
    cur = con.cursor()  

    if request.method == 'POST':
        email = request.form["email"]
        token = str(uuid.uuid4())
        statement = f"SELECT * FROM User WHERE email='{email}';"
        cur.execute(statement)
        data = cur.fetchone()

        if data:
            cur.execute("UPDATE User SET token=? WHERE email=?", [token, email])
            con.commit()
            email_alert("Reset Password", "Hi there. To reset your password, click the link: fomostockpriceprediction.herokuapp.com/reset/"+str(token), email)
            flash("Instruction has been sent to your email..", category='s')
        
        else:
            flash("Email not found.", category='e')

    return render_template("forgot.html")

@auth.route('/reset/<token>', methods = ["GET", "POST"])
def reset(token):

    con = sqlite3.connect('system.db')  
    con.row_factory = sqlite3.Row  
    cur = con.cursor()
    
    cur.execute("SELECT * FROM User where token=?", [(token)])
    user = cur.fetchone()
    token1 = str(uuid.uuid4())

    if request.method == 'POST':
        password = request.form["password"]
        password1 = request.form["password1"]

        if password != password1:
            flash("Password does not match.", category="e")
            return redirect(token)
        
        elif len(password) < 8:
            flash("Password must be 8 characters.", category="e")
        
        elif not any(char.isupper() for char in password):
            flash('Password should have at least one uppercase letter.', category="e")

        elif not any(char.isdigit() for char in password):
            flash('Password should have at least one numeral.', category="e")

        elif  user:
            cur.execute("UPDATE User SET password=?, password1=?, token=? where token=?",(password,password1,token1,token))
            con.commit()
            flash("Password Successfully changed.", category='s')
            return redirect(url_for('auth.login'))

        else:
            flash("Token invalid", category='e')


    return render_template('reset.html')

@auth.route('/reset/')
def resset():

    return redirect(url_for('auth.login'))

@auth.route('/user')
def user():
    if "email" in session:

        return render_template("user.html")
    
    else:
        return redirect(url_for("auth.login"))

@auth.route('/handbook')
def handbook():
    if "email" in session:

        return render_template("handbook.html")
    
    else:
        return redirect(url_for("auth.login"))

@auth.route('/assets/')
def assets():
    if "email" in session:

        con = sqlite3.connect('system.db')  
        con.row_factory = sqlite3.Row  
        cur = con.cursor()  
        cur.execute("select * from Stocks")  
        rows = cur.fetchall()
        
        return render_template("assets.html", rows = rows)
    
    else:
        return redirect(url_for("auth.login"))


#---------------------------------------------------
@auth.route("/fetchassets", methods = ["GET", "POST"])
def fetchassets():
    if "email" in session:

        con = sqlite3.connect('system.db')  
        con.row_factory = sqlite3.Row  
        cur = con.cursor()

        if request.method == "POST":
            query = request.form['query']

            if query=='':
                cur.execute("select * from Stocks")
                rows = cur.fetchall()
            
            else:
                search_text=request.form['query']
                cur.execute("select * from Stocks where industry =?", [search_text])
                rows = cur.fetchall()
        
        return jsonify ({'htmlresponse': render_template('response.html', rows=rows)})

    else:
        return redirect(url_for("auth.login"))

#---------------------------------------------------
@auth.route("/fetchvalue", methods = ["GET", "POST"])
def fetchvalue():
    if "email" in session:

        con = sqlite3.connect('system.db')  
        con.row_factory = sqlite3.Row  
        cur = con.cursor()

        if request.method == "POST":
            query = request.form['query']

            if query=='':
                rows = "0"
            
            else:
                search_text=request.form['query']

                cur.execute("SELECT * FROM ChartData where symbol=? and interval = '1d' ORDER BY DATE DESC LIMIT 1", [search_text])
                rows = cur.fetchall()
        
        return jsonify ({'value': render_template('value.html', rows=rows)})

    else:
        return redirect(url_for("auth.login"))

#---------------------------------------------------

@auth.route('/calculator')
def calculator():
    if "email" in session:
        
        return render_template("calculator.html")
    
    else:
        return redirect(url_for("auth.login"))
    

@auth.route('/tutorial', methods = ["GET", "POST"])
def tutorial():
    if "email" in session:

        con = sqlite3.connect('system.db')  
        con.row_factory = sqlite3.Row  
        cur = con.cursor()

        cur.execute("select * from Tutorial")
        rows = cur.fetchall()

        return render_template("tutorials.html", rows=rows)
    
    else:
        return redirect(url_for("auth.login"))

@auth.route('/candlestick', methods = ["GET", "POST"])
def candlestick():
    if "email" in session:

        con = sqlite3.connect('system.db')  
        con.row_factory = sqlite3.Row  
        cur = con.cursor()  
        cur.execute("select * from Candlestick")  
        rows = cur.fetchall()

        return render_template("candlestick.html",rows = rows)
    
    else:
        return redirect(url_for("auth.login"))

@auth.route("/pattern")
def pattern():
    if "email" in session:
        con = sqlite3.connect('system.db')  
        con.row_factory = sqlite3.Row  
        cur = con.cursor()  
        cur.execute("select * from Pattern")  
        rows = cur.fetchall()

        return render_template("pattern.html",rows = rows)
    
    else:
        return redirect(url_for("auth.login"))

@auth.route("/terms", methods = ["GET", "POST"])
def terms():
    if "email" in session:
        con = sqlite3.connect('system.db')  
        con.row_factory = sqlite3.Row  
        cur = con.cursor()  
        cur.execute("select * from Terms")  
        rows = cur.fetchall()


        return render_template("terms.html",rows = rows)
    
    else:
        return redirect(url_for("auth.login"))

@auth.route('/admin_user')
def admin_user():

    if "admin" in session:
        
        con = sqlite3.connect('system.db')  
        con.row_factory = sqlite3.Row  
        cur = con.cursor()  
        cur.execute("select * from User")  
        rows = cur.fetchall()

        return render_template("admin_user.html",rows = rows)
    
    else:
        return redirect(url_for("auth.login"))

@auth.route('/user_post')
def user_post():

    if "admin" in session:
        
        con = sqlite3.connect('system.db')  
        con.row_factory = sqlite3.Row  
        cur = con.cursor()

        cur.execute("select * from Blog order by date desc ")  
        rows = cur.fetchall()

        return render_template("user_post.html",rows = rows)
    
    else:
        return redirect(url_for("auth.login"))

@auth.route('/post_delete/<id>')
def post_delete(id):
    if "admin" in session:
        try:
            con = sqlite3.connect('system.db')
            cur = con.cursor()
            cur.execute("DELETE FROM Blog where id=?",([id]))
            con.commit()
            flash("Record Deleted Successfully",category="s")
        except:
            flash("Record Delete Failed","danger",category="e")
        finally:
            return redirect(url_for("auth.user_post"))
    else:
        return redirect(url_for("auth.login"))

@auth.route("/user_add",methods=["POST","GET"])
def user_add():
    if "admin" in session:

        return render_template("user_add.html")
    
    else:
        return redirect(url_for("auth.login"))

@auth.route("/user_update",methods=["POST","GET"])
def user_update():
    if "admin" in session:
    
        return render_template("user_update.html")
    else:
        return redirect(url_for("auth.login"))


@auth.route('/user_delete/<id>')
def user_delete(id):
    if "admin" in session:
        try:
            con = sqlite3.connect('system.db')
            cur = con.cursor()
            cur.execute("DELETE FROM blockUser where id=?",([id]))
            con.commit()
            con.close()
            flash("Record Deleted Successfully",category="s")
        except:
            flash("Record Delete Failed","danger",category="e")
        finally:
            return redirect(url_for("auth.block_user"))
    else:
        return redirect(url_for("auth.login"))


@auth.route("/useradd",methods=["POST","GET"])
def useradd():
    if "admin" in session:

        with sqlite3.connect('system.db') as con:
                cur = con.cursor()
                
        if request.method == 'POST':
            email = request.form.get('email')
            password =  request.form.get('password')
            password1 = request.form.get('password1')
            statement = f"SELECT * FROM User WHERE email='{email}';"
            cur.execute(statement)
            data = cur.fetchone()
            
            if data:
                flash("Email already exists", category="e")
                
            elif len(email) < 4:
                flash("Please enter valid email.", category="e")
                
            elif len(password)< 8:
                flash("Password must be 8 characters.", category="e")
                
            elif password != password1:
                flash("Password does not match.", category="e")
            
            else:
                
                if not data:
                    cur.execute("INSERT into User (email, password, password1) values (?,?,?)",(email,password,password1))
                    con.commit()
                    
                    flash("Successfully Registered", category="s")

                return redirect(url_for("auth.admin_user"))
    
    else:
        return redirect(url_for("auth.login"))

    
    return render_template("user_add.html")


@auth.route('/userupdate/<id>', methods=["POST","GET"])
def userupdate(id):
    if "admin" in session:
    
        con=sqlite3.connect('system.db')
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute("SELECT * FROM User where id=?",([id]))
        data = cur.fetchone()
        con.commit()

        if request.method=='POST':
            email = request.form['email']
            password=request.form['password']
            password1=request.form['password1']

            if data:
                cur.execute("UPDATE User SET email=? where id=?",(email,id))
                con.commit()

                if len(email) < 4:
                    flash("Please enter valid email.", category="e")
                    return render_template('user_update.html', data=data)

                elif data:
            
                    cur.execute("UPDATE User SET password=?, password1=? where id=?",(password,password1,id))
                    con.commit()

                    if len(password)< 8:
                        flash("Password must be 8 characters.", category="e")
                        return render_template('user_update.html', data=data) 
                
                    if password != password1:
                        flash("Password does not match.", category="e")
                        return render_template('user_update.html', data=data) 
                    
                    else:
                        flash("Update Successfully", category='s')
            
            return redirect(url_for("auth.admin_user"))
    else:
        return redirect(url_for("auth.login"))
        
    return render_template('user_update.html', data=data)


def allowed_file(filename):

    ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    

@auth.route("/admin_candlestick")
def admin_candlestick():
    if "admin" in session:
        con = sqlite3.connect('system.db')  
        con.row_factory = sqlite3.Row  
        cur = con.cursor()  
        cur.execute("SELECT * FROM Candlestick ORDER BY ID DESC;")  
        rows = cur.fetchall()

        return render_template("admin_candlestick.html",rows = rows)
    
    else:
        return redirect(url_for("auth.login"))
    
@auth.route("/add_tutorial", methods = ['POST', "GET"])
def add_tutorial():
    if "admin" in session:

        return render_template("add_tutorial.html")

    else:
        return redirect(url_for("auth.login"))

@auth.route("/admin_tutorial")
def admin_tutorial():
    if "admin" in session:
        con = sqlite3.connect('system.db')  
        con.row_factory = sqlite3.Row  
        cur = con.cursor()  
        cur.execute("SELECT * FROM Tutorial ORDER BY ID DESC;")  
        rows = cur.fetchall()

        return render_template("admin_tutorial.html",rows = rows)
    
    else:
        return redirect(url_for("auth.login"))


@auth.route('/delete_tutorial/<int:id>')
def delete_tutorial(id):
    if "admin" in session:
        try:
            con = sqlite3.connect("system.db")
            cur = con.cursor()
            cur.execute("DELETE FROM Tutorial where id=?",([id]))
            cur.execute("DELETE FROM Step where tutorial_id=?",([id]))
            con.commit()

            flash("Record Deleted Successfully",category="s")
        except:
            flash("Record Delete Failed","danger",category="e")
        finally:
            return redirect(url_for("auth.admin_tutorial"))

    else:
        return redirect(url_for("auth.login"))

@auth.route('/delete_archivedtutorial/<id>')
def delete_archivedtutorial(id):
    if "admin" in session:
        try:
            con = sqlite3.connect("system.db")
            cur = con.cursor()
            cur.execute("DELETE FROM tempTutorial where id=?",([id]))
            con.commit()
            cur.execute("DELETE FROM Step where tutorial_id=?",([id]))
            con.commit()

            flash("Record Deleted Successfully",category="s")
        except:
            flash("Record Delete Failed","danger",category="e")
        finally:
            return redirect(url_for("auth.archived_tutorial"))

    else:
        return redirect(url_for("auth.login"))

@auth.route('/archived_tutorial')
def archived_tutorial():

    if "admin" in session:
        
        con = sqlite3.connect('system.db')  
        con.row_factory = sqlite3.Row  
        cur = con.cursor()  
        cur.execute("SELECT * FROM tempTutorial ORDER BY ID DESC;")  
        rows = cur.fetchall()

        return render_template("archived_tutorial.html",rows = rows)
    
    else:
        return redirect(url_for("auth.login"))


@auth.route("/add_candlestick", methods = ['POST', "GET"])
def add_candlestick():
    if "admin" in session:

        return render_template("add_candlestick.html")

    else:
        return redirect(url_for("auth.login"))


@auth.route('/delete_candlestick/<int:id>')
def delete_candlestick(id):
    if "admin" in session:
        try:
            con = sqlite3.connect("system.db")
            cur = con.cursor()
            cur.execute("DELETE FROM Candlestick where id=?",([id]))
            con.commit()
            flash("Record Deleted Successfully",category="s")
        except:
            flash("Record Delete Failed","danger",category="e")
        finally:
            return redirect(url_for("auth.admin_candlestick"))

    else:
        return redirect(url_for("auth.login"))

@auth.route('/block_user')
def block_user():

    if "admin" in session:
        
        con = sqlite3.connect('system.db')  
        con.row_factory = sqlite3.Row  
        cur = con.cursor()  
        cur.execute("SELECT * FROM blockUser ORDER BY ID DESC;")  
        rows = cur.fetchall()

        return render_template("block_user.html",rows = rows)
    
    else:
        return redirect(url_for("auth.login"))

@auth.route('/archived_candlestick')
def archived_candlestick():

    if "admin" in session:
        
        con = sqlite3.connect('system.db')  
        con.row_factory = sqlite3.Row  
        cur = con.cursor()  
        cur.execute("SELECT * FROM tempCandlestick ORDER BY ID DESC;")  
        rows = cur.fetchall()

        return render_template("archived_candlestick.html",rows = rows)
    
    else:
        return redirect(url_for("auth.login"))

@auth.route('/delete_archivedcandlestick/<name>')
def delete_archivedcandlestick(name):

    if "admin" in session:

        try:
            con = sqlite3.connect("system.db")
            cur = con.cursor()
            cur.execute("DELETE FROM tempCandlestick where name=?",([name]))
            con.commit()
            flash("Record Deleted Successfully",category="s")
        except:
            flash("Record Delete Failed","danger",category="e")
        finally:
            return redirect(url_for("auth.archived_candlestick"))
    
    else:
        return redirect(url_for("auth.login"))

@auth.route("/admin_pattern")
def admin_pattern():
    if "admin" in session:

        con = sqlite3.connect("system.db")  
        con.row_factory = sqlite3.Row  
        cur = con.cursor()  
        cur.execute("SELECT * FROM Pattern ORDER BY ID DESC;")  
        rows = cur.fetchall()

        return render_template("admin_pattern.html",rows = rows)

    else:
        return redirect(url_for("auth.login"))

@auth.route("/add_pattern", methods = ['POST', "GET"])
def add_pattern():
    if "admin" in session:

        return render_template("add_pattern.html")
    
    else:
        return redirect(url_for("auth.login"))

@auth.route('/delete_pattern/<int:id>')
def delete_pattern(id):
    if "admin" in session:
        try:
            con = sqlite3.connect("system.db")
            cur = con.cursor()
            cur.execute("DELETE FROM Pattern where id=?",([id]))
            con.commit()
            flash("Record Deleted Successfully",category="s")
        except:
            flash("Record Delete Failed","danger",category="e")
        finally:
            return redirect(url_for("auth.admin_pattern"))

    else:
        return redirect(url_for("auth.login"))

@auth.route('/archived_pattern')
def archived_pattern():

    if "admin" in session:
        
        con = sqlite3.connect('system.db')  
        con.row_factory = sqlite3.Row  
        cur = con.cursor()  
        cur.execute("SELECT * FROM tempPattern ORDER BY ID DESC;")  
        rows = cur.fetchall()

        return render_template("archived_pattern.html",rows = rows)
    
    else:
        return redirect(url_for("auth.login"))

@auth.route('/delete_archivedpattern/<name>')
def delete_archivedpattern(name):

    if "admin" in session:

        try:
            con = sqlite3.connect("system.db")
            cur = con.cursor()
            cur.execute("DELETE FROM tempPattern where name=?",([name]))
            con.commit()
            flash("Record Deleted Successfully",category="s")
        except:
            flash("Record Delete Failed","danger",category="e")
        finally:
            return redirect(url_for("auth.archived_pattern"))
    
    else:
        return redirect(url_for("auth.login"))


@auth.route("/admin_term")
def admin_term():

    if "admin" in session:
        con = sqlite3.connect("system.db")  
        con.row_factory = sqlite3.Row  
        cur = con.cursor()  
        cur.execute("SELECT * FROM Terms ORDER BY ID DESC;")  
        rows = cur.fetchall()

        return render_template("admin_term.html",rows = rows)
    
    else:
        return redirect(url_for("auth.login"))

@auth.route("/add_term", methods = ['POST', "GET"])
def add_term():

    if "admin" in session:

        return render_template("add_term.html")

    else:
        return redirect(url_for("auth.login"))

@auth.route('/archived_term')
def archived_term():

    if "admin" in session:
        
        con = sqlite3.connect('system.db')  
        con.row_factory = sqlite3.Row  
        cur = con.cursor()  
        cur.execute("SELECT * FROM tempTerms ORDER BY ID DESC;")  
        rows = cur.fetchall()

        return render_template("archived_term.html",rows = rows)
    
    else:
        return redirect(url_for("auth.login"))

@auth.route('/delete_term/<int:id>')
def delete_term(id):

    if "admin" in session:

        try:
            con = sqlite3.connect("system.db")
            cur = con.cursor()
            cur.execute("DELETE FROM Terms where id=?",([id]))
            con.commit()
            flash("Record Deleted Successfully",category="s")
        except:
            flash("Record Delete Failed","danger",category="e")
        finally:
            return redirect(url_for("auth.admin_term"))
    
    else:
        return redirect(url_for("auth.login"))

@auth.route('/delete_archivedterm/<name>')
def delete_archivedterm(name):

    if "admin" in session:

        try:
            con = sqlite3.connect("system.db")
            cur = con.cursor()
            cur.execute("DELETE FROM tempTerms where name=?",([name]))
            con.commit()
            flash("Record Deleted Successfully",category="s")
        except:
            flash("Record Delete Failed","danger",category="e")
        finally:
            return redirect(url_for("auth.archived_term"))
    
    else:
        return redirect(url_for("auth.login"))

@auth.route('/admin_stocks')
def admin_stocks():

    if "admin" in session:
        
        con = sqlite3.connect('system.db')  
        con.row_factory = sqlite3.Row  
        cur = con.cursor()  
        cur.execute("SELECT * FROM Stocks ORDER BY ID DESC;")  
        rows = cur.fetchall()

        return render_template("admin_stocks.html",rows = rows)
    
    else:
        return redirect(url_for("auth.login"))

@auth.route("/add_stocks", methods = ['POST', "GET"])
def add_stocks():

    if "admin" in session:

        return render_template("add_stocks.html")

    else:
        return redirect(url_for("auth.login"))

@auth.route('/delete_stocks/<symbol>')
def delete_stocks(symbol):

    if "admin" in session:

        try:
            con = sqlite3.connect("system.db")
            cur = con.cursor()
            cur.execute("DELETE FROM STOCKS where symbol=?",([symbol]))
            con.commit()
            cur.execute("DELETE FROM chartData where symbol=?",([symbol]))
            con.commit()
            cur.execute("DELETE FROM chartData1 where symbol=?",([symbol]))
            con.commit()
            flash("Record Deleted Successfully",category="s")

            file = 'website/data/'+symbol+'.csv'
            if(os.path.exists(file) and os.path.isfile(file)):
                os.remove(file)
                print("file deleted")
            else:
                print("file not found")
                
        except:
            flash("Record Delete Failed","danger",category="e")
        finally:
            return redirect(url_for("auth.admin_stocks"))
    
    else:
        return redirect(url_for("auth.login"))

@auth.route('/archived_stocks')
def archived_stocks():

    if "admin" in session:
        
        con = sqlite3.connect('system.db')  
        con.row_factory = sqlite3.Row  
        cur = con.cursor()  
        cur.execute("SELECT * FROM tempStocks ORDER BY ID DESC;")  
        rows = cur.fetchall()

        return render_template("archived_stocks.html",rows = rows)
    
    else:
        return redirect(url_for("auth.login"))
    
@auth.route('/delete_archivedstocks/<symbol>')
def delete_archivedstocks(symbol):

    if "admin" in session:

        try:
            con = sqlite3.connect("system.db")
            cur = con.cursor()
            cur.execute("DELETE FROM tempStocks where symbol=?",([symbol]))
            con.commit()
            cur.execute("DELETE FROM chartData where symbol=?",([symbol]))
            con.commit()
            cur.execute("DELETE FROM chartData1 where symbol=?",([symbol]))
            con.commit()

            file = 'website/data/'+symbol+'.csv'
            if(os.path.exists(file) and os.path.isfile(file)):
                os.remove(file)
                print("file deleted")
            else:
                print("file not found")
                
            flash("Record Deleted Successfully",category="s")
        except:
            flash("Record Delete Failed","danger",category="e")
        finally:
            return redirect(url_for("auth.archived_stocks"))
    
    else:
        return redirect(url_for("auth.login"))



@auth.route('/admin_broker')
def admin_broker():

    if "admin" in session:
        
        con = sqlite3.connect('system.db')  
        con.row_factory = sqlite3.Row  
        cur = con.cursor()  
        cur.execute("SELECT * FROM Broker ORDER BY ID DESC;")  
        rows = cur.fetchall()

        return render_template("admin_broker.html",rows = rows)
    
    else:
        return redirect(url_for("auth.login"))


@auth.route("/add_broker", methods = ['POST', "GET"])
def add_broker():

    if "admin" in session:

        return render_template("add_broker.html")

    else:
        return redirect(url_for("auth.login"))

@auth.route('/archived_broker')
def archived_broker():

    if "admin" in session:
        
        con = sqlite3.connect('system.db')  
        con.row_factory = sqlite3.Row  
        cur = con.cursor()  
        cur.execute("SELECT * FROM tempBroker ORDER BY ID DESC;")  
        rows = cur.fetchall()

        return render_template("archived_broker.html",rows = rows)
    
    else:
        return redirect(url_for("auth.login"))

@auth.route('/delete_broker/<int:id>')
def delete_broker(id):

    if "admin" in session:

        try:
            con = sqlite3.connect("system.db")
            cur = con.cursor()
            cur.execute("DELETE FROM Broker where id=?",([id]))
            con.commit()
            flash("Record Deleted Successfully",category="s")

        except:
            flash("Record Delete Failed","danger",category="e")
        finally:
            return redirect(url_for("auth.admin_broker"))
    
    else:
        return redirect(url_for("auth.login"))

@auth.route('/delete_archivedbroker/<int:id>')
def delete_archivedbroker(id):

    if "admin" in session:

        try:
            con = sqlite3.connect("system.db")
            cur = con.cursor()
            cur.execute("DELETE FROM tempBroker where id=?",([id]))
            con.commit()
            flash("Record Deleted Successfully",category="s")
        except:
            flash("Record Delete Failed","danger",category="e")
        finally:
            return redirect(url_for("auth.archived_broker"))
    
    else:
        return redirect(url_for("auth.login"))


@auth.route('/profile', methods = ['GET','POST'])
def profile():

    if "email" in session:

        email = session["email"]
        con = sqlite3.connect("system.db")
        con.row_factory = sqlite3.Row  
        cur = con.cursor()

        cur.execute("SELECT * FROM Blog where author=? order by date desc",([email]))
        blog = cur.fetchall()

        cur.execute("SELECT * FROM User where username=?",([email]))
        user = cur.fetchall()

        cur.execute("SELECT COUNT (*) FROM Blog where author=?",([email]))
        count = cur.fetchone()[0]

        return render_template('profile.html', blog=blog, user=user, count=count)

    else:
        return redirect(url_for("auth.login"))

@auth.route('/changepass', methods = ['GET','POST'])
def changepass():

    if "email" in session:

        email = session["email"]
        con = sqlite3.connect("system.db")
        con.row_factory = sqlite3.Row  
        cur = con.cursor()

        cur.execute("SELECT * FROM User where username=?",([email]))
        user = cur.fetchall()

        if request.method=='POST':
            eaddress=request.form['email']
            password=request.form['password']
            password1=request.form['password1']
            
            if user:
                cur.execute("UPDATE User SET password=?, password1=? where username=?",(password,password1,email))
               
            if len(password)< 8:
                flash("Password must be 8 characters.", category="e")

                
            elif password != password1:
                flash("Password does not match.", category="e")

            else:
                con.commit()
                email_alert("Did you changed your password?", "Hi "+email+". We noticed the password for your account was recently changed.", eaddress)
                flash("Password Successfully changed.", category='s')
                return redirect(url_for("auth.profile"))

        return redirect(url_for("auth.profile", user=user))

    else:
        return redirect(url_for("auth.login"))

@auth.route('/community', methods = ['GET','POST'])
def community():

    if "email" in session:

        con = sqlite3.connect("system.db")
        con.row_factory = sqlite3.Row  
        cur = con.cursor()
        cur.execute("SELECT * FROM Blog ORDER BY id desc")
        blog = cur.fetchall()

        cur.execute("SELECT * from Stocks")
        symbol=cur.fetchall()

        return render_template('community.html', blog=blog, symbol=symbol)

    else:
        return redirect(url_for("auth.login"))

@auth.route("/fetchforum", methods = ["GET", "POST"])
def fetchforum():
    if "email" in session:

        con = sqlite3.connect('system.db')  
        con.row_factory = sqlite3.Row  
        cur = con.cursor()

        if request.method == "POST":
            query = request.form['query']

            if query=='':
                cur.execute("SELECT * FROM Blog ORDER BY DATE DESC")
                blog = cur.fetchall()
            
            else:
                search_text=request.form['query']
                cur.execute("SELECT * FROM Blog WHERE category =? ORDER BY DATE DESC", [search_text])
                blog = cur.fetchall()
        
        return jsonify ({'htmlresponse': render_template('forum.html', blog=blog)})

    else:
        return redirect(url_for("auth.login"))


@auth.route('/blog/<id>', methods=["POST","GET"])
def blog(id):

    if "email" in session:
        
        con=sqlite3.connect("system.db")
        con.row_factory = sqlite3.Row
        cur = con.cursor()

        cur.execute("Select * from Blog where id=?", [id])
        blog=cur.fetchall()

        cur.execute("Select * from Comment where blog_id=? order by id desc",[id])
        comment=cur.fetchall()

        return render_template('post.html', blog=blog, comment=comment)
    
    else:
        return redirect(url_for("auth.login"))

@auth.route('/comment/<id>', methods=["POST","GET"])
def comment(id):

    if "email" in session:
        
        email = session["email"]
        con=sqlite3.connect("system.db")
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        
        cur.execute("Select * from Blog where id=?", [id])
        blog=cur.fetchone()
        author = blog['author']
        blog_id = blog['id']
        eaddress = blog['email']
        
        cur.execute("Select * from User where email=?", [author])
        user=cur.fetchone()

        if request.method == "POST":

            comment = request.form.get('comment')
            time = datetime.now().strftime("%B %d, %Y %I:%M%p")

            cur.execute("INSERT into Comment (comment, comment_author, author, blog_id, date, author_email) values (?,?,?,?,?,?)",(comment, email, author, blog_id, time, eaddress))
            con.commit()
            flash("Your comment has been posted.", category='s')
            email_alert("Notification", "Hi "+author+". "+email+" has been comment to your post. Click the link to redirect. fomostockpriceprediction.herokuapp.com/blog/"+str(id), eaddress)
            return redirect(url_for("auth.blog", id = blog_id))

        return render_template('post.html', blog=blog, user=user, blog_id=blog_id)
    
    else:
        return redirect(url_for("auth.login", ))

@auth.route('/delete_blog/<id>')
def delete_blog(id):

    if "email" in session:

        try:
            con = sqlite3.connect("system.db")
            cur = con.cursor()
            cur.execute("DELETE FROM Blog where id=?",([id]))
            cur.execute("DELETE FROM Comment where blog_id=?",([id]))
            con.commit()
            
            flash("Record Deleted Successfully",category="s")

        except:
            flash("Record Delete Failed","danger",category="e")
        finally:
            return redirect(url_for("auth.profile"))
    
    else:
        return redirect(url_for("auth.login"))


def get_price(symbol):
    page = requests.get("https://finance.yahoo.com/quote/" + symbol)
    soup = BeautifulSoup(page.text, "html.parser")

    price = soup.find('fin-streamer', {'class':'Fw(b) Fz(36px) Mb(-4px) D(ib)'}).text

    # remove thousands separator
    price = price.replace(",", "")
    
    return price


@auth.route('/portfolio')
def portfolio():

    if "email" in session:

        email = session["email"]
        con=sqlite3.connect("system.db")
        con.row_factory = sqlite3.Row
        cur = con.cursor()

        cur.execute("SELECT * from Stocks")
        symbol=cur.fetchall()

        cur.execute("SELECT * FROM Portfolio where email=?",([email]))
        portfolio=cur.fetchall()

        return render_template('portfolio.html', symbol= symbol, portfolio = portfolio)

    else:
        return redirect(url_for("auth.login"))

@auth.route('/myportfolio')
def myportfolio():

    if "email" in session:

        email = session["email"]
        con=sqlite3.connect("system.db")
        con.row_factory = sqlite3.Row
        cur = con.cursor()

        assets = []

        cur.execute("SELECT * FROM Portfolio where email=?",([email]))
        portfolio=cur.fetchall()
        

        for result in portfolio:
            id = result['id']
            symbol = result['symbol']
            quantity = result['quantity']
            initial_value = result['initial_value']
            

            portfolioContent = {
                'id' : id,
                'symbol' : symbol,
                'quantity' : f'{quantity:,}',
                'initial_value' : float(initial_value),
                'totalcost' : round(float(quantity*initial_value),2),
                'currentprice' : get_price(symbol),
                'currentvalue' : round(float(get_price(symbol))*int(quantity),2),
                'net' : round((float(get_price(symbol))-initial_value)/(initial_value)*100, 2),
                'profit' : round(round(float(get_price(symbol)) - initial_value,2)*int(quantity),2)
            }

            assets.append(portfolioContent);
        
        return jsonify(assets)

    else:
        return redirect(url_for("auth.login"))

@auth.route('/addportfolio', methods=["POST","GET"])
def addportfolio():

    if "email" in session:

        email = session["email"]
        con=sqlite3.connect("system.db")
        con.row_factory = sqlite3.Row
        cur = con.cursor()

        if request.method == "POST":

            symbol = request.form.get('symbol')
            quantity = int(request.form.get('quantity'))
            initial_value = float(request.form.get('initial_value'))
            #initial_invest = quantity*initial_value
            #current_price = get_price(symbol)

            #current_value = round(float(current_price)*int(quantity))
            #gain = float(current_price) - float(initial_value)
            #net = round((float(gain)/float(initial_value))*100)

            #cur.execute("INSERT into Portfolio (email, symbol, quantity, initial_value, initial_invest, cprice, current_value, net) values (?,?,?,?,?,?,?,?)",(email, symbol, quantity, initial_value, initial_invest, current_price, current_value,net))
            #con.commit()

            if request.form.get('symbol') == '':

                flash("Something went wrong!", category="e")
            
            else:

                cur.execute("INSERT into Portfolio (email, symbol, quantity, initial_value) values (?,?,?,?)",(email, symbol, quantity, initial_value))
                con.commit()

                flash("Successfully Added", category="s")
            
            return redirect(url_for("auth.portfolio"))

        return render_template('portfolio.html')

    else:
        return redirect(url_for("auth.login"))

#@auth.route('/deleteportfolio')
#def deleteportfolio():
    if "email" in session:

        email = session["email"]
        con=sqlite3.connect("system.db")
        con.row_factory = sqlite3.Row
        cur = con.cursor()

        cur.execute("DELETE FROM Portfolio where email=?", [email])
        con.commit()

        flash("Successfully Deleted", category='s')

        return redirect(url_for("auth.portfolio"))

    else:
        return redirect(url_for("auth.login"))

@auth.route('/deleteportfolio/<id>')
def deleteportfolio(id):

    if "email" in session:

        try:
            con = sqlite3.connect("system.db")
            cur = con.cursor()
            cur.execute("DELETE FROM Portfolio where id=?",([id]))
            con.commit()
            flash("Record Deleted Successfully",category="s")

        except:
            flash("Record Delete Failed","danger",category="e")
        finally:
            return redirect(url_for("auth.portfolio"))
    
    else:
        return redirect(url_for("auth.login"))

@auth.route('/editportfolio/<id>', methods=["POST","GET"])
def editportfolio(id):

    if "email" in session:

        con=sqlite3.connect("system.db")
        con.row_factory = sqlite3.Row
        cur = con.cursor()

        cur.execute("SELECT * FROM Portfolio where id=?",([id]))
        data = cur.fetchone()

        if request.method == 'POST':
            quantity = request.form['quantity']
            initial_value = request.form['initial_value']


            if data:
                cur.execute("UPDATE Portfolio SET quantity=? where id=?",(quantity,id))
                con.commit()

                flash("Successfully Updated", category="s")

            if data:
                cur.execute("UPDATE Portfolio SET initial_value=? where id=?",(initial_value,id))
                con.commit()
        

            return redirect(url_for("auth.portfolio"))
    
 
        return render_template('update_portfolio.html', data=data)

    else:
        
        return redirect(url_for("auth.login"))


@auth.route('/fetchcandlestick', methods=['GET', 'POST'])
def fetchcandlestick():

    if "email" in session:

        con = sqlite3.connect('system.db')  
        con.row_factory = sqlite3.Row  
        cur = con.cursor()
        
        if request.method == "POST":
            query = request.form['query']
            
            if query=='':
                
                cur.execute("select * from Candlestick")
                candlestick = cur.fetchall()
                
            else:
                search_text=request.form['query']
                cur.execute("select * from Candlestick where name =?", [search_text])
                candlestick = cur.fetchall()
                
        
        return jsonify({'htmlresponse': render_template('candlestick_search.html', candlestick=candlestick)})
    
    else:
        return redirect(url_for("auth.login"))

@auth.route('/fetchpattern', methods = ['GET', 'POST'])
def fetchpattern():

    if "email" in session:

        con = sqlite3.connect('system.db')  
        con.row_factory = sqlite3.Row  
        cur = con.cursor()

        if request.method == "POST":
            query = request.form['query']
            
            if query=='':
                
                cur.execute("select * from Pattern")
                pattern = cur.fetchall()
                
            else:
                search_text=request.form['query']
                cur.execute("select * from Pattern where name =?", [search_text])
                pattern = cur.fetchall()
                
        
        return jsonify({'htmlresponse': render_template('pattern_search.html', pattern=pattern)})
        
    else:
        return redirect(url_for("auth.login"))

@auth.route('/fetchterms', methods = ['GET', 'POST'])
def fetchterms():

    if "email" in session:

        con = sqlite3.connect('system.db')  
        con.row_factory = sqlite3.Row  
        cur = con.cursor()

        if request.method == "POST":
            query = request.form['query']
            
            if query=='':
                
                cur.execute("select * from Terms")
                terms = cur.fetchall()
                
            else:
                search_text=request.form['query']
                cur.execute("select * from Terms where name =?", [search_text])
                terms = cur.fetchall()
                
        
        return jsonify({'htmlresponse': render_template('terms_search.html', terms=terms)})
        
    else:
        return redirect(url_for("auth.login"))

@auth.route('/fetchtutorials', methods = ['GET', 'POST'])
def fetchtutorials():
    if "email" in session:
        
        con = sqlite3.connect('system.db')  
        con.row_factory = sqlite3.Row  
        cur = con.cursor()

        if request.method == "POST":
            query = request.form['query']

            tut = []
            ids = []
            
            if query=='':

                cur.execute("select id from Tutorial")
                data = cur.fetchall()

                for result in data:
                    ids.append(result['id'])


                for id in ids:
                    
                    cur.execute("select name, image from Tutorial where id = ?", ([id]))
                    data = cur.fetchall()
                    for result in data:
                        name = result['name']
                        img = result['image']

                    cur.execute("select * from Step where tutorial_id = ?",([id]))
                    stepResult = cur.fetchall()
                    
                    steps = []

                    for step in stepResult:
                        content = {
                            'stepNumber': step['step_number'],
                            'StepDetail': step['step_detail'],
                        }
                        steps.append(content)

                    tutContent = {
                        'name': name,
                        'img': img,
                        'stepNumber': steps
                    }

                    tut.append(tutContent);

                jsonTut = json.dumps(tut)
            
            else:
                search_text=request.form['query']

                cur.execute("select id from Tutorial where id=?", ([search_text]))
                data = cur.fetchall()


                for result in data:
                    ids.append(result['id'])


                for id in ids:
                    
                    cur.execute("select name, image from Tutorial where id = ?", ([id]))
                    data = cur.fetchall()
                    for result in data:
                        name = result['name']
                        img = result['image']

                    cur.execute("select * from Step where tutorial_id = ?",([id]))
                    stepResult = cur.fetchall()
                    
                    steps = []

                    for step in stepResult:
                        content = {
                            'stepNumber': step['step_number'],
                            'StepDetail': step['step_detail'],
                        }
                        steps.append(content)

                    tutContent = {
                        'name': name,
                        'img': img,
                        'stepNumber': steps
                    }

                    tut.append(tutContent);

                jsonTut = json.dumps(tut)
            
            

        return jsonify({'htmlresponse': render_template('tutorials_search.html', tutCompilation = jsonTut)})

    else:
        return redirect(url_for("auth.login"))


@auth.route('/dashboard')
def dashboard():
    if "admin" in session:

        con = sqlite3.connect('system.db')  
        con.row_factory = sqlite3.Row  
        cur = con.cursor()

        cur.execute("SELECT COUNT (*) FROM User")
        user = cur.fetchone()[0]

        cur.execute("SELECT COUNT (*) FROM Stocks")
        stocks = cur.fetchone()[0]

        cur.execute("SELECT COUNT (*) FROM Broker")
        broker = cur.fetchone()[0]

        cur.execute("SELECT COUNT (*) FROM Blog")
        blog = cur.fetchone()[0]

        cur.execute("SELECT * FROM Blog ORDER BY date desc LIMIT 7")
        rblog = cur.fetchall()

        cur.execute("SELECT * FROM Stocks ORDER BY id desc LIMIT 6")
        rstocks = cur.fetchall()
        
        return render_template("dashboard.html", user=user, stocks=stocks, broker=broker, blog=blog, rblog=rblog, rstocks=rstocks)
        
    else:
        return redirect(url_for("auth.login"))

@auth.route('/datavisual/<symbol>24hr')
def datavisual24hr(symbol):

    if "email" in session:

        con = sqlite3.connect('system.db')  
        con.row_factory = sqlite3.Row  
        cur = con.cursor()

        cur.execute("select * from Stocks WHERE symbol =?",([symbol]))
        profile = cur.fetchall()

        return render_template("datavisual24hr.html", profile=profile)
    
    else:
        return redirect(url_for("auth.login"))


@auth.route('/datavisual/<symbol>1mo')
def datavisual1mo(symbol):

    if "email" in session:

        con = sqlite3.connect('system.db')  
        con.row_factory = sqlite3.Row  
        cur = con.cursor()

        cur.execute("select * from Stocks WHERE symbol =?",([symbol]))
        profile = cur.fetchall()

        return render_template("datavisual1mo.html", profile=profile)
    
    else:
        return redirect(url_for("auth.login"))

@auth.route('/datavisual/<symbol>3mo')
def datavisual3mo(symbol):

    if "email" in session:

        con = sqlite3.connect('system.db')  
        con.row_factory = sqlite3.Row  
        cur = con.cursor()

        cur.execute("select * from Stocks WHERE symbol =?",([symbol]))
        profile = cur.fetchall()

        return render_template("datavisual3mo.html", profile=profile)
    
    else:
        return redirect(url_for("auth.login"))

@auth.route('/datavisual/<symbol>6mo')
def datavisual6mo(symbol):

    if "email" in session:

        con = sqlite3.connect('system.db')  
        con.row_factory = sqlite3.Row  
        cur = con.cursor()

        cur.execute("select * from Stocks WHERE symbol =?",([symbol]))
        profile = cur.fetchall()

        return render_template("datavisual6mo.html", profile=profile)
    
    else:
        return redirect(url_for("auth.login"))

@auth.route('/datavisual/<symbol>1yr')
def datavisual1yr(symbol):

    if "email" in session:

        con = sqlite3.connect('system.db')  
        con.row_factory = sqlite3.Row  
        cur = con.cursor()

        cur.execute("select * from Stocks WHERE symbol =?",([symbol]))
        profile = cur.fetchall()

        return render_template("datavisual1yr.html", profile=profile)
    
    else:
        return redirect(url_for("auth.login"))

@auth.route('/logout')
def logout():
    session.pop("email", None)
    session.pop("admin", None)
    
    return redirect(url_for("auth.login"))