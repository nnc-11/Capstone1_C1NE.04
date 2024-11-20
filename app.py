from flask import Flask, render_template, request, redirect, url_for, session # type: ignore
from werkzeug.security import generate_password_hash, check_password_hash # type: ignore
from app.paths import PathManager
from datetime import datetime, timedelta
from modules.fake_news_detector import FakeNewsDetector
from modules.UrlText_Ver1 import input_UrlText
import re
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Kết nối cơ sở dữ liệu SQLite
def get_db_connection():
    conn = sqlite3.connect('instance\\users.db')
    conn.row_factory = sqlite3.Row
    return conn

# Tạo bảng người dùng nếu chưa có
def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT NOT NULL,
            password TEXT NOT NULL
        );
    ''')
    conn.commit()
    conn.close()

def is_valid_url(url):
    url_pattern = re.compile(r'^(https?://)?([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,6}(/[^\s]*)?$')
    return re.match(url_pattern, url)

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        # Nhận dữ liệu từ form
        url = request.form['url']
        author = request.form['author']
        date = request.form['date']
        title = request.form['title']
        text = request.form['text']

        # Kiểm tra nếu không nhập URL hoặc Title + Text
        error_message_url = None
        error_message_title = None
        error_message_text = None
        
        if not url and not title and not text:
            return render_template('home.html', url=url, author=author, date=date, title=title, text=text,
                           error_message_url=1, error_message_title=1, error_message_text=1)    
        elif not text and title:
            return render_template('home.html', url=url, author=author, date=date, title=title, text=text,
                        error_message_text=1)
        # Tiến hành xử lý phân tích nếu không có lỗi
        result = ''
        percentage = 0
        result_text = ''
        
        # Nếu URL được cung cấp, lấy văn bản từ URL
        if url:
            try:
                aurl = input_UrlText(url).get_Text_in_Url()
                if aurl['id']=='0':  
                    return render_template('home.html', 
                               result="", 
                               percentage='', 
                               result_text=aurl['content'],
                               url='', author='', date='', title='', text='')
                else:
                    text = aurl['content']

            except Exception as e:
                # Xử lý lỗi nếu gặp lỗi ngoài mong muốn
                error_message_url = f"Error extracting text from URL: {str(e)}"
                return render_template('home.html', url=url, author=author, date=date, title=title, text=text,
                                    error_message_url=error_message_url)

        #print(text)
        # Tiến hành phân tích Fake News nếu có Text
        text = title + text
        if text:
            try:
                path_manager = PathManager()
                # Sử dụng các phương thức của PathManager để lấy đường dẫn
                detector = FakeNewsDetector(
                    svm_path=path_manager.get_svm_model_path(),
                    tfidf_path=path_manager.get_tfidf_vectorizer_path(),
                    bert_path=path_manager.get_bert_model_path()
                )
                    
                result, percentage = detector.predict(text)  # Example: result could be 'REAL'/'FAKE', percentage the confidence
                result_text = f"\nPrediction: {'FAKE' if result == 1 else 'REAL'}, Confidence: {percentage:.4f}%"
            except Exception as e:
                result = "ERROR"
                result_text = f"Error during Fake News detection: {str(e)}"
                percentage = 0

            # Return the result in the template
            return render_template('home.html', 
                                result_text=result_text,
                                url='', author='', date='', title='', text='')

    # Nếu GET request, render form trống
    return render_template('home.html', url='', author='', date='', title='', text='')  # Render form trống nếu GET


@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/services')
def services():
    return render_template('services.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    error_message = None
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        phone = request.form['phone']
        password = request.form['password']

        # Kiểm tra dữ liệu đầu vào
        if len(password) < 8 or len(password) > 16:
            error_message = "Password must be between 8 and 16 characters and contain only letters and numbers."
        elif not re.match("^[A-Za-z0-9]*$", password):
            error_message = "Password must only contain letters and numbers, no special characters."
        elif not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            error_message = "Email must be in a valid format (with '@' and '.')."
        elif not re.match(r"^\d{10}$", phone):
            error_message = "Phone number must have exactly 10 digits."

        if error_message:
            return render_template('register.html', error=error_message)

        # Hash mật khẩu trước khi lưu vào DB
        hashed_password = generate_password_hash(password)
        
        # Lưu thông tin người dùng vào cơ sở dữ liệu
        conn = get_db_connection()
        conn.execute('INSERT INTO users (username, email, phone, password) VALUES (?, ?, ?, ?)',
                     (username, email, phone, hashed_password))
        conn.commit()
        conn.close()
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    error_message = None
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
        conn.close()

        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            return redirect(url_for('profile'))
        else:
            error_message = "Login failed, please check your information."
            return render_template('login.html', error=error_message)
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    conn.close()
    return render_template('profile.html', user=user)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
