from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
from hashutils import make_pw_hash, check_pw_hash


app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogzpw@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'


class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250))
    body = db.Column(db.String(5000))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner


class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    pw_hash = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.pw_hash = make_pw_hash(password)


@app.before_request
def require_login():
    allowed_routes = ['login', 'list_blogs', 'index', 'signup', 'logout']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user:
            if check_pw_hash(password, user.pw_hash):
                session['username'] = username
                flash('Logged in')
                return redirect('/newpost')
            else:
                flash('Invalid passsord', 'error')
                return render_template('login.html', username=username)
        else:
            flash('User does not exist', 'error')
            
    return render_template('login.html')


def test_len(field):
    if len(field)>=3:
        return True
    else:
        return False

def test_space(field):
    if ' ' not in field:
        return True
    else:
        return False
 
def validate_field(field):
    if test_len(field) and test_space(field):
        return True
    else:
        return False


@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify_password = request.form['verify']

        username_error = ''
        password_error = ''
        password_match_error = ''

        existing_user = User.query.filter_by(username=username).first()

        if not existing_user:
            if not validate_field(username):
                username_error = 'That\'s not a valid username'
            if not validate_field(password):
                password_error = 'That\'s not a valid password'
            if not validate_field(verify_password) or password != verify_password:
                password_match_error = 'Passwords don\'t match'
            if not username_error and not password_error and not password_match_error: 
                new_user = User(username, password)
                db.session.add(new_user)
                db.session.commit()
                session['username'] = username
                flash('User created')
                return redirect('/newpost')
            else:
                return render_template('signup.html', username=username, username_error=username_error, password_error=password_error, password_match_error=password_match_error)
        else:
            flash('Username already exists', 'error')
            return render_template('signup.html', username=username)

    return render_template('signup.html')


@app.route('/logout')
def logout():

    try:
        del session['username']
        flash("Logged out")
    finally:
        return redirect('/blog')


@app.route('/')
def index():
    users = User.query.all()
    return render_template('index.html', users=users)


@app.route('/blog', methods=['POST', 'GET'])
def list_blogs():

    blog_id = request.args.get('id')
    user_id = request.args.get('user')
    if blog_id:
        blog = Blog.query.filter_by(id=int(blog_id)).all()
        return render_template('single_blog.html', blog=blog)
    elif user_id:
        blogs = Blog.query.filter_by(owner_id=int(user_id)).all()
        return render_template('blog.html', blogs=blogs)
    else:
        blogs = Blog.query.all()
        return render_template('blog.html', blogs=blogs)


def test_empty(field):
    if len(field) == 0:
        return True
    else:
        return False

@app.route('/newpost', methods=['GET', 'POST'])
def new_post():
     
    if request.method == 'POST':
        owner = User.query.filter_by(username=session['username']).first()
        blog_title = request.form['blog_title']
        blog_body = request.form['body']

        title_error = ''
        body_error = ''

        if test_empty(blog_title):
            title_error = 'Please fill in the title'

        if test_empty(blog_body):
            body_error = 'Please fill in the body'

        if not title_error and not body_error:
            new_blog = Blog(blog_title, blog_body, owner)
            db.session.add(new_blog)
            
            db.session.commit()
            blog_id = new_blog.id
            return redirect('/blog?id={0}'.format(blog_id))
        else:
            return render_template('new_post.html', blog_title=blog_title, body=blog_body, title_error=title_error, body_error=body_error)
    else:
        return render_template('new_post.html')


if __name__ == '__main__':
    app.run()