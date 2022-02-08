from re import T
from click import Abort
from flask import Flask,session,jsonify,request
from flask_cors import CORS
import os, json
from flask_mysqldb import MySQL
import uuid

app = Flask(__name__)
app.config['SECRET_KEY'] = "as213as2d4a6sd32"

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_DB'] = 'myapp-db'

CORS(app)
mysql = MySQL(app)


def sql_qry(qry):
    cur = mysql.connection.cursor()
    cur.execute(qry)
    data = []
    if not "select" in qry:
        mysql.connection.commit()
    else:
        data = cur.fetchall()
    cur.close()
    
    return data
    
    
@app.route("/api/posts", methods = ['GET', 'POST'])
def test():
    if request.method == "POST":
        try:
            return {"data": sql_qry("select * from posts")}
        except:
            return Abort(500)


@app.route("/api/upload-file", methods=['GET', 'POST'])
def upload_file():
    data = []
    file = request.files['file']
    
    if not file:
        return {"status": "error"}

    if file:
        path = os.path.join("data", file.filename)
        file.save(path)
        
        f = open(path)
        data = json.load(f)
        f.close()    
        res = []
        for obj in data:
            try:
                sql_qry(f"insert into posts (id,userid,title,body) values ('{obj['id']}', '{obj['userId']}', '{obj['title']}', '{obj['body']}')")
                res.append(list(obj.values()))
            except Exception as e:
                print(e)
                
        return {"data": sql_qry("select * from posts")}




@app.route("/auth/login" , methods = ["GET", "POST"])
def sign_in():
    if request.method == "POST":
        data = request.form
        res = sql_qry(f"select * from users where email='{data['email']}' and password='{data['password']}';")
        if len(res) >= 1:
            session['user'] = data['email']
            
            return {"status" : "Logged in Successfully", "userid" : res[0][0]}
        else:
            return Abort(401)
        
        
@app.route("/auth/register", methods=["GET", "POST"])
def sign_up():
    if request.method == "POST":
        name = request.form['name']
        email = request.form['email']
        paasw = request.form['password']

        user = sql_qry(f"select * from users where email='{email}';")
        
        if len(user) > 0:
            return {"status" : "error"}
        
        userid = str(uuid.uuid1())
        sql_qry(f"""
                INSERT into users (userid, username, email,password) values(
                    '{userid}','{name}','{email}', '{paasw}'
                )
        """)
        session['user'] = email
        session['userid'] = userid

        return {"staus" : "done"}



if __name__ == "__main__":
    app.run()