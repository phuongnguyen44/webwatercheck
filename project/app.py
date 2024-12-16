from flask import Flask,render_template,session,request,redirect,url_for
from flask_mysqldb import MySQL
from predictModel.models import *
from datetime import timedelta
import pandas as pd
import os
from flask_socketio import SocketIO, emit
app =Flask(__name__)
app.secret_key='phuong2003'
# Cấu hình kết nối MySQL trong XAMPP
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'       # Tên người dùng MySQL (mặc định là 'root')
app.config['MYSQL_PASSWORD'] = ''       # Mật khẩu (mặc định là trống)
app.config['MYSQL_DB'] = 'flask_users'     # Tên cơ sở dữ liệu bạn đã tạo trong phpMyAdmin
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)  # Đặt thời gian sống của session là 30 ngày


# Đặt thư mục lưu trữ file tải lên
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Giới hạn kích thước file là 16MB

# Chỉ cho phép các file với các định dạng cụ thể
ALLOWED_EXTENSIONS = {'csv'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Khởi tạo Flask-MySQL
mysql = MySQL(app)
socketio = SocketIO(app)

@app.route('/')
def home():
    if 'username' in session:
        return render_template('index.html', username=session['username'])
    else:
        return render_template('index.html')
@app.route('/blog')
def blog():
    if 'username' in session:
        return render_template('blog.html', username=session['username'])
    else:
        return render_template('blog.html')

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method =='POST':
        username=request.form['username']
        password=request.form['password']
        cur=mysql.connection.cursor()
        cur.execute(f"select username,password from tbl_users where username='{username}'")
        user =cur.fetchone()
        cur.close()
        if user and password==user[1]:
            session['username']=user[0]
            return redirect(url_for('home'))
        else:
            return render_template('login.html',error="Invalid username or password")
    return render_template('login.html')

@app.route('/register',methods=['GET','POST'])
def register():
    if request.method =='POST':
        username=request.form['username']
        password=request.form['password']
        email=request.form['email']
        cur=mysql.connection.cursor()
        cur.execute(f"insert into tbl_users (username,email,password) values ('{username}','{email}','{password}')")
        mysql.connection.commit()
        cur.close()

        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('username',None)
    return redirect(url_for('home'))

@app.route("/predict",methods=['POST'])
def predict():
    if request.method =='POST':
        ph = request.form['ph']
        hardness = request.form['hardness']
        solids = request.form['solids']
        chloramines = request.form['chloramines']
        sulfate = request.form['sulfate']
        conductivity = request.form['conductivity']
        organic_carbon = request.form['organic_carbon']
        trihalomethanes = request.form['trihalomethanes']
        turbidity = request.form['turbidity']
        data=predicted( ph,hardness,solids,chloramines,sulfate ,conductivity ,organic_carbon ,trihalomethanes ,turbidity )
        save_dt=data[0]
        # Path to save the file
        file_path = 'save_file/model_water_safety.txt'
        # Write the data to the file
        with open(file_path, 'w') as file:
            for model, safety in save_dt.items():
                file.write(f'{model}: {safety}\n')
        if 'username' in session:
            return render_template('total.html',datas1=data, username=session['username'])
        else:
            return render_template('total.html',datas1=data)

@app.route("/upload",methods=['POST',"GET"])
def upload():
    if request.method =='POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            if not os.path.exists(app.config['UPLOAD_FOLDER']):
                os.makedirs(app.config['UPLOAD_FOLDER'])
            # Lưu file vào thư mục uploads
            filename = file.filename
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            try:
                tt=[]
                required_columns = [
                    'ph',
                    'Hardness', 
                    'Solids', 
                    'Chloramines', 
                    'Sulfate', 
                    'Conductivity', 
                    'Organic_carbon', 
                    'Trihalomethanes', 
                    'Turbidity'
                ]
                df = pd.read_csv(file_path)
                if all(column in df.columns for column in required_columns):
                    print("File CSV chứa tất cả các cột yêu cầu.")
                    # Lặp qua từng dòng của DataFrame
                    for index, row in df.iterrows():
                        data=predicted( row[0],row[1],row[2],row[3],row[4] ,row[5] ,row[6] ,row[7] ,row[8] )
                        tt.append(data)
                    # Luu file
                    saved_fl=[]
                    for j in tt:
                        for k in range(len(j)):
                            if j[k]==j[0]:
                                saved_fl.append(j[k])
                    print(saved_fl)
                    # Path to save the file
                    file_path = 'save_file/models_water_safety_array.txt'

                    # Write the data to the file
                    with open(file_path, 'w') as file:
                        for index, entry in enumerate(saved_fl):
                            file.write(f"Entry {index + 1}:\n")  # Writing the entry number
                            for model, safety in entry.items():
                                file.write(f'{model}: {safety}\n')
                            file.write("\n")  # Add an empty line between entries

                    return render_template('total.html',datas=tt, username=session['username'])
                else:
                    print("File CSV thiếu một số cột yêu cầu.")
                    return render_template('upload.html',error="Invalid file", username=session['username'])

            except:
                return render_template('upload.html',error="Invalid file", username=session['username'])
    if 'username' in session:
        return render_template('upload.html',username=session['username'])
    else:
        return render_template('upload.html')

@app.route("/guide",methods=['POST',"GET"])
def guide():
    if request.method =='POST':
        if 'username' in session:
            username=session['username']
            title = request.form['title']
            content = request.form['content']

            cur=mysql.connection.cursor()
            cur.execute('SELECT title,content FROM posts WHERE (title,content) = (%s, %s)',(title, content))
            tt=cur.fetchall()
            if (tt):
                return redirect(url_for('home'))
            cur.execute('INSERT INTO posts (title, content,user) VALUES (%s, %s, %s)', (title, content,username))
            mysql.connection.commit()
            post_id = cur.lastrowid
            print(post_id)

            # Phát sự kiện mới để cập nhật cho các client đang kết nối
            socketio.emit('new_post', {'title': title, 'content': content,'user':username,'id':post_id})

            cur.execute("SELECT * FROM posts ORDER BY date DESC")  # Truy vấn tất cả bài viết từ bảng posts
            posts = cur.fetchall()  # Lấy tất cả kết quả
            comments = {}
            for post in posts:
                post_id = post[0]  # Lấy id của bài viết
                cur.execute("SELECT * FROM comments WHERE post_id = %s", (post_id,))
                comments[post_id] = cur.fetchall()
                cur.execute(f"SELECT user FROM posts WHERE id={post_id}")  # Truy vấn tất cả bài viết từ bảng posts
            cur.close()
            return render_template('guide.html',posts=posts, username=session['username'],comments=comments)
        else:
            return redirect(url_for('home'))
    else:
        if 'username' in session:
            cur=mysql.connection.cursor()
            cur.execute("SELECT * FROM posts ")  # Truy vấn tất cả bài viết từ bảng posts
            posts = cur.fetchall()  # Lấy tất cả kết quả
            comments = {}
            for post in posts:
                post_id = post[0]  # Lấy id của bài viết
                cur.execute("SELECT * FROM comments WHERE post_id = %s", (post_id,))
                comments[post_id] = cur.fetchall()
                cur.execute(f"SELECT user FROM posts WHERE id={post_id}")  # Truy vấn tất cả bài viết từ bảng posts
            cur.close()
            return render_template('guide.html',posts=posts, username=session['username'],comments=comments)
        else:
            return redirect(url_for('home'))
@app.route("/comment/<int:post_id>",methods=['POST'])
def comment(post_id):
    if 'username' in session:
        username=session['username']
        content = request.form['content']
        cur=mysql.connection.cursor()
        cur.execute('INSERT INTO comments (post_id, content) VALUES (%s, %s)', (post_id, content))
        mysql.connection.commit()
        cur.close()
        socketio.emit('new_comment', {'content': content,'postId':post_id})
        return redirect(url_for('guide'))
    else:
        return redirect(url_for('index'))


if __name__ =="__main__":
    # app.run(debug=True)
    socketio.run(app, debug=True)

