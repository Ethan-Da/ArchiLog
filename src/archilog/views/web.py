from flask import url_for, redirect, flash, abort
from sqlalchemy.exc import IntegrityError
import logging
from archilog.models import create_entry, delete_entry, get_entry, get_all_entries, update_entry
from archilog.services import import_from_csv, export_to_csv
from flask import Blueprint, render_template, Response, request
import io
from flask_wtf import FlaskForm
from wtforms import StringField, FloatField
from wtforms.validators import DataRequired
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash

class UpdateForm(FlaskForm):
    name = StringField("name", validators=[])
    price = FloatField("price", validators=[], default=None)
    category = StringField("category", validators=[])

class AddForm(FlaskForm):
    name = StringField("name", validators=[DataRequired()])
    price = FloatField("price", validators=[DataRequired()])
    category = StringField("category", validators=[])

web_ui = Blueprint("web_ui", __name__, url_prefix="/")


auth = HTTPBasicAuth()
users = {
    "Ethan": [generate_password_hash("admin"), ["admin", "user"]],
    "max": [generate_password_hash("max"), ["user"]]
}


#==============ROUTES WEBUI BLUEPRINT================#

@web_ui.route("/")
@auth.login_required
def show():
    return render_template("web_ui.html", list=get_all_entries(), addform=AddForm())

@web_ui.route("/delete/<id>")
@auth.login_required(role="admin")
def delete(id:str = None):
    delete_entry(uuid.UUID(id))
    return render_template("web_ui.html", list=get_all_entries(), addform=AddForm())

@web_ui.route("/add", methods=['POST'])
@auth.login_required(role="admin")
def add():
    form = AddForm()
    if form.validate_on_submit():
        create_entry(form.name.data, form.price.data, form.category.data)
    return render_template("web_ui.html", list=get_all_entries(), addform=AddForm())

@web_ui.route("/update_page/<id>", methods=["GET"])
@auth.login_required(role="admin")
def update_page(id:str = None):
    select = get_entry(uuid.UUID(id))
    return render_template("update.html", ligne=select, updateform=UpdateForm())

@web_ui.route("/do_update/<id>", methods=["POST"])
@auth.login_required(role="admin")
def do_update(id:str = None):
    form = UpdateForm()
    if form.validate_on_submit():
        update_entry(uuid.UUID(id), form.name.data, form.price.data, form.category.data)
    print(form.errors)
    return render_template("web_ui.html", list=get_all_entries(), addform=AddForm())

@web_ui.route("/importcsv", methods=['POST'])
@auth.login_required(role="admin")
def importcsv():
    file = request.files['csv-file']
    filestream = io.StringIO(file.stream.read().decode('utf8'))
    import_from_csv(filestream)
    return render_template("web_ui.html", list=get_all_entries())

@web_ui.route("/exportcsv", methods=['POST'])
@auth.login_required
def exportcsv():
    output = export_to_csv()
    response = Response(output.getvalue(), content_type='text/csv')
    response.headers['Content-Disposition'] = 'attachment; filename="export.csv"'
    return response

 #==============ERROR================#

@web_ui.errorhandler(IntegrityError)
def handle_internal_error(error):
    flash("Erreur interne du serveur", "error")
    logging.exception(error)
    return redirect("/")

@web_ui.errorhandler(500)
def handle_internal_error(error):
    flash("Erreur interne du serveur", "error")
    return redirect("/")


 #==============AUTHENTIFICATION================#

@auth.verify_password
def verify_password(username, password):
    if username in users and \
            check_password_hash(users.get(username)[0], password):
        return username

@auth.get_user_roles
def get_user_roles(username):
    return users.get(username)[1]