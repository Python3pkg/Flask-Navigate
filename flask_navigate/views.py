from flask_bs import render_content_with_bootstrap
from flask import current_app, redirect, request, url_for
from flask_navigate.models import Nav, NavForm
from werkzeug.local import LocalProxy
from flask_wtf_flexwidgets import render_form_template, css_template
from jinja2 import Template


_navigate = LocalProxy(lambda: current_app.extensions['navigate'])

_datastore = LocalProxy(lambda: _navigate.datastore)


def admin_list_nav():
    navigation_menus = _datastore.get_all_nav()
    return render_content_with_bootstrap(body=nav_admin_list_template.
                                         render(navs=navigation_menus,
                                                add_nav_endpoint=_navigate.blueprint_name + '.admin_add_nav',
                                                url_for=url_for),
                                         head="<style>" + css_template + "</style>")


def admin_add_nav():
    form = NavForm()
    if request.method == 'GET':
        rendered_form = render_form_template(form)
        return render_content_with_bootstrap(body=nav_admin_add_nav_template.render(form=rendered_form),
                                             head="<style>" + css_template + "</style>")
    else:
        form.process(formdata=request.form)
        if form.validate():
            nav = _datastore.create_nav(**form.data_without_submit)
            return redirect(url_for(_navigate.blueprint_name + '.admin_list_nav'))
        else:
            rendered_form = render_form_template(form)
        return render_content_with_bootstrap(body=nav_admin_add_nav_template.render(form=rendered_form),
                                             head="<style>" + css_template + "</style>")


def admin_edit_nav():
    pass


def admin_delete_nav():
    pass


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
        <div><a href="#">{{ nav.name }}</a> -=- <a href="#">Delete</a></div>
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
        </form>
    {% endif %}
    </div>
</div>
""")
