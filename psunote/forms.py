from wtforms_sqlalchemy.orm import model_form
from flask_wtf import FlaskForm
from wtforms import Field, widgets, StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired

import models


class TagListField(Field):
    """
    Custom field สำหรับจัดการ tags ที่รับค่าแบบ comma-separated
    และแปลงเป็น list ของ tag names
    """

    widget = widgets.TextInput()

    def __init__(self, label="", validators=None, remove_duplicates=True, **kwargs):
        super().__init__(label, validators, **kwargs)
        self.remove_duplicates = remove_duplicates
        self.data = []

    def process_formdata(self, valuelist):
        """
        ประมวลผลข้อมูลจากฟอร์ม แปลงจาก comma-separated string เป็น list
        """
        data = []
        if valuelist:
            data = [x.strip() for x in valuelist[0].split(",") if x.strip()]

        if not self.remove_duplicates:
            self.data = data
            return

        # ลบ tag ที่ซ้ำ
        self.data = []
        for d in data:
            if d not in self.data:
                self.data.append(d)

    def _value(self):
        """
        แปลง list ของ tags กลับเป็น comma-separated string สำหรับแสดงในฟอร์ม
        """
        if self.data:
            return ", ".join(self.data)
        else:
            return ""


BaseNoteForm = model_form(
    models.Note,
    base_class=FlaskForm,
    exclude=["created_date", "updated_date"],
    db_session=models.db.session,
)


class NoteForm(BaseNoteForm):
    """
    ฟอร์มสำหรับสร้างและแก้ไข Note พร้อมการจัดการ tags
    """

    tags = TagListField(
        "Tags (คั่นด้วยจุลภาค)", description="เช่น: python, flask, web development"
    )
    submit = SubmitField("บันทึก")


class TagForm(FlaskForm):
    """
    ฟอร์มสำหรับสร้าง Tag ใหม่
    """

    name = StringField(
        "ชื่อ Tag", validators=[DataRequired()], description="ชื่อ tag ที่จะสร้าง"
    )
    submit = SubmitField("สร้าง Tag")


class SearchForm(FlaskForm):
    """
    ฟอร์มสำหรับค้นหา Note
    """

    query = StringField("ค้นหา", description="ค้นหาใน title, description หรือ tag")
    submit = SubmitField("ค้นหา")
