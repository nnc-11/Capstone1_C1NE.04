from flask import Flask, render_template, request, redirect, url_for, session # type: ignore
from werkzeug.security import generate_password_hash, check_password_hash # type: ignore
from app.paths import PathManager
from modules.fake_news_detector import FakeNewsDetector
from modules.LS_ import HistoricalVerifier
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
    try:
        conn = get_db_connection()
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL
            )
        ''')
        conn.commit()
    except Exception as e:
        print(f"Error initializing database: {str(e)}")
    finally:
        conn.close()


def is_valid_url(url):
    url_pattern = re.compile(r'^(https?://)?([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,6}(/[^\s]*)?$')
    return re.match(url_pattern, url)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/home', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        # Nhận dữ liệu từ form
        url = request.form['url']
        author = request.form['author']
        date = request.form['date']
        title = request.form['title']
        text = request.form['text']
        models_selected = request.form.getlist('models')
        print(models_selected)
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
                detector = FakeNewsDetector(
                    svm_path=path_manager.get_svm_model_path(),
                    tfidf_path=path_manager.get_tfidf_vectorizer_path(),
                    bert_path=path_manager.get_bert_model_path()
                )
                Lsdetector= HistoricalVerifier(
                    model_path=path_manager.get_ModelSimCSE_VN(),
                    embedding_dir=path_manager.get_PBERT()
                )

                if 'model1' in models_selected:
                    #svm
                    svm_pred, svm_proba = detector.predictSVM(text) 
                    if svm_pred == 1:
                        res_svm = f"SVM Prediction: FAKE, Probability: {svm_proba[1]*100:.2f}%"
                    else:
                        res_svm = f"SVM Prediction: REAL, Probability: {svm_proba[0]*100:.2f}%"
                    result_text = f"{res_svm}<br>"
                if 'model2' in models_selected:
                    #bert
                    bert_pred, bert_proba = detector.predictBERT(text)
                    if bert_pred == 1:
                        res_bert = f"BERT Prediction: FAKE, Probability: {bert_proba[1]*100:.2f}%"
                    else:
                        res_bert = f"BERT Prediction: REAL, Probability: {bert_proba[0]*100:.2f}%"
                    result_text += f"{res_bert}<br>"
                if 'model3' in models_selected:
                    res=Lsdetector.interactive_verify(text)
                    result_text += f"{res}<br>"
                    #LS PhoBert
                    pass
            except Exception as e:
                result_text = f"Error during Fake News detection: {str(e)}"

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
# Đăng ký người dùng
@app.route('/register', methods=['POST'])
def register():
    name = request.form.get('name')
    email = request.form.get('email')
    password = request.form.get('password')

    conn = get_db_connection()
    # Kiểm tra xem email đã tồn tại chưa
    user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()

    if user:
        conn.close()
        return "Email already registered!", 400

    # Mã hóa mật khẩu trước khi lưu
    hashed_password = generate_password_hash(password)

    # Lưu người dùng vào cơ sở dữ liệu
    conn.execute('INSERT INTO users (name, email, password) VALUES (?, ?, ?)', 
                 (name, email, hashed_password))
    conn.commit()
    conn.close()

    return redirect(url_for('index'))

@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')

    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
    conn.close()

    if not user or not check_password_hash(user['password'], password):
        return "Invalid email or password", 400

    # Lưu thông tin người dùng vào session để sử dụng cho các route khác
    session['user_id'] = user['id']
    session['user_name'] = user['name']

    # Sau khi đăng nhập thành công, chuyển hướng đến trang home
    return redirect(url_for('home'))

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('user_name', None)
    return redirect(url_for('index'))

@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('home'))

    # Lấy thông tin người dùng từ cơ sở dữ liệu bằng ID người dùng trong session
    conn = get_db_connection()
    user = conn.execute('SELECT name, email FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    conn.close()

    if user:
        # Nếu không có ảnh người dùng, dùng ảnh mặc định
        user_profile_image = 'profi.png'  # Đường dẫn đến ảnh mặc định trong thư mục static
        return render_template('profile.html', user=user, user_profile_image=user_profile_image)
    else:
        return "User not found", 404


if __name__ == '__main__':
    init_db()
    app.run(debug=True)
