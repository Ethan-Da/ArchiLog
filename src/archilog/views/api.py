import uuid

from flask import Blueprint, Response, jsonify
from pydantic import BaseModel, Field
from archilog.models import create_entry, delete_entry, get_entry, get_all_entries, update_entry
from flask_httpauth import HTTPTokenAuth
from spectree import SpecTree, SecurityScheme, BaseFile
from archilog.services import export_to_csv, import_from_csv
import io


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

# ========================== Tokens =============================#

auth = HTTPTokenAuth(scheme='Bearer')

valid_tokens = {
    "829HKZBDIY89I2HZ": {'user': 'admin', 'roles': ["admin", "user"]},
    "UIYUI9018UZHA902": {'user': 'lambda', 'roles': ["user"]}
}


# ========================== ROUTES API =============================#

# ==CRUD==#

@api.route("/entries", methods=["GET"])
@spec.validate(tags=["api"])
@auth.login_required(role='user')
def get_all():
    entries = get_all_entries()
    return entries


@api.route("/entries/<id>", methods=["GET"])
@spec.validate(tags=["api"])
@auth.login_required(role='user')
def get(id):
    entry = get_entry(id)
    return entry


@api.route("/entries", methods=["POST"])
@spec.validate(tags=["api"])
@auth.login_required(role='admin')
def add(json: EntryData):
    create_entry(json.name, json.amount, json.category)
    return jsonify(message="Entry added")


@api.route("/entries/<id>", methods=["PUT"])
@spec.validate(tags=["api"])
@auth.login_required(role='admin')
def update(id, json: EntryData):
    update_entry(id, json.name, json.amount, json.category)
    return jsonify(message="Entry updated")


@api.route("/entries/<id>", methods=["DELETE"])
@spec.validate(tags=["api"])
@auth.login_required(role='admin')
def delete(id):
    delete_entry(uuid.UUID(id))
    return jsonify(message="Entry deleted")


# ==RPC==#

class File(BaseModel):
    file: BaseFile


@api.route("/entries/export", methods=["POST"])
@spec.validate(tags=["api"])
@auth.login_required(role='admin')
def export_csv():
    output = export_to_csv()
    response = Response(output.getvalue(), content_type='text/csv')
    response.headers['Content-Disposition'] = 'attachment; filename="export.csv"'
    return response


@api.route("/entries/import", methods=["POST"])
@spec.validate(tags=["api"])
@auth.login_required(role='admin')
def import_csv(form: File):
    filestream = io.StringIO(form.file.stream.read().decode('utf8'))
    import_from_csv(filestream)
    return jsonify(message="CSV Imported")


# ==============ERROR HANDLER================#

@api.errorhandler(500)
def handle_internal_error(error):
    json = {
        'Message': 'Erreur 500',
        'Result': error.description,
    }
    return jsonify(json)


# ==============AUTHENTIFICATION================#

@auth.verify_token
def verify_token(token):
    print(token)
    if token in valid_tokens:
        return valid_tokens.get(token)
    return False


@auth.get_user_roles
def get_user_roles(token):
    return token['roles']
