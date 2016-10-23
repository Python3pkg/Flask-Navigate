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
from flask_bs import render_content_with_bootstrap
from flask import current_app, redirect, request, url_for, flash
from werkzeug.local import LocalProxy
from flask_wtf_flexwidgets import render_form_template, css_template
from .models import NavForm, NavItemForm
from .helper import view_context, populate_form, update_object
from .templates import nav_admin_add_nav_item_template, nav_admin_add_nav_template, nav_admin_delete_template, \
    nav_admin_edit_nav_template, nav_admin_list_template, nav_item_admin_delete_template, \
    nav_admin_edit_nav_item_template, nav_admin_add_sub_nav_item_template
_navigate = LocalProxy(lambda: current_app.extensions['navigate'])

_datastore = LocalProxy(lambda: _navigate.datastore)


def admin_list_nav():
    navigation_menus = _datastore.get_all_nav()
    context = view_context()
    return render_content_with_bootstrap(body=nav_admin_list_template.render(navs=navigation_menus, **context),
                                         head="<style>" + css_template + "</style>")


def admin_add_nav():
    form = NavForm()
    context = view_context()
    if request.method == 'GET':
        rendered_form = render_form_template(form)
        return render_content_with_bootstrap(body=nav_admin_add_nav_template.render(form=rendered_form, **context),
                                             head="<style>" + css_template + "</style>")
    else:
        form.process(formdata=request.form)
        if form.validate():
            nav = _datastore.create_nav(**form.data_without_submit)
            return redirect(url_for(context['edit_nav_endpoint'], nav_id=nav.id))
        rendered_form = render_form_template(form)
        return render_content_with_bootstrap(body=nav_admin_add_nav_template.render(form=rendered_form, **context),
                                             head="<style>" + css_template + "</style>")


def admin_edit_nav(nav_id=None):
    nav_obj = _datastore.get_nav(nav_id)
    context = view_context()
    if nav_obj:
        form = NavForm()
        populate_form(form, nav_obj)
        if request.method == 'GET':
            rendered_form = render_form_template(form)
            return render_content_with_bootstrap(body=nav_admin_edit_nav_template.render(form=rendered_form,
                                                                                         nav=nav_obj, **context),
                                                 head="<style>" + css_template + "</style>")
        else:
            form.process(formdata=request.form)
            if form.validate():
                flash("Nav menu updated", "success")
                update_object(form, nav_obj)
                return redirect(url_for(context['list_nav_endpoint']))
            rendered_form = render_form_template(form)
            return render_content_with_bootstrap(body=nav_admin_edit_nav_template.render(form=rendered_form,
                                                                                         nav=nav_obj, **context),
                                                 head="<style>" + css_template + "</style>")

    flash("Nav menu not found", "error")
    return redirect(url_for(context['list_nav_endpoint']))


def admin_delete_nav(nav_id=None):
    nav_obj = _datastore.get_nav(nav_id)
    context = view_context()
    if nav_obj:
        if request.method == 'GET':
            return render_content_with_bootstrap(body=nav_admin_delete_template.render(nav=nav_obj, **context),
                                                 head="<style>" + css_template + "</style>")
        else:
            flash('Navigation menu deleted', 'success')
            _datastore.delete(nav_obj)
        return redirect(url_for(context['list_nav_endpoint']))
    flash('Navigation menu not found!', 'error')
    return redirect(url_for(context['list_nav_endpoint']))


def admin_add_nav_item(nav_id=None):
    nav_obj = _datastore.get_nav(nav_id)
    context = view_context()
    if nav_obj:
        form = NavItemForm()
        if request.method == 'GET':
            rendered_form = render_form_template(form)
            return render_content_with_bootstrap(body=nav_admin_add_nav_item_template.render(
                                                        form=rendered_form, nav=nav_obj, **context),
                                                 head="<style>" + css_template + "</style>")
        else:
            form.process(formdata=request.form)
            if form.validate():
                flash("Navigation Menu Item Added", 'success')
                _datastore.create_nav_item(nav_id=nav_obj.id, **form.data_without_submit)
                return redirect(url_for(context['edit_nav_endpoint'],
                                        nav_id=nav_obj.id))
            else:
                rendered_form = render_form_template(form)
                return render_content_with_bootstrap(body=nav_admin_add_nav_item_template.render(
                                                            form=rendered_form, nav=nav_obj, **context),
                                                     head="<style>" + css_template + "</style>")
    flash('Navigation Item Not Found!', 'error')
    return redirect(url_for(context['list_nav_endpoint']))


def admin_add_sub_nav_item(nav_item_id=None):
    nav_item_obj = _datastore.get_nav_item(nav_item_id)
    context = view_context()
    if nav_item_obj:
        form = NavItemForm()
        if request.method == 'GET':
            rendered_form = render_form_template(form)
            return render_content_with_bootstrap(body=nav_admin_add_sub_nav_item_template.render(
                                                        form=rendered_form, nav=nav_item_obj.nav, nav_item=nav_item_obj,
                                                        **context),
                                                 head="<style>" + css_template + "</style>")
        else:
            form.process(formdata=request.form)
            if form.validate():
                flash("Navigation Menu Item Added", 'success')
                _datastore.create_nav_item(nav_id=nav_item_obj.nav_id, parent_id=nav_item_obj.id,
                                           **form.data_without_submit)
                return redirect(url_for(context['edit_nav_endpoint'],
                                        nav_id=nav_item_obj.nav_id))
            else:
                rendered_form = render_form_template(form)
                return render_content_with_bootstrap(body=nav_admin_add_sub_nav_item_template.render(
                                                        form=rendered_form, nav=nav_item_obj.nav, nav_item=nav_item_obj,
                                                        **context),
                                                     head="<style>" + css_template + "</style>")
    flash('Navigation Item Not Found!', 'error')
    return redirect(url_for(context['list_nav_endpoint']))


def admin_edit_nav_item(nav_item_id=None):
    nav_item_obj = _datastore.get_nav_item(nav_item_id)
    context = view_context()
    if nav_item_obj:
        form = NavItemForm()
        populate_form(form, nav_item_obj)
        if request.method == 'GET':
            rendered_form = render_form_template(form)
            return render_content_with_bootstrap(body=nav_admin_edit_nav_item_template.render(
                                                    form=rendered_form, nav_item=nav_item_obj, **context),
                                                 head="<style>" + css_template + "</style>")
        else:
            form.process(formdata=request.form)
            if form.validate():
                flash("Nav menu item updated", "success")
                update_object(form, nav_item_obj)
                return redirect(url_for(context['list_nav_endpoint']))
            rendered_form = render_form_template(form)
            return render_content_with_bootstrap(body=nav_admin_edit_nav_template.render(
                                                    form=rendered_form, nav_item=nav_item_obj, **context),
                                                 head="<style>" + css_template + "</style>")

    flash('Navigation Item Not Found!', 'error')
    return redirect(url_for(context['list_nav_endpoint']))


def admin_delete_nav_item(nav_item_id=None):
    nav_item_obj = _datastore.get_nav_item(nav_item_id)
    context = view_context()
    if nav_item_obj:
        if request.method == 'GET':
            return render_content_with_bootstrap(body=nav_item_admin_delete_template.render(
                                                    nav_item=nav_item_obj, **context),
                                                 head="<style>" + css_template + "</style>")
        else:
            flash('Navigation Menu Item Deleted', 'success')
            nav_id = nav_item_obj.nav_id
            _datastore.delete(nav_item_obj)
            return redirect(url_for(context['edit_nav_endpoint'], nav_id=nav_id))
    flash('Navigation Menu Item Not Found!', 'error')
    return redirect(url_for(context['list_nav_endpoint']))
