"""
    Flask-Navigate - Another flask extension that provides Navigation menus.

    Author: Bill Schumacher <bill@servernet.co>
    License: LGPLv3
    Copyright: 2016 Bill Schumacher, Cerebral Power
** GNU Lesser General Public License Usage
** This file may be used under the terms of the GNU Lesser
** General Public License version 3 as published by the Free Software
** Foundation and appearing in the file LICENSE.LGPLv3 included in the
** packaging of this file. Please review the following information to
** ensure the GNU Lesser General Public License version 3 requirements
** will be met: https://www.gnu.org/licenses/lgpl.html.


    Some code copied from:
    https://github.com/maxcountryman/flask-login and https://github.com/mattupstate/flask-security  See LICENSE
"""
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
