from flask import Flask, render_template, flash, request, redirect, url_for
from datetime import datetime, date
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from web_forms import PostForm, UserForm, NamerForm, PasswordForm, LoginForm, SearchForm
from flask_ckeditor import CKEditor, CKEditorField

# Create Flask Instance 
app = Flask(__name__)
# Add Database
# Old SQLite DB
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
# New MySQL DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:roXor230297-@localhost/my_users'

# Secret Key
app.config['SECRET_KEY'] = "eat-my-fat_ass-bitchs"
# Initialize The Datebase
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# CKEditor
cheditor = CKEditor(app) 


# Flask_login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


# Create Blog Post Model
class Posts(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(300))
	content = db.Column(db.Text)
	# author = db.Column(db.String(300))
	date_posted = db.Column(db.DateTime, default=datetime.utcnow)
	slug = db.Column(db.String(300))
	# Foregin Key to Link Users
	poster_id = db.Column(db.Integer, db.ForeignKey("users.id"))


# Create Model
class Users(db.Model, UserMixin):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(20), nullable=False, unique=True)
	username = db.Column(db.String(100), nullable=False)
	email = db.Column(db.String(100), nullable=False, unique=True)
	about_author = db.Column(db.Text(500), nullable=True)
	date_added = db.Column(db.DateTime, default=datetime.utcnow)
	# profile_pic = db.Column(db.String(), nullable=True)
	# password shit 
	password_hash = db.Column(db.String(128))
	# User Owning Posts
	posts = db.relationship("Posts", backref="poster")



	@property
	def password(self):
		raise AttributeError('password is not readable!!!')
	
	@password.setter
	def password(self, password):
		self.password_hash = generate_password_hash(password)

	def verify_password(self, password):
		return check_password_hash(self.password_hash, password)
	

	# Create A String
	def __repr__(self):
		return '<Name %r>' % self.name


# Create Custome Error Pages

# Invalid URL
@app.errorhandler(404)
def page_not_found(e):
	return render_template("404.html"), 404

# Internal Server Error
@app.errorhandler(500)
def page_not_found(e):
	return render_template("404.html"), 500


@app.route('/')
def index():
	first_name = "David"
	stuff = "This is <strong>Bold</strong> Text"
	return render_template("index.html",
		first_name=first_name, stuff=stuff)


# Admin Page
@app.route('/admin')
@login_required
def admin():
	id = current_user.id
	if id == 15:
		return render_template("admin.html")
	else:
		flash("Access Denied")
		return redirect(url_for('dashboard'))


@app.route('/user/<name>')
def user(name):
	return render_template("user.html", user_name=name)
	

# Create Name Page
@app.route('/name', methods=['GET','POST'])
def name():
	name = None
	form = NamerForm()
	# Validat Form
	if form.validate_on_submit():
		name = form.name.data
		form.name.data = ''
		flash("Form Submitted Successfully")
		
	return render_template("name.html", name=name, form=form)


# Create Password TEST Page
@app.route('/test_pw', methods=['GET','POST'])
def test_pw():
	email = None
	password = None
	pw_to_check = None
	passed = None
	form = PasswordForm()


	# Validat Form
	if form.validate_on_submit():
		email = form.email.data
		password = form.password_hash.data
		# Clear form
		form.email.data = ''
		form.password_hash.data = ''

		# Check User by Email
		pw_to_check = Users.query.filter_by(email=email).first()

		# Check Hashed Password
		passed = check_password_hash(pw_to_check.password_hash, password)
		
	return render_template("test_pw.html",
		email=email, 
		password=password,
		pw_to_check=pw_to_check,
		passed=passed,
		form=form)



# Pass Shit To Navbar
@app.context_processor
def base():
	form = SearchForm()
	return dict(form=form)


# Creating User
@app.route('/user/add', methods=['GET','POST'])
def add_user():
	name = None
	form = UserForm()
	if form.validate_on_submit():
		# Hashing PW 
		hashed_pw = generate_password_hash(form.password_hash.data, "sha256")
		user = Users.query.filter_by(email=form.email.data).first()
		if user is None:
			user = Users(name=form.name.data, username=form.username.data, email=form.email.data,
			password_hash=hashed_pw)
			db.session.add(user)
			db.session.commit()
		name = form.name.data
		form.name.data = ''
		form.username.data = ''
		form.email.data = ''
		form.password_hash.data = ''
		flash("User Add Successfully")
	our_users = Users.query.order_by(Users.date_added)
	return render_template("add_user.html", form=form,
		name=name, our_users=our_users)


# Updating User Data 
@app.route('/update/<int:id>', methods=["GET",'POST'])
def update_user(id):
	form = UserForm()
	name_to_update = Users.query.get_or_404(id)
	if request.method == "POST":
		name_to_update.name = request.form['name']
		name_to_update.email = request.form['email']
		name_to_update.username = request.form['username']
		name_to_update.about_author = request.form['about_author']
		name_to_update.profile_pic = request.files['profile_pic']
		try:
			db.session.commit()
			flash("Profile Updated!")
			return render_template("dashboard.html", 
				form=form,
				name_to_update=name_to_update)
		except:
			flash("Error! Try Again")
			return render_template("update.html", 
				form=form,
				name_to_update=name_to_update)
	else:
		return render_template("update.html", 
			form=form,
			name_to_update=name_to_update,
			id=id)


# Deleting User
@app.route('/delete/<int:id>')
def delete(id):
	user_to_delete = Users.query.get_or_404(id)
	name = None
	form = UserForm()
	try:
		db.session.delete(user_to_delete)
		db.session.commit()
		flash("User Deleted!")
		our_users = Users.query.order_by(Users.date_added)
		return render_template("add_user.html", form=form,
			name=name, our_users=our_users)

	except:
		flash("Couldn't Delete User...")
		return render_template("add_user.html", form=form,
			name=name, our_users=our_users)


# View Post Page
@app.route('/posts/<int:id>')
def post(id):
	 post = Posts.query.get_or_404(id)
	 return render_template("post.html", post=post)


# Add Post Page
@app.route('/add-post', methods=['GET', 'POST'])
@login_required
def add_post():
	form = PostForm()

	if form.validate_on_submit():
		poster = current_user.id
		post = Posts(title=form.title.data, content=form.content.data,
			poster_id=poster, slug=form.slug.data)
		# Clear Form
		form.title.data = ''
		form.content.data = ''
		# form.author.data = ''
		form.slug.data = ''

		# Add Post to DB
		db.session.add(post)
		db.session.commit()

		flash("Post Submitted Successfully")

	return render_template("add_post.html", form=form)


# Posts Page
@app.route('/posts')
def posts():
	posts = Posts.query.order_by(Posts.date_posted)
	return render_template("posts.html", posts=posts)


# Edit Post Page
@app.route('/posts/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_post(id):
	post = Posts.query.get_or_404(id)
	form = PostForm()

	if form.validate_on_submit():
		post.title = form.title.data
		# post.author = form.author.data
		post.slug = form.slug.data
		post.content = form.content.data
		# Update DB
		db.session.add(post)
		db.session.commit()
		flash("Post Updated!")
		return redirect(url_for('post', id=post.id))

	if current_user.id == post.poster_id:
		form.title.data = post.title
		# form.author.data = post.author
		form.slug.data = post.slug
		form.content.data = post.content
		return render_template("edit_post.html", form=form)

	else:
		flash("Insufficient Permissions")
		# Get Posts From DB
		posts = Posts.query.order_by(Posts.date_posted)
		return render_template("posts.html", posts=posts)


# Deleting Post Page
@app.route('/post/delete/<int:id>')
@login_required
def delete_post(id):
	post_to_delete = Posts.query.get_or_404(id)
	id = current_user.id
	
	if id == post_to_delete.poster.id:
		try:
			db.session.delete(post_to_delete)
			db.session.commit()
			# Message
			flash("Deleted Successfully")
			# Get Posts From DB
			posts = Posts.query.order_by(Posts.date_posted)
			return render_template("posts.html", posts=posts)

		except:
			flash("Couldn't Delete Post")
			# Get Posts From DB
			posts = Posts.query.order_by(Posts.date_posted)
			return render_template("posts.html", posts=posts)

	else:
		flash("Insufficient Permissions")
		# Get Posts From DB
		posts = Posts.query.order_by(Posts.date_posted)
		return render_template("posts.html", posts=posts)


@login_manager.user_loader
def load_user(user_id):
	return Users.query.get(int(user_id))


# Login Page
@app.route('/login', methods=['GET','POST'])
def login():
	form = LoginForm()

	if form.validate_on_submit():
		user = Users.query.filter_by(username=form.username.data).first()
		if user:
			# Check Hash
			if check_password_hash(user.password_hash, form.password.data):
				login_user(user)
				flash("Logged In")
				return redirect(url_for("dashboard"))
			else:
				flash("Wrong Password... Try Agian!")
		else:
			flash("User Doesn't Exist... Try Again!")

	return render_template("login.html", form=form)


# Logout Page
@app.route('/logout', methods=['GET','POST'])
@login_required
def logout():
	logout_user()
	flash("Logged Out Successfully!")
	return redirect(url_for("login"))


# Dashboard Page
@app.route('/dashboard', methods=['GET','POST'])
@login_required
def dashboard():
	return render_template("dashboard.html")


# Sreach Function
@app.route('/search', methods=['POST'])
def search():
	form = SearchForm()
	posts = Posts.query
	if form.validate_on_submit():
		# Data From Submitted Form
		post.searched = form.searched.data
		# Query DB
		posts = posts.filter(Posts.content.like('%' + post.searched + '%'))
		posts = posts.order_by(Posts.title).all()

		return render_template("search.html", form=form,
		searched=post.searched, posts=posts)

