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
from flask import current_app, url_for, redirect, request, flash, get_flashed_messages
from flask_bs import render_content_with_bootstrap
from flask_wtf_flexwidgets import css_template, render_form_template
from jinja2 import Template
from werkzeug.local import LocalProxy

from ._compat import iteritems

_navigate = LocalProxy(lambda: current_app.extensions['navigate'])
_datastore = LocalProxy(lambda: _navigate.datastore)


def dot(a, b):
    return "{}.{}".format(a, b)


def endpoint(ep):
    return dot(_navigate.blueprint_name, ep)


def view_context():
    return {
        'add_nav_endpoint': endpoint(_navigate.admin_add_nav_endpoint),
        'edit_nav_endpoint': endpoint(_navigate.admin_edit_nav_endpoint),
        'delete_nav_endpoint': endpoint(_navigate.admin_delete_nav_endpoint),
        'list_nav_endpoint': endpoint(_navigate.admin_list_nav_endpoint),
        'add_nav_item_endpoint': endpoint(_navigate.admin_add_nav_item_endpoint),
        'add_sub_nav_item_endpoint': endpoint(_navigate.admin_add_sub_nav_item_endpoint),
        'edit_nav_item_endpoint': endpoint(_navigate.admin_edit_nav_item_endpoint),
        'delete_nav_item_endpoint': endpoint(_navigate.admin_delete_nav_item_endpoint),
        'url_for': url_for,
        'get_flashed_messages': get_flashed_messages
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


def render(template, **kwargs):
    return render_content_with_bootstrap(body=template.render(**kwargs), head="<style>" + css_template + "</style>")


def validate_on_submit(form):
    form.process(formdata=request.form)
    if form.validate():
        return True
    return False


def is_get():
    if request.method == 'GET':
        return True
    return False


def model_exists(model, model_id=None, filters=list(), not_found_url=None):
    if len(filters):
        query = _datastore.db.query(model)
        for f in filters:
            if f.operator == "==":
                query.filter(f.column == f.value)
            elif f.operator == "!=":
                query.filter(f.column != f.value)
            else:
                raise NotImplementedError
        if model_id is not None:
            query.filter(model.id == model_id)
        obj = query.first()
    else:
        obj = _datastore.get(model, model_id)
    if not obj:
        flash("{} was not found...".format(model.info['label']), "error")
        if not_found_url is not None:
            if type(not_found_url) == str:
                return redirect(not_found_url)
    return obj


class Filter(object):
    def __init__(self, column, value, operator):
        self.column = column
        self.value = value
        self.operator = operator


def view_function(get_template, **kwargs):
    return render(get_template, **kwargs)


def add_view_function(template=Template(""), name="", form=None, model=None, edit_endpoint=None, back_endpoint=None,
                      back_endpoint_kwargs={}, additional_model_fields={}, context={}, edit_uses_id=True,
                      edit_endpoint_kwargs={}):
    if is_get():
        rendered_form = render_form_template(form)
        return render(template, form=rendered_form, back_endpoint=back_endpoint,
                      back_endpoint_kwargs=back_endpoint_kwargs, **context)
    else:
        if validate_on_submit(form):
            new_db_obj = model(**additional_model_fields, **form.data_without_submit)
            _datastore.add(new_db_obj)
            if _navigate.flash_messages:
                flash("{name} added successfully!".format(name=name), 'success')
            if edit_uses_id:
                return redirect(url_for(edit_endpoint, id=new_db_obj.id, **edit_endpoint_kwargs))
            else:
                return redirect(url_for(edit_endpoint, **edit_endpoint_kwargs))
        if _navigate.flash_messages:
            flash("{name} form has errors.".format(name=name), 'error')
        rendered_form = render_form_template(form)
        return render(template, form=rendered_form, back_endpoint=back_endpoint,
                      back_endpoint_kwargs=back_endpoint_kwargs, **context)


def edit_view_function(template=Template(""), name="", form=None, model=None, success_endpoint=None, back_endpoint=None,
                       back_endpoint_kwargs={}, context={}, success_endpoint_kwargs={}):
    if is_get():
        populate_form(form, model)
        rendered_form = render_form_template(form)
        return render(template, form=rendered_form, back_endpoint=back_endpoint,
                      back_endpoint_kwargs=back_endpoint_kwargs, **context)
    else:
        if validate_on_submit(form):
            update_object(form, model)
            if _navigate.flash_messages:
                flash("{name} updated successfully!".format(name=name), 'success')
            return redirect(url_for(success_endpoint, **success_endpoint_kwargs))
        if _navigate.flash_messages:
            flash("{name} form has errors.".format(name=name), 'error')
        rendered_form = render_form_template(form)
        return render(template, form=rendered_form, back_endpoint=back_endpoint,
                      back_endpoint_kwargs=back_endpoint_kwargs, **context)


def delete_view_function(template=Template(""), name="", form=None, model=None, back_endpoint=None,
                         success_endpoint=None, success_endpoint_kwargs={}, back_endpoint_kwargs={}, context={}):
    if is_get():
        if form is not None:
            rendered_form = render_form_template(form)
            return render(template, form=rendered_form, back_endpoint=back_endpoint,
                          back_endpoint_kwargs=back_endpoint_kwargs, **context)
        else:
            return render(template, back_endpoint=back_endpoint,
                          back_endpoint_kwargs=back_endpoint_kwargs, **context)
    else:
        if form is not None:
            if validate_on_submit(form):
                if _navigate.flash_messages:
                    flash("{name} deleted successfully!".format(name=name), 'success')
                _datastore.delete(model)
                return redirect(url_for(success_endpoint, **success_endpoint_kwargs))
            else:
                if _navigate.flash_messages:
                    flash("{name} form has errors.".format(name=name), 'error')

            rendered_form = render_form_template(form)
            return render(template, form=rendered_form, back_endpoint=back_endpoint,
                          back_endpoint_kwargs=back_endpoint_kwargs, **context)
        if _navigate.flash_messages:
            flash("{name} deleted successfully!".format(name=name), 'success')
        _datastore.delete(model)
        return redirect(url_for(success_endpoint, **success_endpoint_kwargs))
