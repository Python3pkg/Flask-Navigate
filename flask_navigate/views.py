from flask_bs import render_content_with_bootstrap
from flask import current_app, redirect, request, url_for, flash
from werkzeug.local import LocalProxy
from flask_wtf_flexwidgets import render_form_template, css_template
from jinja2 import Template
from ._compat import iteritems
from .models import Nav, NavForm

_navigate = LocalProxy(lambda: current_app.extensions['navigate'])

_datastore = LocalProxy(lambda: _navigate.datastore)


def dot(a, b):
    return "{}.{}".format(a, b)


def admin_list_nav():
    navigation_menus = _datastore.get_all_nav()
    return render_content_with_bootstrap(body=nav_admin_list_template.
                                         render(navs=navigation_menus,
                                                add_nav_endpoint=dot(_navigate.blueprint_name,
                                                                     _navigate.admin_add_nav_endpoint),
                                                edit_nav_endpoint=dot(_navigate.blueprint_name,
                                                                      _navigate.admin_edit_nav_endpoint),
                                                delete_nav_endpoint=dot(_navigate.blueprint_name,
                                                                        _navigate.admin_delete_nav_endpoint),
                                                url_for=url_for),
                                         head="<style>" + css_template + "</style>")


def admin_add_nav():
    form = NavForm()
    if request.method == 'GET':
        rendered_form = render_form_template(form)
        return render_content_with_bootstrap(body=nav_admin_add_nav_template.render(
                                                    form=rendered_form,
                                                    nav_list_endpoint=dot(
                                                        _navigate.blueprint_name,
                                                        _navigate.admin_list_nav_endpoint
                                                    ),
                                                    url_for=url_for),
                                             head="<style>" + css_template + "</style>")
    else:
        form.process(formdata=request.form)
        if form.validate():
            nav = _datastore.create_nav(**form.data_without_submit)
            return redirect(url_for(_navigate.blueprint_name + '.admin_list_nav'))
        rendered_form = render_form_template(form)
        return render_content_with_bootstrap(body=nav_admin_add_nav_template.render(
                                                    form=rendered_form,
                                                    nav_list_endpoint=dot(
                                                        _navigate.blueprint_name,
                                                        _navigate.admin_list_nav_endpoint
                                                    ),
                                                    url_for=url_for),
                                             head="<style>" + css_template + "</style>")


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


def admin_edit_nav(nav_id=None):
    nav_obj = _datastore.get_nav(nav_id)
    if nav_obj:
        form = NavForm()
        populate_form(form, nav_obj)
        if request.method == 'GET':
            rendered_form = render_form_template(form)
            return render_content_with_bootstrap(body=nav_admin_edit_nav_template.render(
                                                    form=rendered_form,
                                                    nav_list_endpoint=dot(
                                                        _navigate.blueprint_name,
                                                        _navigate.admin_list_nav_endpoint
                                                     ),
                                                    url_for=url_for),
                                                 head="<style>" + css_template + "</style>")
        else:
            form.process(formdata=request.form)
            if form.validate():
                flash("Nav menu updated", "success")
                update_object(form, nav_obj)
                return redirect(url_for(_navigate.blueprint_name + '.admin_list_nav'))
            rendered_form = render_form_template(form)
            return render_content_with_bootstrap(body=nav_admin_edit_nav_template.render(
                                                    form=rendered_form,
                                                    nav_list_endpoint=dot(
                                                        _navigate.blueprint_name,
                                                        _navigate.admin_list_nav_endpoint
                                                     ),
                                                    url_for=url_for),
                                                 head="<style>" + css_template + "</style>")

    flash("Nav menu not found", "error")
    return redirect(url_for(dot(_navigate.blueprint_name, _navigate.admin_list_nav_endpoint)))


def admin_delete_nav(nav_id=None):
    nav_obj = _datastore.get_nav(nav_id)
    if nav_obj:
        if request.method == 'GET':
            return render_content_with_bootstrap(body=nav_admin_delete_template.render(
                                                        nav_list_endpoint=dot(
                                                            _navigate.blueprint_name,
                                                            _navigate.admin_list_nav_endpoint
                                                         ),
                                                        url_for=url_for,
                                                        nav=nav_obj),
                                                 head="<style>" + css_template + "</style>")
        else:
            flash('Navigation menu deleted', 'success')
            _datastore.delete(nav_obj)
            return redirect(url_for(dot(_navigate.blueprint_name, _navigate.admin_list_nav_endpoint)))
    flash('Navigation menu not found!', 'error')
    return redirect(url_for(dot(_navigate.blueprint_name, _navigate.admin_list_nav_endpoint)))


def admin_add_nav_item():
    pass


def admin_edit_nav_item():
    pass


def admin_delete_nav_item():
    pass


nav_admin_list_template = Template("""
<div>
    <div>
        <h4>Navigation Menus</h4>
    {%- for nav in navs -%}
        <div><a href="{{ url_for(edit_nav_endpoint, nav_id=nav.id) }}">{{ nav.name }}</a> -=- <a href="{{ url_for(delete_nav_endpoint, nav_id=nav.id) }}">Delete</a></div>
    {% else %}
        <div>No menus created yet.</div>
    {%- endfor -%}
        <a href="{{ url_for(add_nav_endpoint) }}">Create Navigation Menu</a>
    </div>
</div>
""")


nav_admin_add_nav_template = Template("""
<div>
    <div>
        <h4>Add Navigation Menu</h4>
        {{ form }}
        <a href="{{ url_for(nav_list_endpoint) }}">Back</a>
    </div>
</div>
""")

nav_admin_edit_nav_template = Template("""
<div>
    <div>
        <h4>Edit Navigation Menu</h4>
        {{ form }}
        <a href="{{ url_for(nav_list_endpoint) }}">Back</a>
    </div>
</div>
""")

nav_admin_delete_template = Template("""
<div>
    <div>
        <h4>Delete Navigation Menu</h4>
    {% if nav_in_use %}
        Cannot delete navigation menu while it is in use!<br>
    {% else %}
        Are you sure you want to delete: {{ nav.name }} ?<br>
        <br>
        *** WARNING ***<br>
        It will be permanently deleted!<br>
        <form method="post">
            <div>
                <div>
                    <a href="#">
                </div>
                <div>
                    <input type="submit" value="Delete">
                </div>
            </div>
            <a href="{{ url_for(nav_list_endpoint) }}">Back</a>
        </form>
    {% endif %}
    </div>
</div>
""")
