import flask
from sqlalchemy import or_

import models
import forms


app = flask.Flask(__name__)
app.config["SECRET_KEY"] = "This is secret key"
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://pun:123456@localhost:5432/coedb"

models.init_app(app)


# Template Context Processor สำหรับส่งข้อมูลไปยัง Template ทุกครั้ง
@app.context_processor
def inject_sidebar_data():
    """
    ส่งข้อมูล tags ทั้งหมดไปยัง template เพื่อแสดงใน sidebar
    และส่งฟอร์มค้นหาไปด้วย
    """
    db = models.db
    all_tags = (
        db.session.execute(db.select(models.Tag).order_by(models.Tag.name))
        .scalars()
        .all()
    )

    search_form = forms.SearchForm()

    return dict(sidebar_tags=all_tags, search_form=search_form)


@app.route("/")
def index():
    """
    หน้าแรก (Dashboard) แสดง:
    - จำนวน note และ tag ทั้งหมด
    - รายการ note ทั้งหมด
    - สามารถค้นหาและกรองตาม tag ได้
    """
    db = models.db

    # รับพารามิเตอร์จาก URL
    search_query = flask.request.args.get("search", "")
    tag_filter = flask.request.args.get("tag", "")

    # เริ่มต้น query
    query = db.select(models.Note)

    # ถ้ามีการค้นหา
    if search_query:
        query = query.where(
            or_(
                models.Note.title.ilike(f"%{search_query}%"),
                models.Note.description.ilike(f"%{search_query}%"),
                models.Note.tags.any(models.Tag.name.ilike(f"%{search_query}%")),
            )
        )

    # ถ้ามีการกรองตาม tag
    if tag_filter:
        query = query.where(models.Note.tags.any(models.Tag.name == tag_filter))

    # จัดเรียงตาม updated_date ล่าสุด
    query = query.order_by(models.Note.updated_date.desc())

    notes = db.session.execute(query).scalars().all()

    # นับจำนวนทั้งหมด
    total_notes = db.session.execute(db.select(models.Note)).scalars().all()
    total_tags = db.session.execute(db.select(models.Tag)).scalars().all()

    return flask.render_template(
        "index.html",
        notes=notes,
        total_notes=len(total_notes),
        total_tags=len(total_tags),
        search_query=search_query,
        tag_filter=tag_filter,
    )


@app.route("/notes/create", methods=["GET", "POST"])
def notes_create():
    """
    สร้าง Note ใหม่ พร้อมการจัดการ tags
    - สร้าง tag ใหม่ถ้ายังไม่มี
    - เพิ่ม tag ที่มีอยู่แล้วให้กับ note
    """
    form = forms.NoteForm()
    if not form.validate_on_submit():
        print("error", form.errors)
        return flask.render_template(
            "notes-create.html",
            form=form,
        )

    # สร้าง note ใหม่
    note = models.Note()
    form.populate_obj(note)
    note.tags = []

    db = models.db

    # จัดการ tags
    for tag_name in form.tags.data:
        if tag_name:  # ตรวจสอบว่าไม่ใช่ string ว่าง
            # หา tag ที่มีอยู่แล้ว
            tag = (
                db.session.execute(
                    db.select(models.Tag).where(models.Tag.name == tag_name)
                )
                .scalars()
                .first()
            )

            # ถ้าไม่มี tag นี้ ให้สร้างใหม่
            if not tag:
                tag = models.Tag(name=tag_name)
                db.session.add(tag)

            note.tags.append(tag)

    db.session.add(note)
    db.session.commit()

    flask.flash(f'สร้าง Note "{note.title}" เรียบร้อยแล้ว!', "success")
    return flask.redirect(flask.url_for("index"))


@app.route("/notes/<int:note_id>/edit", methods=["GET", "POST"])
def notes_edit(note_id):
    """
    แก้ไข Note ที่มีอยู่
    - แก้ไข title, description
    - เพิ่ม/ลบ/สร้าง tags ใหม่
    """
    db = models.db
    note = (
        db.session.execute(db.select(models.Note).where(models.Note.id == note_id))
        .scalars()
        .first()
    )

    if not note:
        flask.flash("ไม่พบ Note ที่ต้องการแก้ไข", "error")
        return flask.redirect(flask.url_for("index"))

    form = forms.NoteForm(obj=note)

    # ตั้งค่า tags ใน form
    if flask.request.method == "GET":
        form.tags.data = [tag.name for tag in note.tags]

    if form.validate_on_submit():
        # อัปเดต title และ description
        note.title = form.title.data
        note.description = form.description.data

        # ล้าง tags เดิม
        note.tags.clear()

        # เพิ่ม tags ใหม่
        for tag_name in form.tags.data:
            if tag_name:  # ตรวจสอบว่าไม่ใช่ string ว่าง
                # หา tag ที่มีอยู่แล้ว
                tag = (
                    db.session.execute(
                        db.select(models.Tag).where(models.Tag.name == tag_name)
                    )
                    .scalars()
                    .first()
                )

                # ถ้าไม่มี tag นี้ ให้สร้างใหม่
                if not tag:
                    tag = models.Tag(name=tag_name)
                    db.session.add(tag)

                note.tags.append(tag)

        db.session.commit()
        flask.flash(f'แก้ไข Note "{note.title}" เรียบร้อยแล้ว!', "success")
        return flask.redirect(flask.url_for("index"))

    return flask.render_template(
        "notes-edit.html",
        form=form,
        note=note,
    )


@app.route("/notes/<int:note_id>/delete", methods=["POST"])
def notes_delete(note_id):
    """
    ลบ Note
    """
    db = models.db
    note = (
        db.session.execute(db.select(models.Note).where(models.Note.id == note_id))
        .scalars()
        .first()
    )

    if not note:
        flask.flash("ไม่พบ Note ที่ต้องการลบ", "error")
        return flask.redirect(flask.url_for("index"))

    note_title = note.title
    db.session.delete(note)
    db.session.commit()

    flask.flash(f'ลบ Note "{note_title}" เรียบร้อยแล้ว!', "success")
    return flask.redirect(flask.url_for("index"))


@app.route("/tags")
def tags_list():
    """
    แสดงรายการ tag ทั้งหมด พร้อมจำนวน note ในแต่ละ tag
    """
    db = models.db
    tags = (
        db.session.execute(db.select(models.Tag).order_by(models.Tag.name))
        .scalars()
        .all()
    )

    # นับจำนวน note ในแต่ละ tag
    tag_counts = {}
    for tag in tags:
        count = (
            db.session.execute(
                db.select(models.Note).where(models.Note.tags.any(id=tag.id))
            )
            .scalars()
            .all()
        )
        tag_counts[tag.id] = len(count)

    return flask.render_template(
        "tags-list.html",
        tags=tags,
        tag_counts=tag_counts,
    )


@app.route("/tags/create", methods=["GET", "POST"])
def tags_create():
    """
    สร้าง Tag ใหม่
    """
    form = forms.TagForm()
    if form.validate_on_submit():
        db = models.db

        # ตรวจสอบว่ามี tag นี้อยู่แล้วหรือไม่
        existing_tag = (
            db.session.execute(
                db.select(models.Tag).where(models.Tag.name == form.name.data)
            )
            .scalars()
            .first()
        )

        if existing_tag:
            flask.flash(f'Tag "{form.name.data}" มีอยู่แล้ว!', "warning")
        else:
            tag = models.Tag(name=form.name.data)
            db.session.add(tag)
            db.session.commit()
            flask.flash(f'สร้าง Tag "{tag.name}" เรียบร้อยแล้ว!', "success")

        return flask.redirect(flask.url_for("tags_list"))

    return flask.render_template(
        "tags-create.html",
        form=form,
    )


@app.route("/tags/<tag_name>")
def tags_view(tag_name):
    """
    แสดง note ทั้งหมดที่มี tag นี้
    รองรับการค้นหาเพิ่มเติมภายใน tag
    """
    db = models.db

    # หา tag
    tag = (
        db.session.execute(db.select(models.Tag).where(models.Tag.name == tag_name))
        .scalars()
        .first()
    )

    if not tag:
        flask.flash(f'ไม่พบ Tag "{tag_name}"', "error")
        return flask.redirect(flask.url_for("index"))

    # รับพารามิเตอร์ค้นหา
    search_query = flask.request.args.get("search", "")

    # เริ่มต้น query
    query = db.select(models.Note).where(models.Note.tags.any(id=tag.id))

    # ถ้ามีการค้นหา
    if search_query:
        query = query.where(
            or_(
                models.Note.title.ilike(f"%{search_query}%"),
                models.Note.description.ilike(f"%{search_query}%"),
            )
        )

    # จัดเรียงตาม updated_date ล่าสุด
    query = query.order_by(models.Note.updated_date.desc())

    notes = db.session.execute(query).scalars().all()

    return flask.render_template(
        "tags-view.html",
        tag=tag,
        tag_name=tag_name,
        notes=notes,
        search_query=search_query,
    )


@app.route("/tags/<int:tag_id>/edit", methods=["GET", "POST"])
def tags_edit(tag_id):
    """
    แก้ไข Tag ที่มีอยู่
    """
    db = models.db
    tag = (
        db.session.execute(db.select(models.Tag).where(models.Tag.id == tag_id))
        .scalars()
        .first()
    )

    if not tag:
        flask.flash("ไม่พบ Tag ที่ต้องการแก้ไข", "error")
        return flask.redirect(flask.url_for("tags_list"))

    form = forms.TagForm(obj=tag)

    if form.validate_on_submit():
        # ตรวจสอบว่ามี tag ชื่อนี้อยู่แล้วหรือไม่ (ยกเว้นตัวเอง)
        existing_tag = (
            db.session.execute(
                db.select(models.Tag).where(
                    models.Tag.name == form.name.data, models.Tag.id != tag_id
                )
            )
            .scalars()
            .first()
        )

        if existing_tag:
            flask.flash(f'Tag "{form.name.data}" มีอยู่แล้ว!', "warning")
        else:
            old_name = tag.name
            tag.name = form.name.data
            db.session.commit()
            flask.flash(
                f'แก้ไข Tag จาก "{old_name}" เป็น "{tag.name}" เรียบร้อยแล้ว!', "success"
            )
            return flask.redirect(flask.url_for("tags_list"))

    return flask.render_template(
        "tags-edit.html",
        form=form,
        tag=tag,
    )


@app.route("/tags/<int:tag_id>/delete", methods=["POST"])
def tags_delete(tag_id):
    """
    ลบ Tag
    """
    db = models.db
    tag = (
        db.session.execute(db.select(models.Tag).where(models.Tag.id == tag_id))
        .scalars()
        .first()
    )

    if not tag:
        flask.flash("ไม่พบ Tag ที่ต้องการลบ", "error")
        return flask.redirect(flask.url_for("tags_list"))

    # ตรวจสอบว่ามี Notes ที่ใช้ tag นี้หรือไม่
    notes_using_tag = (
        db.session.execute(
            db.select(models.Note).where(models.Note.tags.any(id=tag.id))
        )
        .scalars()
        .all()
    )

    tag_name = tag.name

    if notes_using_tag:
        # ถ้ามี Notes ใช้ tag นี้ ให้เอา tag ออกจาก Notes ทั้งหมดก่อน
        for note in notes_using_tag:
            note.tags = [t for t in note.tags if t.id != tag.id]

        flask.flash(
            f'ลบ Tag "{tag_name}" เรียบร้อยแล้ว (เอาออกจาก {len(notes_using_tag)} Notes)',
            "success",
        )
    else:
        flask.flash(f'ลบ Tag "{tag_name}" เรียบร้อยแล้ว!', "success")

    db.session.delete(tag)
    db.session.commit()

    return flask.redirect(flask.url_for("tags_list"))


@app.route("/search")
def search():
    """
    หน้าค้นหาแยก (ถ้าต้องการ)
    """
    query = flask.request.args.get("q", "")
    if query:
        return flask.redirect(flask.url_for("index", search=query))
    else:
        return flask.redirect(flask.url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
