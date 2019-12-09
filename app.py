import flask
from forms import LoginForm, RegistrationForm, PostForm
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy


app = flask.Flask(__name__)
app.config["SECRET_KEY"] = "MY_NEW_PROJECT"
app.config["WTF_CSRF_ENABLED"] = False
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"

bcrypt = Bcrypt(app)
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)

    def __repr__(self):
        return f"User({self.username}, {self.email}, {self.password})"


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post = db.Column(db.String(300), nullable=False)

    def __repr__(self):
        return self.post


@app.route("/", methods=["POST", "GET"])
def login():
    made_function = False

    form = LoginForm()

    if form.validate_on_submit():

        password = form.password.data
        username = form.username.data
        rpassword = bcrypt.generate_password_hash(password).decode("utf-8")

        user = User.query.filter_by(username=username).first()

        if user is not None:
            if bcrypt.check_password_hash(user.password, password=password):

                try:
                    if user is not None:
                        @app.route(f"/chat{rpassword}", methods=["POST", "GET"])
                        def chat():
                            write = Post.query.all()
                            form1 = PostForm()
                            if form1.validate_on_submit():
                                post = Post(post=form1.post.data)
                                db.session.add(post)
                                db.session.commit()
                                return flask.redirect(flask.url_for("chat"))
                            return flask.render_template("chat.html", write=write) + flask.render_template("post.html",
                                                                                                           form=form1)

                        @app.route(f"/home{rpassword}")
                        def main_page():
                            return flask.render_template("home.html")

                        made_function = True
                except:
                    made_function = True
                return flask.redirect(flask.url_for("main_page"))

            else:
                return flask.render_template("wrong.html")
        else:
            return flask.render_template("wrong.html")

    return flask.render_template("login.html", form=form)


@app.route("/register", methods=["POST", "GET"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        password = bcrypt.generate_password_hash(form.password.data)
        user = User(username=form.username.data, password=password, email=form.email.data)
        db.session.add(user)
        db.session.commit()
        return flask.redirect(flask.url_for("login"))
    return flask.render_template("register.html", form=form)

