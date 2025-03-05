from flask import url_for, redirect, flash, abort
from flask import request

from archilog.models import *
from archilog.services import import_from_csv, export_to_csv

from flask import Blueprint, render_template, Response, request
import io

web_ui = Blueprint("web_ui", __name__, url_prefix="/")
api = Blueprint("api", __name__, url_prefix="/api")

@web_ui.route("/<page>")
def show(page):
    return render_template(f"{page}.html", list=get_all_entries())

@web_ui.route("/delete/<id>")
def delete(id:str = None):
    delete_entry(uuid.UUID(id))
    return render_template("web_ui.html", list=get_all_entries())

@web_ui.route("/add", methods=['POST'])
def add():
    result = request.form
    create_entry(result["Name"], float(result["Price"]), result['Category'])
    return render_template("web_ui.html", list=get_all_entries())

@web_ui.route("/update", methods=['POST'])
def update():
    result = request.form
    price = None
    if result["Price"] != '':
        price = float(result["Price"])
    update_entry(uuid.UUID(result['id']), result['Name'], price, result['Category'])
    return render_template("web_ui.html", list=get_all_entries())

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

@web_ui.errorhandler(500)
def handle_internal_error(error):
    flash("Erreur interne du serveur", "error")
    return redirect("/web_ui")



if __name__ == "__main__":

    print(url_for('delete', id='c7c176b6a2e74186b510f76035e284f0'))
