from flask import Flask, render_template, flash, request, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError
from wtforms.validators import DataRequired, EqualTo, Length
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date 
from wtforms.widgets import TextArea


# Create Flask Instance 
app = Flask(__name__)
# Add Database
# Old SQLite DB
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
# New MySQL DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:roXor230297-@localhost/my_users'

# Secret Key
app.config['SECRET_KEY'] = "eat my fat ass bitchs"
# Initialize The Datebase
db = SQLAlchemy(app)
migrate = Migrate(app, db)


# Create Blog Post Model
class Posts(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(300))
	content = db.Column(db.Text)
	author = db.Column(db.String(300))
	date_posted = db.Column(db.DateTime, default=datetime.utcnow)
	slug = db.Column(db.String(300))


# Create Post Form
class PostForm(FlaskForm):
	title = StringField("Title", validators=[DataRequired()])
	content = StringField("Content", validators=[DataRequired()], widget=TextArea())
	author =StringField("Author", validators=[DataRequired()])
	slug = StringField("Slug", validators=[DataRequired()])
	submit = SubmitField("Submit")


# Create Model
class Users(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(100), nullable=False)
	email = db.Column(db.String(100), nullable=False, unique=True)
	favorite_music = db.Column(db.String(100))
	date_added = db.Column(db.DateTime, default=datetime.utcnow)
	# password shit 
	password_hash = db.Column(db.String(128))

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


# Create a Flask Instance
class UserForm(FlaskForm):
	name = StringField("Name", validators=[DataRequired()])
	email = StringField("Email", validators=[DataRequired()])
	favorite_music = StringField("Favorite Music")
	password_hash = PasswordField("Password", validators=[DataRequired(), EqualTo("password_hash2", message="Passwords Must Match!")])
	password_hash2 = PasswordField("Confirm Password", validators=[DataRequired()])
	submit = SubmitField("Submit")

# Create a Flask Instance
class NamerForm(FlaskForm):
	name = StringField("What's Your Name", validators=[DataRequired()])
	submit = SubmitField("Submit")


class PasswordForm(FlaskForm):
	email = StringField("What's Your Email", validators=[DataRequired()])
	password_hash = PasswordField("What's Your Password", validators=[DataRequired()])
	submit = SubmitField("Submit")

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


# Updating User Data 
@app.route('/update/<int:id>', methods=["GET",'POST'])
def update_user(id):
	form = UserForm()
	name_to_update = Users.query.get_or_404(id)
	if request.method == "POST":
		name_to_update.name = request.form['name']
		name_to_update.email = request.form['email']
		name_to_update.favorite_music = request.form['favorite_music']
		try:
			db.session.commit()
			flash("User Updated!")
			return render_template("update.html", 
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
			user = Users(name=form.name.data, email=form.email.data,
			favorite_music=form.favorite_music.data, password_hash=hashed_pw)
			db.session.add(user)
			db.session.commit()
		name = form.name.data
		form.name.data = ''
		form.email.data = ''
		form.favorite_music.data = ''
		form.password_hash.data = ''
		flash("User Add Successfully")
	our_users = Users.query.order_by(Users.date_added)
	return render_template("add_user.html", form=form,
		name=name, our_users=our_users)


# JSON
@app.route('/date')
def get_current_date():
	favorite_pizza = {
	"David": "Mushrooms",
	"Alina": "Olives"
	}
	# return {"Date": date.today()}
	return favorite_pizza


@app.route('/posts/<int:id>')
def post(id):
	 post = Posts.query.get_or_404(id)
	 return render_template("post.html", post=post)

	# Add Post Page
@app.route('/add-post', methods=['GET', 'POST'])
def add_post():
	form = PostForm()

	if form.validate_on_submit():
		post = Posts(title=form.title.data, content=form.content.data,
			author=form.author.data, slug=form.slug.data)
		# Clear Form
		form.title.data = ''
		form.content.data = ''
		form.author.data = ''
		form.slug.data = ''

		# Add Post to DB
		db.session.add(post)
		db.session.commit()

		flash("Post Submitted Successfully")

	return render_template("add_post.html", form=form)


@app.route('/posts')
def posts():
	posts = Posts.query.order_by(Posts.date_posted)
	return render_template("posts.html", posts=posts)


@app.route('/posts/edit/<int:id>', methods=['GET', 'POST'])
def edit_post(id):
	post = Posts.query.get_or_404(id)
	form = PostForm()
	if form.validate_on_submit():
		post.title = form.title.data
		post.author = form.author.data
		post.slug = form.slug.data
		post.content = form.content.data
		# Update DB
		db.session.add(post)
		db.session.commit()
		flash("Post Updated!")
		return redirect(url_for('post', id=post.id))
	form.title.data = post.title
	form.author.data = post.author
	form.slug.data = post.slug
	form.content.data = post.content
	return render_template("edit_post.html", form=form)


@app.route('/post/delete/<int:id>')
def delete_post(id):
	post_to_delete = Posts.query.get_or_404(id)

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
