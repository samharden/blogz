from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://blogmaster:spillyourguts@localhost:3306/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'notmuchofasecret'

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(1000))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    posts = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['display_login', "login", "signup_form", "sign_up", "home", "list_blogs", "view_post"]
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/login')
def display_login():
    return render_template("login.html")

@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            # flash("Logged in")
            return redirect('/blog')
        else:
            error = 'User password incorrect, or user does not exist.'
            return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    del session['username']
    flash("You have been logged out.")
    return redirect('/blog')

@app.route("/")
def home():
    users = User.query.all()
    if 'username' in session:
        _username = session['username']
    else:
        _username = None
    return render_template(
                            "index.html",
                            usernames = users,
                            _username = _username
                            )

@app.route("/add-new")
def show_form():
    if 'username' in session:
        _username = session['username']
        print(_username)
    else:
        _username = False
        print("No logged in user")
    user_id = User.query.filter_by(username=session['username']).first()
    # id_num = request.args.get('user_id')
    print("ID NUMBER = ", user_id)
    return render_template(
                            "add_posts.html",
                            _username = _username)

@app.route('/add-new', methods=["POST", "GET"])
def submit_form():
    title = request.form["title"]
    body = request.form["body"]
    user_id = User.query.filter_by(username=session['username']).first()
    _username = session['username']
    title_error = ""
    body_error = ""

    if len(title) <1:
        title_error = "Needs a title."
        title = ""

    if len(body) <1:
        body_error = "Try actually putting something in the post content this time."
        body = ""

    if not title_error and not body_error:
        if request.method == "POST":
            new_post = Blog(title, body, user_id)
            db.session.add(new_post)
            db.session.commit()
            return redirect("/display?id="+str(new_post.id))
    else:
        return render_template("add_posts.html", title = title,
            body = body,
            title_error = title_error,
            body_error = body_error,
            _username = _username)

@app.route("/blog", methods=["POST", "GET"])
def list_blogs():
    author_name = ""

    if request.args.get('user_id'):
        print("USER ID = ", request.args.get('user_id'))
        if 'username' in session:
            _username = session['username']
            _userid = User.query.filter_by(username=session['username']).first().id
        else:
            _username = None
            _userid = None
        # _username = session['username']
        # _userid = User.query.filter_by(username=session['username']).first().id
        print(_username)
        id_num = request.args.get('user_id')
        print("OWNER ID = ", id_num)
        filtered_blog_posts = Blog.query.filter_by(owner_id = id_num).all()
        author_name = User.query.filter_by(id=id_num).first().username
        posts_by = "Posts by "+author_name
        all_users = User.query.all()
        return render_template(
                                "list_blogs.html",
                                title="Build A Blog",
                                blog_posts=filtered_blog_posts,
                                author_name = author_name,
                                _username = _username,
                                posts_by = posts_by,
                                id_num = id_num,
                                _userid = _userid,
                                all_users = all_users,
                                )

    elif request.method == "GET" and 'username' in session:
        _username = session['username']
        _userid = User.query.filter_by(username=session['username']).first().id
        print(_username)
        id_num = User.query.filter_by(username=session['username']).first().id
        print("OWNER ID = ", id_num)
        filtered_blog_posts = Blog.query.all()
        all_users = User.query.all()
        author_name = User.query.filter_by(id=id_num).first().username

        posts_by = "All Posts"
        return render_template(
                                "list_blogs.html",
                                title="Build A Blog",
                                blog_posts=filtered_blog_posts,
                                author_name = author_name,
                                _username = _username,
                                posts_by = posts_by,
                                _userid = id_num,
                                all_users = all_users,
                                )

    else:
        _username = False
        print("No logged in user")
        all_blog_posts = Blog.query.all()
        all_users = User.query.all()
        return render_template(
                                "list_blogs.html",
                                title="Build A Blog",
                                blog_posts=all_blog_posts,
                                all_users = all_users,
                                _username = _username)

@app.route('/display', methods=['POST', 'GET'])
def view_post():
    post_id = request.args.get('id')
    blog_post_entry = Blog.query.get(post_id)
    title_name = blog_post_entry.title
    body = blog_post_entry.body
    author_id = blog_post_entry.owner_id
    all_users = User.query.all()
    if 'username' in session:
        _username = session['username']
    else:
        _username = None

    return render_template(
                            'display_post.html',
                            title_name = title_name,
                            blog_post_entry = blog_post_entry,
                            body = body,
                            _username = _username,
                            all_users = all_users,
                            )

@app.route("/signup")
def signup_form():
    return render_template("signup.html")

@app.route("/signup", methods=["POST", "GET"])
def sign_up():
    user_error = ""
    pw_error = ""
    vpw_error = ""

    if request.method == 'POST':
        username = str(request.form["username"])
        password = str(request.form["password"])
        validpw = str(request.form["verify_password"])

        if len(username) <3 or len(username) > 20 or " " in username:
            user_error = "Username must be between 3 and 20 characters long and may not contain spaces."
            user = ""

        if len(password) <3 or len(password) > 20 or " " in password:
            pw_error = "Password must be between 3 and 20 characters long and may not contain spaces."

        if password != validpw:
            vpw_error = "Password entries do not match."

        if not user_error and not pw_error and not vpw_error:
            existing_user = User.query.filter_by(username=username).first()
            if not existing_user:
                new_user = User(username, password)
                db.session.add(new_user)
                db.session.commit()
                session['username'] = username
                flash("You are logged in as {{username}}.")
                return redirect('/add-new')
            elif existing_user:
                flash("This Username is already registered. Please register a different username or login to continue.")
                return render_template("signup.html")
            else:
                return render_template("signup.html",
                    user_error = user_error,
                    pw_error = pw_error,
                    vpw_error = vpw_error,
                    em_error = em_error,
                    user = user,
                    password = "",
                    validpw = "",
                    em = em,)


if __name__ == "__main__":
    app.run()
