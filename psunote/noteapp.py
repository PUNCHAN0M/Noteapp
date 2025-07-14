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
        print("Form errors:", form.errors)
        return flask.render_template(
            "notes-create.html",
            form=form,
        )
    note = models.Note()
    form.populate_obj(note)
    note.tags = []

    db = models.db
    for tag_name in form.tags.data:
        tag_name = tag_name.strip()
        if tag_name:  # Only process non-empty tags
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

    form = forms.NoteForm(obj=note)
    form.tags.data = [tag.name for tag in note.tags]
    print("Pre-update tags in note:", [tag.name for tag in note.tags])
    print("Form tags data (initial):", form.tags.data)

    if form.validate_on_submit():
        print("Form submitted successfully")
        print("Submitted form tags:", form.tags.data)
        print("Raw form data:", flask.request.form)  # Log raw form data
        note.title = form.title.data
        note.description = form.description.data
        note.tags = []  # Clear existing tags

        # Process tags
        if form.tags.data:
            for tag_name in form.tags.data:
                tag_name = tag_name.strip()
                if tag_name:  # Only process non-empty tags
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
                        db.session.flush()  # Ensure tag has an ID
                    note.tags.append(tag)
        else:
            print("No tags provided in form")

        note.updated_date = func.now()
        try:
            db.session.commit()
            print("Post-update tags:", [tag.name for tag in note.tags])
            flask.flash("Note updated successfully.", "success")
        except Exception as e:
            db.session.rollback()
            print("Database commit failed:", str(e))
            flask.flash("Error updating note.", "error")
        return flask.redirect(flask.url_for("index"))
    else:
        print("Form validation failed. Errors:", form.errors)
        print("Form tags data (after validation):", form.tags.data)
        print("Raw form data:", flask.request.form)  # Log raw form data

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
        tag=tag,
        notes=notes,
    )


# New routes for tag management
@app.route("/tags")
def tags_index():
    """Show all tags with note count"""
    db = models.db
    tags = db.session.execute(db.select(models.Tag).order_by(models.Tag.name)).scalars()

    # Count notes for each tag
    tag_counts = []
    for tag in tags:
        note_count = db.session.execute(
            db.select(func.count(models.Note.id))
            .select_from(models.Note)
            .where(models.Note.tags.any(id=tag.id))
        ).scalar()
        tag_counts.append({"tag": tag, "count": note_count})

    return flask.render_template(
        "tags-index.html",
        tag_counts=tag_counts,
    )


@app.route("/tags/update/<int:tag_id>", methods=["GET", "POST"])
def tags_update(tag_id):
    """Update tag name"""
    db = models.db
    tag = (
        db.session.execute(db.select(models.Tag).where(models.Tag.id == tag_id))
        .scalars()
        .first()
    )

    if not tag:
        flask.flash("Tag not found.", "error")
        return flask.redirect(flask.url_for("tags_index"))

    if flask.request.method == "POST":
        new_name = flask.request.form.get("name", "").strip()

        if not new_name:
            flask.flash("Tag name cannot be empty.", "error")
            return flask.render_template("tags-update.html", tag=tag)

        # Check if tag name already exists
        existing_tag = (
            db.session.execute(
                db.select(models.Tag).where(
                    models.Tag.name == new_name, models.Tag.id != tag_id
                )
            )
            .scalars()
            .first()
        )

        if existing_tag:
            flask.flash("Tag name already exists.", "error")
            return flask.render_template("tags-update.html", tag=tag)

        old_name = tag.name
        tag.name = new_name

        try:
            db.session.commit()
            flask.flash(
                f"Tag '{old_name}' updated to '{new_name}' successfully.", "success"
            )
            return flask.redirect(flask.url_for("tags_index"))
        except Exception as e:
            db.session.rollback()
            flask.flash("Error updating tag.", "error")
            return flask.render_template("tags-update.html", tag=tag)

    return flask.render_template("tags-update.html", tag=tag)


@app.route("/tags/delete/<int:tag_id>")
def tags_delete(tag_id):
    """Delete tag and remove it from all notes"""
    db = models.db
    tag = (
        db.session.execute(db.select(models.Tag).where(models.Tag.id == tag_id))
        .scalars()
        .first()
    )

    if not tag:
        flask.flash("Tag not found.", "error")
        return flask.redirect(flask.url_for("tags_index"))

    tag_name = tag.name

    try:
        # The relationship will automatically remove the tag from all notes
        # due to the many-to-many relationship
        db.session.delete(tag)
        db.session.commit()
        flask.flash(f"Tag '{tag_name}' deleted successfully.", "success")
    except Exception as e:
        db.session.rollback()
        flask.flash("Error deleting tag.", "error")

    return flask.redirect(flask.url_for("tags_index"))


@app.route("/tags/cleanup")
def tags_cleanup():
    """Remove unused tags (tags with no notes)"""
    db = models.db

    # Find tags that have no associated notes
    unused_tags = (
        db.session.execute(
            db.select(models.Tag).where(
                ~models.Tag.id.in_(db.select(models.note_tag_m2m.c.tag_id))
            )
        )
        .scalars()
        .all()
    )

    if not unused_tags:
        flask.flash("No unused tags found.", "info")
        return flask.redirect(flask.url_for("tags_index"))

    try:
        for tag in unused_tags:
            db.session.delete(tag)

        db.session.commit()
        flask.flash(f"Removed {len(unused_tags)} unused tags.", "success")
    except Exception as e:
        db.session.rollback()
        flask.flash("Error cleaning up tags.", "error")

    return flask.redirect(flask.url_for("tags_index"))


if __name__ == "__main__":
    app.run(debug=True)
