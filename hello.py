from flask import Flask, render_template, request, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor, CKEditorField
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm

from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL

app = Flask(__name__)
app.config['SECRET_KEY'] = 'INeedSomeCheeseCake'
ckeditor = CKEditor(app)
Bootstrap(app)

# Create Database
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///posts.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), unique=True, nullable=False)
    subtitle = db.Column(db.String(100), unique=True, nullable=False)
    body = db.Column(db.Text(250), unique=True, nullable=False)
    img_url = db.Column(db.String(250), nullable=False)


# db.create_all()


class PostForm(FlaskForm):
    title = StringField('Post Title', validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    body = CKEditorField("Body", validators=[DataRequired()])
    img_url = StringField("Image URL", validators=[DataRequired(), URL()])
    submit = SubmitField('Submit')


@app.route("/")
def get_all_posts():
    all_posts = db.session.query(Post).all()
    return render_template("index.html", posts=all_posts)


@app.route("/post_detail/<int:post_id>")
def post_detail(post_id):
    requested_post = Post.query.get(post_id)
    return render_template("post_detail.html", post=requested_post)


@app.route("/add", methods=["GET", "POST"])
def add():
    form = PostForm()
    if request.method == "POST":
        form = PostForm()
        if form.validate_on_submit():
            new_post = Post(
                title=request.form["title"],
                subtitle=request.form["subtitle"],
                body=request.form["body"],
                img_url=request.form["img_url"]
            )
            db.session.add(new_post)
            db.session.commit()
            return redirect(url_for('get_all_posts'))
    posts = Post.query.all()
    return render_template("add.html", form=form, posts=posts)


@app.route("/edit-post/<int:post_id>", methods=["GET", "POST"])
def edit_post(post_id):
    post = Post.query.get(post_id)
    edit_form = PostForm(
        title=post.title,
        subtitle=post.subtitle,
        img_url=post.img_url,
        body=post.body
    )
    if edit_form.validate_on_submit():
        post.title = edit_form.title.data
        post.subtitle = edit_form.subtitle.data
        post.img_url = edit_form.img_url.data
        post.body = edit_form.body.data
        db.session.commit()
        return redirect(url_for("post_detail", post_id=post.id))
    return render_template("add.html", form=edit_form, is_edit=True)


@app.route("/delete/<int:post_id>")
def delete_post(post_id):
    post_to_delete = Post.query.get(post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('get_all_posts'))


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


if __name__ == "__main__":
    app.run(debug=True)
