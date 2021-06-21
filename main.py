from flask import Flask, render_template, redirect, url_for, flash, request, session, json
import requests, json
from flask_sqlalchemy import SQLAlchemy
import sqlalchemy
from wtforms.validators import InputRequired, Email, Length
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SelectField
import base64
import os
import os.path
import boto3
import uuid
import json
import datetime


UPLOAD_FOLDER = 'C:/Users/AVIK/PycharmProjects/Blogging_Website/static/data_stored/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'JPG', 'PNG', 'JPEG'}

app = Flask(__name__)
app.config['SECRET_KEY'] = 'bloggingwebsitesecretkey'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:' '@localhost/blogging_project'





db = SQLAlchemy(app)

class Admin_panel(FlaskForm):
    username = StringField('uname', validators=[InputRequired()])
    password = PasswordField('pswd', validators=[InputRequired()])

class Blog_data(db.Model):
    sl_no  = db.Column(db.Integer, primary_key = True)
    id_no = db.Column(db.String(50), nullable=False)
    title = db.Column(db.String(10), nullable=True)
    user = db.Column(db.String(10), nullable=True)
    created_on = db.Column(db.String(10), nullable=True)
    status = db.Column(db.Integer)
    date = db.Column(db.String(10), nullable=False)

class Admin_data(db.Model):
    user_id = db.Column(db.Integer, primary_key = True)
    user_name = db.Column(db.String(10), nullable=True)
    password = db.Column(db.String(10), nullable=True)
    date_time = db.Column(db.String(10), nullable=True)
    




@app.route("/")
def home():
    return render_template('Home_page.html')





@app.route("/blog")
def blog():
    blog  = Blog_data.query.filter_by(status=1)
    return render_template('blog_page.html', blog=blog)


@app.route("/blog_details/<id_no>")
def blog_details(id_no):
    tt = Blog_data.query.filter_by(id_no=id_no)
    for i in tt:
        title = i.title


    
    s3 = boto3.client(
        's3',
        aws_access_key_id="AKIATP5QTEPV7YAVXCWN",
        aws_secret_access_key="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"                
    )

    data = s3.get_object(
        Bucket = 'us-east-2.german-bakery.blog', 
        Key = str(id_no)+'.content'
    )['Body'].read()


    currdata = json.loads(data.decode('utf-8'))
    


    
    # actual_data = str(json.dumps(parsed_data, indent=4, sort_keys=True))
    # title = currdata["title"]
    content = currdata["content"].replace("textarea", "p")

 

    return render_template('blog_details.html',  content=content, title=title)




@app.route("/contact_us", methods=['GET', 'POST'])
def contact_us():
              
    return render_template('Contact_Us.html')

@app.route("/about_us")
def about_us():
    return render_template('About_Us.html')

@app.route('/admin_panel', methods=['GET', 'POST'])
def admin_panel():
    if request.method == 'POST':
        username = request.form.get('uname')
        password = request.form.get('pswd')

        if username == 'admin' and password == 'admin' or username == 'avik' and password == 'avik':
            session['username'] = username
            return redirect(url_for('admin_blog'))
        
        else:
            return"<h1>Wrong USername and Password</h1>"



    return render_template('admin_panel.html')


@app.route('/admin_blog', methods=['POST', 'GET'])
def admin_blog():
    if 'username' in session:
        if request.method == 'POST':
            title = request.form.get('title')
            print(title)
        return render_template('admin_blog.html')
    
    else:
        return"<h1>Unauthorised Users</h1>"

@app.route('/create_new_blog', methods=['POST', 'GET'])
def create_new_blog():
    if 'username' in session:
        if request.method == 'POST':
            blog_id = uuid.uuid4()            
            user = session["username"]
            requestBody = request.get_json(force=True)
            title = requestBody["title"]
            blog = Blog_data(id_no=blog_id, user=user, title=title)
            db.session.add(blog)
            
            s3 = boto3.client(
                's3',
                aws_access_key_id="AKIATP5QTEPV7YAVXCWN",
                aws_secret_access_key="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"                
            )

            

            s3.put_object(
                ACL = 'public-read',
                Body = '', 
                Bucket = 'us-east-2.german-bakery.blog', 
                Key = str(blog_id)+'.content'
            )
            
            db.session.commit()

            return json.dumps({
                "success": 1,
                "id": str(blog_id)
            })
    else:
        return "<h1>Unauthorised Users</h1>"


@app.route('/my_blogs', methods=['POST', 'GET'])
def my_blogs():
    if 'username' in session:
        user = session["username"]
        blog  = Blog_data.query.filter_by(user=user)
        return render_template('admin_my_blogs.html', blog=blog)
    
    else:
        return"<h1>Unauthorised Users</h1>"



@app.route('/write_blogs', methods=['POST', 'GET'])
def write_blogs():
    if 'username' in session:
        sl_no = 'avik'
        if request.method == 'POST':
            # title = Blog_data.query.filter_by(id_no=id_no) 
            data = request.form['data']
            '''content = request.form.get('data')
            author = request.form.get('author')'''

            # if 'file' not in request.files:
            #     print('No file part')
            #     return redirect(request.url)

            # files = request.files.getlist('files[]')
            

            # for file in data :
            #     if file.data == '':
            #         return redirect(request.url)


            #     if file and allowed_file(file.filename):
            #         file.filename = sl_no
            #         file.save(os.path.join(app.config['UPLOAD_FOLDER'], str(sl_no)))
            #         return ('Uploaded Successfully')

            #     else:
            #         print("File Allowed", allowed_file(file.filename))
            #         return ('Upload Failed')



            blog = Blog_data(title=title, data=content, author=author)
            print(blog)
            # db.session.add(blog)
            # db.session.commit()



        return render_template('write_blog.html')
    
    else:
        return"<h1>Unauthorised Users</h1>"





@app.route('/write_blogs_save', methods=['POST','GET'])
def write_blogs_save():
    if 'username' in session:
        if request.method == 'POST':
            requestBody = request.get_json(force=True)
            content = requestBody["content"]
            blogId = requestBody["id"]   
            x = datetime.datetime.now()
            
            date = x.strftime("%B") + " " + x.strftime("%d") +","+ " " + x.strftime("%Y")
            print(x.strftime("%B") + " " + x.strftime("%d") +","+ " " + x.strftime("%Y"))  

       

            data = Blog_data.query.filter_by(id_no = blogId).first()       
            data.date = date     

            # dt = Blog_data(date=date)
            db.session.add(data)
            

            #bucket: us-east-2.german-bakery.blog
            #key: data/<id>.content
            #Access Key Id: AKIATP5QTEPV7YAVXCWN
            #Secret: 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

            
            s3 = boto3.client(
                's3',
                aws_access_key_id="AKIATP5QTEPV7YAVXCWN",
                aws_secret_access_key="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"                
            )

            

            s3.put_object(
                ACL = 'public-read',
                Body = json.dumps(requestBody), 
                Bucket = 'us-east-2.german-bakery.blog', 
                Key = blogId+'.content'             
            )

            
            

            # dt = Blog_data(date=date)
            # db.session.add(dt)
           
            
            db.session.commit()


            # f = open("myfile.txt", "r")
            # print(f.read())
            # f.close()
            #data = request.json
            # value =data.json()
            #print(data)
        return "<h1> submitted successfully"

        

       

    else:
        return "unauthorised users"

@app.route('/write_blogs_publish', methods=['POST','GET'])
def write_blogs_publish():
    if 'username' in session:
        if request.method == 'POST':
            requestBody = request.get_json(force=True)
            blogId = requestBody["id"]         

            data = Blog_data.query.filter_by(id_no = blogId).first()            
            data.status = 1
            db.session.add(data)
            db.session.commit()
        return "<h1> Published Successfully </h1>"

        

       

    else:
        return "unauthorised users"


@app.route('/write_blogs_unpublish', methods=['POST','GET'])
def write_blogs_unpublish():
    if 'username' in session:
        if request.method == 'POST':
            requestBody = request.get_json(force=True)
            blogId = requestBody["id"]          

            data = Blog_data.query.filter_by(id_no = blogId).first()            
            data.status = 2
            db.session.add(data)
            db.session.commit()
        return "<h1> Blog has been Unpublished successfully. </h1>"

        

       

    else:
        return "unauthorised users"



@app.route('/edit_blogs/<int:sl_no>', methods=['POST', 'GET'])
def edit_blogs(sl_no):
    if 'username' in session:
        if request.method == 'POST':
            title = request.form.get('title')
            print(title)
            data = request.form.get('content')
            print(datatitle)
            author = request.form.get('author')
            print(author)

            blog = Blog_data.query.filter_by(sl_no=sl_no)

            blog.title = title
            blog.data = data
            blog.author = author

            



        return redirect(url_for('my_blogs'))
    
    else:
        return"<h1>Unauthorised Users</h1>"


#this is for upload images 
@app.route('/image_upload/<int:sl_no>', methods=['GET', 'POST'])
def image_upload(sl_no):
    if 'username' in session:

        
        # check if the post request has the file part
        if 'file' not in request.files:
            print('No file part')
            return redirect(request.url)


        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename

        if file.filename == '':
            print('No selected file')
            return redirect(request.url)
        print("Filename bfore validation: ", file.filename)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.filename = sl_no
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], str(sl_no)))
            print(filename)
            return ('Uploaded Successfully')
        else:
            print("File Allowed", allowed_file(file.filename))
            return ('Upload Failed')
            
    

    else:
        return "<h1> You are not allowed to enter.</h1>"

    return render_template('upload.html')


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    if 'username' in session:
        session.pop('username', None)
        return redirect(url_for('admin_panel'))



if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)