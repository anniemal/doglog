import flask
from flask import request, redirect, url_for, flash
import flask.ext.wtf as wtf
from sqlalchemy import Integer, String, DateTime, Text
import sqlalchemy.orm
import wtforms
from flask import Blueprint

class Skaffold(object):
    def __init__(self, app, model, session):
        self.model = model
        self.model_name = model.__name__.lower()
        self.blueprint = Blueprint("admin_%s"%self.model_name, __name__, template_folder="templates")
        self.app = app
        self.validator = None
        self.session = session
        self.urls = {
            'view_url': "admin_%s.view"%self.model_name,
            'edit_url': "admin_%s.edit"%self.model_name,
            'new_url' : "admin_%s.new"%self.model_name}

        self.setup()

    def configure_routes(self):
        routes = [
                ("/", ["GET"], self.list),
                ("/new", ["GET"], self.new),
                ("/<int:id>/edit", ["GET"], self.edit),
                ("/<int:id>/", ["GET"], self.view),
                ("/<int:id>/", ["POST"], self.save),
                ("/", ["POST"], self.save)
                ]
        for url, methods, view in routes:
            self.blueprint.route(url, methods=methods)(view)

    def setup(self):
        self.generate_validator()
        self.configure_routes()
        self.app.register_blueprint(self.blueprint, url_prefix="/admin/%s"%self.model_name)

    def list(self):
        units = self.model.query.limit(100).all()
        properties = self.properties

        units = [ ModelWrapper(unit) for unit in units ]
        return flask.render_template("list.html", units=units, properties = properties,
                h1="Listing: %s"%self.model_name.capitalize(),
                **self.urls)

    def new(self):
        unit = self.model()
        form = self.validator()
        h1 = "Create new %s"%self.model_name.capitalize()
        return flask.render_template("edit.html", unit=unit, form=form, model_name=self.model_name, h1=h1)
                

    def view(self, id):
        unit = self.model.query.get(id)
        h1 = "%s: %d"%(self.model_name.capitalize(), id)
        unit = ModelWrapper(unit)
        return flask.render_template("view.html", unit=unit, model=self.model, h1=h1,
                properties = self.properties,
                **self.urls 
                )

    @property
    def properties(self):
        return [ prop for prop in self.model.__mapper__.iterate_properties if not isinstance(prop, sqlalchemy.orm.RelationshipProperty) ]

    def save(self, id=None):
        form = self.validator()
        if id:
            unit = self.model.query.get(id)
        else:
            unit = self.model()
            self.session.add(unit)

        if form.validate_on_submit():
            form.populate_obj(unit)
            self.session.commit()
            self.session.refresh(unit)
            flash("Successfully saved %s object %d"%(self.model_name, unit.id), "success")
            
            return redirect(url_for("admin_%s.list"%(self.model_name)))

        else:
            self.session.rollback()
            if id:
                h1 = "%s: %d"%(self.model_name.capitalize(), id)
            else:
                h1 = "Create new %s"%self.model_name.capitalize()
            return flask.render_template("edit.html", unit=unit, form=form, model_name=self.model_name, h1=h1)

    def edit(self, id):
        unit = self.model.query.get(id)
        form = self.validator(request.form, unit)
        h1 = "%s: %d"%(self.model_name.capitalize(), id)
        return flask.render_template("edit.html", unit=unit, form=form, model_name=self.model_name, h1=h1)

    def choose_field_validator(self, db_type, field_name, prop):
        type_map = { "VARCHAR": wtf.TextField,
                     "INTEGER": wtf.IntegerField,
                     "DATETIME": DateTimeField,
                     "DATE": DateField,
                     "TEXT": wtf.TextAreaField
                }

        field = None
        if field_name.lower() == "password":
            field = wtf.PasswordField

        if not field:
            field = type_map[db_type]

        validators = []
        if field_name.lower() == "email":
            validators.append(wtf.validators.Email())
        elif field_name.lower().endswith("_url"):
            validators.append(wtf.validators.URL())
        
        if not prop.columns[0].nullable and not prop.columns[0].default:
            validators.append(wtf.validators.Required())
        else:
            validators.append(wtf.validators.Optional())
        
        try:
            field_size = prop.columns[0].type.length
            if field_size:
                validators.append(wtf.validators.length(max=field_size))
        except AttributeError, e:
            pass

        return field(validators=validators)


    def generate_validator(self):
        validator_name = self.model_name.capitalize() + "Form"
        fields = {}
        model = self.model
        props = [ prop for prop in model.__mapper__.iterate_properties if not isinstance(prop, sqlalchemy.orm.RelationshipProperty) and not prop.columns[0].primary_key ]

        for prop in props:
            field_name = prop.key
            # Map the SA type to the WTForms type
            field_type = str(prop.columns[0].type).split("(")[0]
            fields[field_name] = self.choose_field_validator(field_type, field_name, prop)

        validator_form = type(validator_name, (wtf.Form, ),
                fields)

        self.validator = validator_form


class DateTimeInput(wtforms.widgets.Input):
    input_type = "datetime"

class DateInput(wtforms.widgets.Input):
    input_type = "date"

class DateTimeField(wtf.DateTimeField):
    widget = DateTimeInput()

class DateField(wtf.DateField):
    widget = DateInput()

class ModelWrapper(object):
    def __init__(self, wrapped):
        self.wrapped = wrapped
        self.id = wrapped.id

    def getattr(self, attr):
        return getattr(self.wrapped, attr)
