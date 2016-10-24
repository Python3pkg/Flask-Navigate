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
from flask import current_app, url_for
from werkzeug.local import LocalProxy

from .helper import view_context, render, add_view_function, model_exists, \
    edit_view_function, delete_view_function
from .models import NavForm, NavItemForm
from .templates import nav_admin_add_nav_item_template, nav_admin_add_nav_template, nav_admin_delete_template, \
    nav_admin_edit_nav_template, nav_admin_list_template, nav_item_admin_delete_template, \
    nav_admin_edit_nav_item_template, nav_admin_add_sub_nav_item_template

_navigate = LocalProxy(lambda: current_app.extensions['navigate'])

_ds = LocalProxy(lambda: _navigate.datastore)


def admin_list_nav():
    navigation_menus = _ds.get_all_nav()
    context = view_context()
    return render(nav_admin_list_template, navs=navigation_menus, **context)


def admin_add_nav():
    context = view_context()
    return add_view_function(
        nav_admin_add_nav_template, _ds.nav_model.info['label'], NavForm(), _ds.nav_model,
        back_endpoint=context['list_nav_endpoint'], edit_endpoint=context['edit_nav_endpoint'], context=context)


def admin_edit_nav(id=None):
    context = view_context()
    nav_obj = model_exists(_ds.nav_model, model_id=id, not_found_url=url_for(context['list_nav_endpoint']))
    context['nav'] = nav_obj
    return edit_view_function(nav_admin_edit_nav_template, nav_obj.info['label'], NavForm(), nav_obj,
                              back_endpoint=context['list_nav_endpoint'], success_endpoint=context['list_nav_endpoint'],
                              context=context)


def admin_delete_nav(id=None):
    context = view_context()
    nav_obj = model_exists(_ds.nav_model, model_id=id, not_found_url=url_for(context['list_nav_endpoint']))
    context['nav'] = nav_obj
    return delete_view_function(template=nav_admin_delete_template, name=_ds.nav_model.info['label'], model=nav_obj,
                                back_endpoint=context['list_nav_endpoint'],
                                success_endpoint=context['list_nav_endpoint'], context=context)


def admin_add_nav_item(id=None):
    context = view_context()
    nav_obj = model_exists(_ds.nav_model, model_id=id, not_found_url=url_for(context['list_nav_endpoint']))
    context['nav'] = nav_obj
    return add_view_function(nav_admin_add_nav_item_template, _ds.nav_item_model.info['label'], NavItemForm(),
                             _ds.nav_item_model, back_endpoint=context['list_nav_endpoint'],
                             edit_endpoint=context['edit_nav_endpoint'], context=context,
                             additional_model_fields={'nav_id': nav_obj.id}, edit_endpoint_kwargs={'id': nav_obj.id},
                             edit_uses_id=False)


def admin_add_sub_nav_item(id=None):
    context = view_context()
    nav_item_obj = model_exists(_ds.nav_item_model, model_id=id, not_found_url=url_for(context['list_nav_endpoint']))
    context['nav_item'] = nav_item_obj
    return add_view_function(nav_admin_add_sub_nav_item_template, _ds.nav_item_model.info['label'], NavItemForm(),
                             _ds.nav_item_model, back_endpoint=context['list_nav_endpoint'],
                             edit_endpoint=context['edit_nav_item_endpoint'], context=context,
                             additional_model_fields={'nav_id': nav_item_obj.nav_id, 'parent_id': nav_item_obj.id})


def admin_edit_nav_item(id=None):
    context = view_context()
    nav_item_obj = model_exists(_ds.nav_item_model, model_id=id, not_found_url=url_for(context['list_nav_endpoint']))
    context['nav_item'] = nav_item_obj
    return edit_view_function(nav_admin_edit_nav_item_template, nav_item_obj.info['label'], NavItemForm(), nav_item_obj,
                              back_endpoint=context['list_nav_endpoint'], success_endpoint=context['edit_nav_endpoint'],
                              success_endpoint_kwargs={'id': nav_item_obj.nav_id},
                              context=context)


def admin_delete_nav_item(id=None):
    context = view_context()
    nav_item_obj = model_exists(_ds.nav_item_model, model_id=id, not_found_url=url_for(context['list_nav_endpoint']))
    context['nav_item'] = nav_item_obj
    return delete_view_function(template=nav_item_admin_delete_template, name=_ds.nav_item_model.info['label'],
                                model=nav_item_obj, back_endpoint=context['edit_nav_endpoint'],
                                back_endpoint_kwargs={'id': nav_item_obj.nav_id},
                                success_endpoint=context['edit_nav_endpoint'],
                                success_endpoint_kwargs={'id': nav_item_obj.nav_id}, context=context)
