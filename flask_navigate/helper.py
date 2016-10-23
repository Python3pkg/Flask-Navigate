from flask import current_app, url_for, redirect
from werkzeug.local import LocalProxy
from ._compat import iteritems

_navigate = LocalProxy(lambda: current_app.extensions['navigate'])
_datastore = LocalProxy(lambda: _navigate.datastore)


def dot(a, b):
    return "{}.{}".format(a, b)


def view_context():
    return {
        'add_nav_endpoint': dot(_navigate.blueprint_name, _navigate.admin_add_nav_endpoint),
        'edit_nav_endpoint': dot(_navigate.blueprint_name, _navigate.admin_edit_nav_endpoint),
        'delete_nav_endpoint': dot(_navigate.blueprint_name, _navigate.admin_delete_nav_endpoint),
        'list_nav_endpoint': dot(_navigate.blueprint_name, _navigate.admin_list_nav_endpoint),
        'add_nav_item_endpoint': dot(_navigate.blueprint_name, _navigate.admin_add_nav_item_endpoint),
        'edit_nav_item_endpoint': dot(_navigate.blueprint_name, _navigate.admin_edit_nav_item_endpoint),
        'delete_nav_item_endpoint': dot(_navigate.blueprint_name, _navigate.admin_delete_nav_item_endpoint),
        'url_for': url_for,

    }


def populate_form(form, obj):
    for key in form.data_without_submit.keys():
        if key in obj.__table__.columns.keys():
            form.__getattribute__(key).data = obj.__getattribute__(key)


def update_object(form, obj):
    dirty = False
    for key, value in iteritems(form.data_without_submit):
        if key in obj.__table__.columns.keys():
            obj.__setattr__(key, value)
            dirty = True
    if dirty:
        _datastore.commit()
