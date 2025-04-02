from dataclasses import replace
from io import StringIO, BytesIO

from flask import Blueprint, render_template, Response, request

from pydantic import BaseModel, Field
from sqlalchemy.testing.provision import follower_url_from_main

from archilog.models import create_entry, delete_entry, get_entry, get_all_entries, update_entry
from flask_httpauth import HTTPTokenAuth
from spectree import SpecTree, SecurityScheme, BaseFile

from archilog.services import export_to_csv, import_from_csv


class EntryData(BaseModel):
    name: str = Field(min_length=2, max_length=40)
    amount: float = Field(gt=0)
    category: str = Field(min_length=2, max_length=40)

api = Blueprint("api", __name__, url_prefix="/api")

spec = SpecTree("flask",
    security_schemes=[
        SecurityScheme(
            name="bearer_token",
            data={"type": "http", "scheme": "bearer"}
        )
    ],
    security=[{"bearer_token": []}])

#========================== Tokens =============================#

auth = HTTPTokenAuth(scheme='Bearer')

valid_tokens = {
    "829HKZBDIY89I2HZ" : {'user' : 'test', 'roles' : ["admin", "user"]},
    "UIYUI9018UZHA902" : {'user' : 'test2','roles' : ["user"]}
}



#========================== ROUTES API =============================#

#==CRUD==#

@api.route("/entries", methods=["GET"])
@spec.validate(tags=["api"])
@auth.login_required(role='admin')
def get_all():
    entries = get_all_entries()
    return entries

@api.route("/entries/<id>", methods=["GET"])
@spec.validate(tags=["api"])
@auth.login_required
def get(id):
    entry = get_entry(id)
    return entry

@api.route("/entries", methods=["POST"])
@spec.validate(tags=["api"])
@auth.login_required()
def add(json: EntryData):
    create_entry(json["name"], json["amount"], json["category"])
    return

@api.route("/entries/<id>", methods=["PATCH"])
@spec.validate(tags=["api"])
@auth.login_required()
def update(id, json: EntryData):
    update_entry(id, json["name"], json["amount"], json["category"])
    return

@api.route("/entries/<id>", methods=["DELETE"])
@spec.validate(tags=["api"])
@auth.login_required()
def delete(id):
    delete_entry(id)
    return

#==RPC==#

class File(BaseModel):
    file: BaseFile

@api.route("/entries/export", methods=["POST"])
@spec.validate(tags=["api"])
@auth.login_required()
def export_csv():
    file = export_to_csv()
    return file

@api.route("/entries/import", methods=["POST"])
@spec.validate(tags=["api"])
@auth.login_required()
def import_csv(form : File):
    return import_from_csv(form.file)


 #==============AUTHENTIFICATION================#

@auth.verify_token
def verify_token(token):
    print(token)
    if token in valid_tokens:
        return valid_tokens.get(token)
    return False

@auth.get_user_roles
def get_user_roles(token):
    print(valid_tokens.get(token)['roles'])
    return valid_tokens.get(token)['roles']

