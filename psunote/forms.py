from wtforms_sqlalchemy.orm import model_form
from flask_wtf import FlaskForm
from wtforms import Field, widgets
from wtforms.validators import Optional
import models


class TagListField(Field):
    widget = widgets.TextInput()

    def __init__(self, label="", validators=None, remove_duplicates=True, **kwargs):
        if validators is None:
            validators = [Optional()]  # Allow empty input
        super().__init__(label, validators, **kwargs)
        self.remove_duplicates = remove_duplicates
        self.data = []

    def process_formdata(self, valuelist):
        self.data = []
        if valuelist and valuelist[0]:
            data = [x.strip() for x in valuelist[0].split(",") if x.strip()]
            if self.remove_duplicates:
                self.data = list(
                    dict.fromkeys(data)
                )  # Remove duplicates while preserving order
            else:
                self.data = data

    def _value(self):
        if self.data:
            return ", ".join(self.data)
        return ""


BaseNoteForm = model_form(
    models.Note,
    base_class=FlaskForm,
    exclude=["created_date", "updated_date"],
    db_session=models.db.session,
)


class NoteForm(BaseNoteForm):
    tags = TagListField("Tag")
