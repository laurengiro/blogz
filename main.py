from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:buildablog@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250))
    body = db.Column(db.String(5000))

    def __init__(self, title, body):
        self.title = title
        self.body = body


@app.route('/blog', methods=['POST', 'GET'])
def index():

    blog_id = request.args.get('id')
    if blog_id:
        blog = Blog.query.filter_by(id=int(blog_id)).all()
        return render_template('single_blog.html', title='Blog', blog=blog)
    else:
        blogs = Blog.query.all()
        return render_template('blog.html', title='Build a Blog', blogs=blogs)


def test_empty(field):
    if len(field) == 0:
        return True
    else:
        return False

@app.route('/newpost', methods=['GET', 'POST'])
def new_post():

    if request.method == 'POST':
        blog_title = request.form['blog_title']
        blog_body = request.form['body']

        title_error = ''
        body_error = ''

        if test_empty(blog_title):
            title_error = 'Please fill in the title'

        if test_empty(blog_body):
            body_error = 'Please fill in the body'

        if not title_error and not body_error:
            new_blog = Blog(blog_title, blog_body)
            db.session.add(new_blog)
            db.session.commit()
            blog_id = new_blog.id
            return redirect('/blog?id={0}'.format(blog_id))
        else:
            return render_template('new_post.html', blog_title=blog_title, body=blog_body, title_error=title_error, body_error=body_error)
    else:
        return render_template('new_post.html', title='New Post')


if __name__ == '__main__':
    app.run()