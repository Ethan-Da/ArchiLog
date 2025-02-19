import uuid

from flask import Flask
from flask import render_template
from flask import url_for
from flask import request


from archilog.models import *
from archilog.services import import_from_csv

app = Flask(__name__)

@app.route("/budget/")
def init():
    return render_template("interface.html", list=get_all_entries())

@app.route("/budget/delete/<id>")
def delete(id:str = None):
    delete_entry(uuid.UUID(id))
    return render_template("interface.html", list=get_all_entries())

@app.route("/budget/add/", methods=['POST'])
def add():
    result = request.form
    create_entry(result["Name"], float(result["Price"]), result['Category'])
    return render_template("interface.html", list=get_all_entries())

@app.route("/budget/update/", methods=['POST'])
def update():
    result = request.form
    price = None
    if result["Price"] != '':
        price = float(result["Price"])
    update_entry(uuid.UUID(result['id']), result['Name'], price, result['Category'])
    return render_template("interface.html", list=get_all_entries())

@app.route("/budget/addcsv/", methods=['POST'])
def addcsv():
    file = request.files['file'].stream
    import_from_csv(file)
    return render_template("interface.html", list=get_all_entries())

if __name__ == "__main__":

    print(url_for('delete', id='c7c176b6a2e74186b510f76035e284f0'))
