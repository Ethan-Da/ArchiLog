from flask import url_for, redirect, flash, abort
from flask import request
from sqlalchemy.exc import IntegrityError
from unicodedata import category
import logging
from archilog.models import *
from archilog.services import import_from_csv, export_to_csv

from flask import Blueprint, render_template, Response, request
import io

from flask_wtf import FlaskForm
from wtforms import StringField, FloatField
from wtforms.validators import DataRequired

class UpdateForm(FlaskForm):

    name = StringField("name", validators=[])
    price = FloatField("price", validators=[])
    category = StringField("category", validators=[])

class AddForm(FlaskForm):
    name = StringField("name", validators=[DataRequired()])
    price = FloatField("price", validators=[DataRequired()])
    category = StringField("category", validators=[])

web_ui = Blueprint("web_ui", __name__, url_prefix="/")
api = Blueprint("api", __name__, url_prefix="/api")


@web_ui.route("/")
def show():
    return render_template("web_ui.html", list=get_all_entries(), addform=AddForm())

@web_ui.route("/delete/<id>")
def delete(id:str = None):
    delete_entry(uuid.UUID(id))
    return render_template("web_ui.html", list=get_all_entries(), addform=AddForm())

@web_ui.route("/add", methods=['POST'])
def add():
    form = AddForm()
    if form.validate_on_submit():
        create_entry(form.name.data, form.price.data, form.category.data)
    return render_template("web_ui.html", list=get_all_entries(), addform=form)

@web_ui.route("/update_page/<id>", methods=["GET"])
def update_page(id:str = None):
    select = get_entry(uuid.UUID(id))
    return render_template("update.html", ligne=select, updateform=UpdateForm())

@web_ui.route("/do_update/<id>", methods=["POST"])
def do_update(id:str = None):
    form = UpdateForm()
    if form.validate_on_submit():
        update_entry(uuid.UUID(id), form.name.data, form.price.data, form.category.data)
    print(form.errors)
    return render_template("web_ui.html", list=get_all_entries(), addform=AddForm())

@web_ui.route("/importcsv", methods=['POST'])
def importcsv():
    file = request.files['csv-file']
    filestream = io.StringIO(file.stream.read().decode('utf8'))
    import_from_csv(filestream)
    return render_template("web_ui.html", list=get_all_entries())

@web_ui.route("/exportcsv", methods=['POST'])
def exportcsv():
    output = export_to_csv()
    response = Response(output.getvalue(), content_type='text/csv')
    response.headers['Content-Disposition'] = 'attachment; filename="export.csv"'
    return response

@web_ui.errorhandler(IntegrityError)
def handle_internal_error(error):
    flash("Erreur interne du serveur", "error")
    logging.exception(error)
    return redirect("/")

@web_ui.errorhandler(500)
def handle_internal_error(error):
    flash("Erreur interne du serveur", "error")
    return redirect("/")
