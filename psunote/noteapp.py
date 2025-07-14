import flask
from flask import redirect, url_for, render_template
from sqlalchemy.sql import func
import models
import forms

app = flask.Flask(__name__)
app.config["SECRET_KEY"] = "This is secret key"
app.config["SQLALCHEMY_DATABASE_URI"] = (
    "postgresql://coe:CoEpasswd@localhost:5432/coedb"
)

models.init_app(app)


@app.route("/")
def index():
    db = models.db
    notes = db.session.execute(
        db.select(models.Note).order_by(models.Note.title)
    ).scalars()
    return flask.render_template(
        "index.html",
        notes=notes,
    )


@app.route("/notes/create", methods=["GET", "POST"])
def notes_create():
    form = forms.NoteForm()
    if not form.validate_on_submit():
        print("error", form.errors)
        return flask.render_template(
            "notes-create.html",
            form=form,
        )
    note = models.Note()
    form.populate_obj(note)
    note.tags = []

    db = models.db
    for tag_name in form.tags.data:
        tag = (
            db.session.execute(db.select(models.Tag).where(models.Tag.name == tag_name))
            .scalars()
            .first()
        )

        if not tag:
            tag = models.Tag(name=tag_name)
            db.session.add(tag)

        note.tags.append(tag)

    db.session.add(note)
    db.session.commit()

    return flask.redirect(flask.url_for("index"))


@app.route("/notes/update/<int:id>", methods=["GET", "POST"])
def notes_update(id):
    db = models.db
    note = (
        db.session.execute(db.select(models.Note).where(models.Note.id == id))
        .scalars()
        .first()
    )

    if not note:
        flask.flash("Note not found.", "error")
        return flask.redirect(flask.url_for("index"))

    # Pre-populate form with note data, converting tags to list of tag names
    form = forms.NoteForm(obj=note)
    form.tags.data = [tag.name for tag in note.tags]  # Set tags as strings for form
    if form.validate_on_submit():
        # Update note fields manually, excluding tags
        note.title = form.title.data
        note.description = form.description.data
        note.tags = []  # Clear existing tags

        # Process tags manually
        for tag_name in form.tags.data:
            tag = (
                db.session.execute(
                    db.select(models.Tag).where(models.Tag.name == tag_name)
                )
                .scalars()
                .first()
            )

            if not tag:
                tag = models.Tag(name=tag_name)
                db.session.add(tag)

            note.tags.append(tag)

        note.updated_date = func.now()
        db.session.commit()
        flask.flash("Note updated successfully.", "success")
        return flask.redirect(flask.url_for("index"))

    return flask.render_template(
        "notes-update.html",
        form=form,
        note=note,
    )


@app.route("/notes/delete/<int:id>")
def notes_delete(id):
    db = models.db
    note = (
        db.session.execute(db.select(models.Note).where(models.Note.id == id))
        .scalars()
        .first()
    )

    if not note:
        flask.flash("Note not found.", "error")
        return flask.redirect(flask.url_for("index"))

    db.session.delete(note)
    db.session.commit()
    flask.flash("Note deleted successfully.", "success")
    return flask.redirect(flask.url_for("index"))


@app.route("/tags/<tag_name>")
def tags_view(tag_name):
    db = models.db
    tag = (
        db.session.execute(db.select(models.Tag).where(models.Tag.name == tag_name))
        .scalars()
        .first()
    )
    if not tag:
        flask.flash("Tag not found.", "error")
        return flask.redirect(flask.url_for("index"))

    notes = db.session.execute(
        db.select(models.Note).where(models.Note.tags.any(id=tag.id))
    ).scalars()

    return flask.render_template(
        "tags-view.html",
        tag_name=tag_name,
        notes=notes,
    )


if __name__ == "__main__":
    app.run(debug=True)
