from website import create_app
from flask import request, redirect, flash, url_for, render_template, session
import json, os, sqlite3
from datetime import datetime
from pytz import timezone


app = create_app()
app.config['UPLOAD_FOLDER'] = "website/static"
app.config['COMMUNITY_FOLDER'] = "website/static/community"

@app.route('/blockuser/<id>', methods=["POST","GET"])
def blockuser(id):
    
    if "admin" in session:

        con=sqlite3.connect("system.db")
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute("INSERT INTO blockUser SELECT [id], [username], [email], [password], [password1], [token] FROM User WHERE id=?",([id]))
        con.commit()
        cur.execute("DELETE from User WHERE id=?",([id]))
        con.commit()
        flash("Successfully Blocked User", category="s")

        return redirect(url_for("auth.admin_user"))
    
    else:
        return redirect(url_for("auth.login"))

@app.route('/unblock/<id>', methods=["POST","GET"])
def unblock(id):
    
    if "admin" in session:

        con=sqlite3.connect("system.db")
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute("INSERT INTO User SELECT [id], [username], [email], [password], [password1], [token] FROM blockUser WHERE id=?",([id]))
        con.commit()
        cur.execute("DELETE from blockUser WHERE id=?",([id]))
        con.commit()
        flash("Successfully User Unblock!", category="s")

        return redirect(url_for("auth.block_user"))
    
    else:
        return redirect(url_for("auth.login"))

@app.route('/uploadtutorial', methods=["POST","GET"])
def uploadtutorial():
    if "admin" in session:

        with sqlite3.connect("system.db") as con:
            cur = con.cursor()

        if request.method == "POST":

            tutorialId = 0;
            name = request.form.get('name')
            link = request.form.get('link')
            image = request.files['image']
            numberOfStep = request.form.get('numberOfStep')

            if image.filename !=' ':
                filepath=os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
                image.save(filepath)
                cur.execute("INSERT into Tutorial (name, image, link) values (?,?,?)",(name, image.filename, link))
                con.commit()
                tutorialId = cur.lastrowid
                
            for i in range(int(numberOfStep)):
                currentNumberOfStep = i;
                cur.execute("INSERT into Step ('TUTORIAL_ID', 'STEP_NUMBER', 'STEP_DETAIL') values (?,?,?)",
                (tutorialId, str(currentNumberOfStep+1), request.form.get('step'+str(currentNumberOfStep+1))))
                con.commit()

            flash("Successfully Added", category="s")

            return redirect(url_for("auth.admin_tutorial"))
            
        return render_template("add_tutorial.html")
    
    else:
        return redirect(url_for("auth.login"))


@app.route('/tutorialupdate/<id>', methods=["POST","GET"])
def tutorialupdate(id):
    if "admin" in session:

        tut = []
        steps = []

        con = sqlite3.connect('system.db')  
        con.row_factory = sqlite3.Row  
        cur = con.cursor()  
        
        cur.execute("select * from Tutorial where id =  ?", ([id]))
        result = cur.fetchall()

        for rs in result:
            tut = {
                'id': rs['id'],
                'name': rs['name'],
                'link': rs['link'],
                'image': rs['image']
            }

        cur.execute("select * from Step where TUTORIAL_ID =  ?", ([id]))
        result = cur.fetchall()

        for rs in result:
            step = {
                'stepNumeber': rs['STEP_NUMBER'],
                'stepDetail': rs['STEP_DETAIL']
            }
            steps.append(step);

        
        if request.method == 'POST':
            name = request.form['name']
            numberOfStep = request.form.get('numberOfStep')
            link = request.form['link']
            image = request.files['image']

            
            if result:
                    cur.execute("UPDATE Tutorial SET name=? where id=?",(name,id))
                    con.commit()

            
            if result:
                    cur.execute("UPDATE Tutorial SET link=? where id=?",(link,id))
                    con.commit()

                    flash("Successfully Updated", category="s")
            
            if image:
                filepath=os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
                image.save(filepath)

                cur.execute("UPDATE Tutorial SET image=? where id=?",(image.filename,id))
                con.commit()
            
            cur.execute("DELETE from Step where TUTORIAL_ID = ?",([id]))
            con.commit()

            for i in range(int(numberOfStep)):
                currentNumberOfStep = i;
                cur.execute("INSERT into Step ('TUTORIAL_ID', 'STEP_NUMBER', 'STEP_DETAIL') values (?,?,?)",
                (id, str(currentNumberOfStep+1), request.form.get('step'+str(currentNumberOfStep+1))))
                con.commit()
            
            return redirect(url_for("auth.admin_tutorial"))

        stepsTut = json.dumps(steps)

        return render_template('update_tutorial.html', tut=tut, stepsTut=stepsTut)

    else:

        return redirect(url_for("auth.login"))

@app.route('/tutorialarchived/<id>', methods=["POST","GET"])
def tutorialarchived(id):
    
    if "admin" in session:

        con=sqlite3.connect("system.db")
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute("INSERT INTO tempTutorial SELECT [id], [name], [image], [link] FROM Tutorial WHERE id=?",([id]))
        con.commit()
        cur.execute("DELETE from Tutorial WHERE id=?",([id]))
        con.commit()
        flash("Successfully Data Archived", category="s")

        return redirect(url_for("auth.admin_tutorial"))
    
    else:
        return redirect(url_for("auth.login"))

@app.route('/tutorialrestore/<id>', methods=["POST","GET"])
def tutorialrestore(id):
    
    if "admin" in session:

        con=sqlite3.connect("system.db")
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute("INSERT INTO Tutorial SELECT [id], [name], [image], [link] FROM tempTutorial WHERE id=?",([id]))
        con.commit()
        cur.execute("DELETE from tempTutorial WHERE id=?",([id]))
        con.commit()
        flash("Successfully Data Restored", category="s")

        return redirect(url_for("auth.archived_tutorial"))
    
    else:
        return redirect(url_for("auth.login"))

@app.route('/uploadcandlestick', methods=["POST","GET"])
def uploadcandlestick():

    with sqlite3.connect("system.db") as con:
        cur = con.cursor()

    if request.method == "POST":
        name = request.form.get('name')
        description =  request.form.get('description')
        image = request.files['image']

        if image.filename !=' ':
            filepath=os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
            image.save(filepath)
            cur.execute("INSERT into Candlestick (name, description, image) values (?,?,?)",(name, description, image.filename,))
            con.commit()

        flash("Successfully Added")

        return redirect(url_for("auth.admin_candlestick"))
        
    return render_template("add_candlestick.html")

@app.route('/candlestickupdate/<id>', methods=["POST","GET"])
def candlestickupdate(id):
    if "admin" in session:
    
        con=sqlite3.connect('system.db')
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute("SELECT * FROM Candlestick where id=?",([id]))
        data = cur.fetchone()

        if request.method == 'POST':
            name = request.form['name']
            description=request.form['description']
            image = request.files['image']


            if data:
                cur.execute("UPDATE Candlestick SET name=? where id=?",(name,id))
                con.commit()

                flash("Successfully Updated", category="s")

            if data:
                cur.execute("UPDATE Candlestick SET description=? where id=?",(description,id))
                con.commit()
            
            if image:
                filepath=os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
                image.save(filepath)

                cur.execute("UPDATE Candlestick SET image=? where id=?",(image.filename,id))
                con.commit()

            return redirect(url_for("auth.admin_candlestick"))
    
        return render_template('update_candlestick.html', data=data)
    
    else:
        return redirect(url_for("auth.login"))

@app.route('/candlestickarchived/<name>', methods=["POST","GET"])
def candlestickarchived(name):
    
    if "admin" in session:

        con=sqlite3.connect("system.db")
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute("INSERT INTO tempCandlestick SELECT [id], [name], [description], [image] FROM Candlestick WHERE name=?",([name]))
        con.commit()
        cur.execute("DELETE from Candlestick WHERE name=?",([name]))
        con.commit()
        flash("Successfully Data Archived", category="s")

        return redirect(url_for("auth.admin_candlestick"))
    
    else:
        return redirect(url_for("auth.login"))

@app.route('/candlestickrestore/<name>', methods=["POST","GET"])
def candlestickrestore(name):
    
    if "admin" in session:

        con=sqlite3.connect("system.db")
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute("INSERT INTO Candlestick SELECT [id], [name], [description], [image] FROM tempCandlestick WHERE name=?",([name]))
        con.commit()
        cur.execute("DELETE from tempCandlestick WHERE name=?",([name]))
        con.commit()
        flash("Successfully Data Restored", category="s")

        return redirect(url_for("auth.archived_candlestick"))
    
    else:
        return redirect(url_for("auth.login"))

@app.route('/uploadpattern', methods=["POST","GET"])
def uploadpattern():

    with sqlite3.connect("system.db") as con:
        cur = con.cursor()

    if request.method == "POST":
        name = request.form.get('name')
        description =  request.form.get('description')
        image = request.files['image']
        link = request.form.get('link')

        if image.filename !=' ':
            filepath=os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
            image.save(filepath)
            cur.execute("INSERT into Pattern (name, description, image, link) values (?,?,?,?)",(name, description, image.filename, link))
            con.commit()

        flash("Successfully Added", category="s")

        return redirect(url_for("auth.admin_pattern"))
        
    return render_template("add_pattern.html")

@app.route('/patternupdate/<id>', methods=["POST","GET"])
def patternupdate(id):

    if "admin" in session:
        con=sqlite3.connect("system.db")
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute("SELECT * FROM Pattern where id=?",([id]))
        data = cur.fetchone()

        if request.method == 'POST':
            name = request.form['name']
            description=request.form['description']
            image = request.files['image']
            link = request.form['link']


            if data:
                cur.execute("UPDATE Pattern SET name=? where id=?",(name,id))
                con.commit()

                flash("Successfully Updated", category="s")

            if data:
                cur.execute("UPDATE Pattern SET description=? where id=?",(description,id))
                con.commit()
            
            if image:
                filepath=os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
                image.save(filepath)

                cur.execute("UPDATE Pattern SET image=? where id=?",(image.filename,id))
                con.commit()
            
            if data:
                cur.execute("UPDATE Pattern SET link=? where id=?",(link,id))
                con.commit()

            return redirect(url_for("auth.admin_pattern"))
    
 
        return render_template('update_pattern.html', data=data)

    else:
            return redirect(url_for("auth.login"))

@app.route('/patternarchived/<name>', methods=["POST","GET"])
def patternarchived(name):
    
    if "admin" in session:

        con=sqlite3.connect("system.db")
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute("INSERT INTO tempPattern SELECT [id], [name], [description], [image], [link] FROM Pattern WHERE name=?",([name]))
        con.commit()
        cur.execute("DELETE from Pattern WHERE name=?",([name]))
        con.commit()
        flash("Successfully Data Archived", category="s")

        return redirect(url_for("auth.admin_pattern"))
    
    else:
        return redirect(url_for("auth.login"))

@app.route('/patternrestore/<name>', methods=["POST","GET"])
def patternrestore(name):
    
    if "admin" in session:

        con=sqlite3.connect("system.db")
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute("INSERT INTO Pattern SELECT [id], [name], [description], [image], [link] FROM tempPattern WHERE name=?",([name]))
        con.commit()
        cur.execute("DELETE from tempPattern WHERE name=?",([name]))
        con.commit()
        flash("Successfully Data Restored", category="s")

        return redirect(url_for("auth.archived_pattern"))
    
    else:
        return redirect(url_for("auth.login"))

@app.route('/uploadterms', methods=["POST","GET"])
def uploadterms():

    with sqlite3.connect("system.db") as con:
        cur = con.cursor()
    
    if request.method == "POST":
        name = request.form.get('name')
        description =  request.form.get('description')
        image = request.files['image']

        if image.filename !=' ':
            filepath=os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
            image.save(filepath)
            cur.execute("INSERT into Terms (name, description, image) values (?,?,?)",(name, description, image.filename,))
            con.commit()

        flash("Successfully Added", category="s")

        return redirect(url_for("auth.admin_term"))
        
    return render_template("add_term.html")

@app.route('/termupdate/<id>', methods=["POST","GET"])
def termupdate(id):
    
    if "admin" in session:

        con=sqlite3.connect("system.db")
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute("SELECT * FROM Terms where id=?",([id]))
        data = cur.fetchone()

        if request.method == 'POST':
            name = request.form['name']
            description=request.form['description']
            image = request.files['image']


            if data:
                cur.execute("UPDATE TERMS SET name=? where id=?",(name,id))
                con.commit()

                flash("Successfully Updated", category="s")

            if data:
                cur.execute("UPDATE TERMS SET description=? where id=?",(description,id))
                con.commit()
            
            if image:
                filepath=os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
                image.save(filepath)

                cur.execute("UPDATE TERMS SET image=? where id=?",(image.filename,id))
                con.commit()

            return redirect(url_for("auth.admin_term"))
    
        return render_template('update_term.html', data=data)

    else:
        return redirect(url_for("auth.login"))

@app.route('/termarchived/<name>', methods=["POST","GET"])
def termarchived(name):
    
    if "admin" in session:

        con=sqlite3.connect("system.db")
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute("INSERT INTO tempTerms SELECT [id], [name], [description], [image] FROM Terms WHERE name=?",([name]))
        con.commit()
        cur.execute("DELETE from Terms WHERE name=?",([name]))
        con.commit()
        flash("Successfully Data Archived", category="s")

        return redirect(url_for("auth.admin_term"))
    
    else:
        return redirect(url_for("auth.login"))

@app.route('/termrestore/<name>', methods=["POST","GET"])
def termrestore(name):
    
    if "admin" in session:

        con=sqlite3.connect("system.db")
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute("INSERT INTO Terms SELECT [id], [name], [description], [image] FROM tempTerms WHERE name=?",([name]))
        con.commit()
        cur.execute("DELETE from tempTerms WHERE name=?",([name]))
        con.commit()
        flash("Successfully Data Restored", category="s")

        return redirect(url_for("auth.archived_term"))
    
    else:
        return redirect(url_for("auth.login"))

@app.route('/uploadstocks', methods=["POST","GET"])
def uploadstocks():

    with sqlite3.connect("system.db") as con:
        cur = con.cursor()

    if request.method == "POST":
        name = request.form.get('name')
        symbol =  request.form.get('symbol')
        logo = request.files['logo']
        exchange =  request.form.get('exchange')
        sector = request.form.get('sector')
        industry = request.form.get('industry')
        profile = request.form.get('profile')

        if logo.filename !=' ':
            filepath=os.path.join(app.config['UPLOAD_FOLDER'], logo.filename)
            logo.save(filepath)
            cur.execute("INSERT into Stocks (name, symbol, logo, exchange, sector, industry, profile) values (?,?,?,?,?,?,?)",(name, symbol, logo.filename, exchange, sector, industry, profile))
            con.commit()

        flash("Successfully Added", category="s")

        return redirect(url_for("auth.admin_stocks"))
        
    return render_template("add_stocks.html")

@app.route('/stocksupdate/<id>', methods=["POST","GET"])
def stocksupdate(id):
    
    if "admin" in session:

        con=sqlite3.connect("system.db")
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute("SELECT * FROM Stocks where id=?",([id]))
        data = cur.fetchone()

        if request.method == 'POST':
            name = request.form['name']
            symbol=request.form['symbol']
            logo = request.files['logo']
            exchange=request.form['exchange']
            sector = request.form['sector']
            industry = request.form['industry']
            profile = request.form['profile']


            if data:
                cur.execute("UPDATE STOCKS SET name=? where id=?",(name,id))
                con.commit()

                flash("Successfully Updated", category="s")

            if data:
                cur.execute("UPDATE STOCKS SET symbol=? where id=?",(symbol,id))
                con.commit()
            
            if logo:
                filepath=os.path.join(app.config['UPLOAD_FOLDER'], logo.filename)
                logo.save(filepath)

                cur.execute("UPDATE STOCKS SET logo=? where id=?",(logo.filename,id))
                con.commit()
            
            if data:
                cur.execute("UPDATE STOCKS SET exchange=? where id=?",(exchange,id))
                con.commit()

            
            if data:
                cur.execute("UPDATE STOCKS SET sector=? where id=?",(sector,id))
                con.commit()

            if data:
                cur.execute("UPDATE STOCKS SET industry=? where id=?",(industry,id))
                con.commit()
            
            if data:
                cur.execute("UPDATE STOCKS SET profile=? where id=?",(profile,id))
                con.commit()

            return redirect(url_for("auth.admin_stocks"))
    
        return render_template('update_stock.html', data=data)

    else:
        return redirect(url_for("auth.login"))

@app.route('/stocksarchived/<symbol>', methods=["POST","GET"])
def stocksarchived(symbol):
    
    if "admin" in session:

        con=sqlite3.connect("system.db")
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute("INSERT INTO tempStocks SELECT [id], [name], [symbol], [logo], [exchange], [sector], [industry], [profile] FROM Stocks WHERE symbol=?",([symbol]))
        con.commit()
        cur.execute("DELETE from Stocks WHERE symbol=?",([symbol]))
        con.commit()
        flash("Successfully Data Archived", category="s")

        return redirect(url_for("auth.admin_stocks"))
    
    else:
        return redirect(url_for("auth.login"))

@app.route('/stocksrestore/<symbol>', methods=["POST","GET"])
def stocksrestore(symbol):
    
    if "admin" in session:

        con=sqlite3.connect("system.db")
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute("INSERT INTO Stocks SELECT [id], [name], [symbol], [logo], [exchange], [sector], [industry], [profile] FROM tempStocks WHERE symbol=?",([symbol]))
        con.commit()
        cur.execute("DELETE from tempStocks WHERE symbol=?",([symbol]))
        con.commit()
        flash("Successfully Data Restored", category="s")

        return redirect(url_for("auth.archived_stocks"))
    
    else:
        return redirect(url_for("auth.login"))

@app.route('/uploadbroker', methods=["POST","GET"])
def uploadbroker():

    with sqlite3.connect("system.db") as con:
        cur = con.cursor()
    
    if request.method == "POST":
        bname = request.form.get('bname')
        blogo = request.files['blogo']
        bpair =  request.form.get('bpair')
        blink =  request.form.get('blink')


        if blogo.filename !=' ':
            filepath=os.path.join(app.config['UPLOAD_FOLDER'], blogo.filename)
            blogo.save(filepath)
            cur.execute("INSERT into Broker (bname, blogo, bpair, blink) values (?,?,?,?)",(bname, blogo.filename, bpair, blink))
            con.commit()

        flash("Successfully Added", category="s")

        return redirect(url_for("auth.admin_broker"))
        
    return render_template("add_broker.html")

@app.route('/brokerupdate/<id>', methods=["POST","GET"])
def brokerupdate(id):
    
    if "admin" in session:

        con=sqlite3.connect("system.db")
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute("SELECT * FROM Broker where id=?",([id]))
        data = cur.fetchone()

        if request.method == 'POST':
            bname = request.form['bname']
            blogo = request.files['blogo']
            bpair = request.form['bpair']
            blink = request.form['blink']


            if data:
                cur.execute("UPDATE BROKER SET bname=? where id=?",(bname,id))
                con.commit()

                flash("Successfully Updated", category="s")

            
            if blogo:
                filepath=os.path.join(app.config['UPLOAD_FOLDER'], blogo.filename)
                blogo.save(filepath)

                cur.execute("UPDATE BROKER SET blogo=? where id=?",(blogo.filename,id))
                con.commit()

            if data:
                cur.execute("UPDATE BROKER SET bpair=? where id=?",(bpair,id))
                con.commit()
            
            if data:
                cur.execute("UPDATE BROKER SET blink=? where id=?",(blink,id))
                con.commit()

            return redirect(url_for("auth.admin_broker"))
    
        return render_template('update_broker.html', data=data)

    else:
        return redirect(url_for("auth.login"))

@app.route('/brokerarchived/<id>', methods=["POST","GET"])
def brokerarchived(id):
    
    if "admin" in session:

        con=sqlite3.connect("system.db")
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute("INSERT INTO tempBroker SELECT [id], [bname], [blogo], [bpair], [blink] FROM Broker WHERE id=?",([id]))
        con.commit()
        cur.execute("DELETE from Broker WHERE id=?",([id]))
        con.commit()
        flash("Successfully Data Archived", category="s")

        return redirect(url_for("auth.admin_broker"))
    
    else:
        return redirect(url_for("auth.login"))

@app.route('/brokerrestore/<id>', methods=["POST","GET"])
def brokerrestore(id):
    
    if "admin" in session:

        con=sqlite3.connect("system.db")
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute("INSERT INTO Broker SELECT [id], [bname], [blogo], [bpair], [blink] FROM tempBroker WHERE id=?",([id]))
        con.commit()
        cur.execute("DELETE from tempBroker WHERE id=?",([id]))
        con.commit()
        flash("Successfully Data Restored", category="s")

        return redirect(url_for("auth.archived_broker"))
    
    else:
        return redirect(url_for("auth.login"))

@app.route('/write', methods=["POST","GET"])
def write():

    if "email" in session:
        
        email = session["email"]
        con=sqlite3.connect("system.db")
        con.row_factory = sqlite3.Row
        cur = con.cursor()

        cur.execute("SELECT * FROM User WHERE username=?", [email])
        user = cur.fetchone()
        eaddress = user['email']

        if request.method == "POST":
            blog = request.form.get('blog')
            image = request.files['image']
            symbol = request.form.get('symbol')
            time_format = "%B %d, %Y %I:%M%p"
            now = datetime.now().strftime(time_format)
            tz = ['Asia/Manila']

            for zone in tz:
                dt = datetime.now(timezone(zone)).strftime(time_format)
            


            if image.filename !=' ':
                filepath=os.path.join(app.config['COMMUNITY_FOLDER'], image.filename)
                image.save(filepath)
                cur.execute("INSERT into Blog (blog, category, image, author, date, email) values (?,?,?,?,?,?)",(blog, symbol, image.filename, email, dt, eaddress))
                con.commit()

                flash("Successfully Posted", category="s")
                return redirect(url_for("auth.community"))

        return render_template('community.html')
    
    else:
        return redirect(url_for("auth.login"))

@app.route('/editpost/<id>', methods=["POST","GET"])
def editpost(id):
    
    if "email" in session:

        con=sqlite3.connect("system.db")
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute("SELECT * FROM Blog where id=?",([id]))
        data = cur.fetchone()

        if request.method == 'POST':
            blog = request.form['blog']
            image = request.files['image']
            time = datetime.now().strftime("%B %d, %Y %I:%M%p")

            if data:
                cur.execute("UPDATE Blog SET blog=? where id=?",(blog,id))
                con.commit()

                flash("Successfully Updated", category="s")

            
            if image:
                filepath=os.path.join(app.config['COMMUNITY_FOLDER'], image.filename)
                image.save(filepath)

                cur.execute("UPDATE Blog SET image=? where id=?",(image.filename,id))
                con.commit()
            
            if data:
                cur.execute("UPDATE Blog SET date=? where id=?",(time,id))
                con.commit()



            return redirect(url_for("auth.profile"))
    
        return render_template('editpost.html', data=data)

    else:
        return redirect(url_for("auth.login"))


if __name__ == '__main__':
    app.run(debug=True, threaded=True, process=1)
    #socketio.run(app, debug=True)
