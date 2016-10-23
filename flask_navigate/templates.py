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
"""
from jinja2 import Template


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
        <a href="{{ url_for(list_nav_endpoint) }}">Back</a>
    </div>
</div>
""")

nav_admin_edit_nav_template = Template("""
{% macro render_admin_nav_item(nav_item) %}
    <div>
    <a href="{{ url_for(edit_nav_item_endpoint, nav_item_id=nav_item.id) }}">{{ nav_item.text }}</a> - <a href="{{ url_for(delete_nav_item_endpoint, nav_item_id=nav_item.id) }}">Delete</a>

    {% for child in nav_item.children() %}
        <div style="margin-left: 5px;">{{ render_admin_nav_item(child) }}</div>
    {% endfor %}
    </div>
{% endmacro %}
<div>
    <div class="flex_container">
        <div class="flex_container_item">
            <h4>Edit Navigation Menu</h4>
        {{ form }}
        </div>
        <div class="flex_container_item">
            <h4>Edit Navigation Menu Items</h4>
            {% for nav_item in nav.top_level_items() %}
                {{ render_admin_nav_item(nav_item) }}
            {% endfor %}
            <br>
            <a href="{{ url_for(add_nav_item_endpoint, nav_id=nav.id) }}">Create Nav Item</a>
        </div>
    </div>
    <br>
    <a href="{{ url_for(list_nav_endpoint) }}">Back</a>
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
                    <a href="{{ url_for(list_nav_endpoint) }}">Back</a>
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

nav_item_admin_delete_template = Template("""
<div>
    <div>
        <h4>Delete Navigation Menu Item</h4>
    {% if nav_in_use %}
        Cannot delete navigation menu while it is in use!<br>
    {% else %}
        Are you sure you want to delete: {{ nav_item.text }} ?<br>
        <br>
        *** WARNING ***<br>
        It will be permanently deleted!<br>
        <form method="post">
            <div>
                <div>
                    <a href="{{ url_for(list_nav_endpoint) }}">Back</a>
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

nav_admin_add_nav_item_template = Template("""
<div>
    <div>
        <h4>Add Navigation Menu Item</h4>
        {{ form }}
        <a href="{{ url_for(edit_nav_endpoint, nav_id=nav.id) }}">Back</a>
    </div>
</div>
""")

nav_admin_edit_nav_item_template = Template("""
{% macro render_admin_nav_item(nav_item) %}
    <div>
    <a href="{{ url_for(edit_nav_item_endpoint, nav_item_id=nav_item.id) }}">{{ nav_item.text }}</a> - <a href="{{ url_for(delete_nav_item_endpoint, nav_item_id=nav_item.id) }}">Delete</a>

    {% for child in nav_item.children() %}
        <div style="margin-left: 5px;">{{ render_admin_nav_item(child) }}</div>
    {% endfor %}
    </div>
{% endmacro %}
<div>
    <div class="flex_container">
        <div class="flex_container_item">
            <h4>Edit Navigation Item Menu</h4>
        {{ form }}
        </div>
        <div class="flex_container_item">
            <h4>Edit Navigation Menu Sub Items</h4>
            {% for nav_item_child in nav_item.children() %}
                {{ render_admin_nav_item(nav_item_child) }}
            {% endfor %}
            <br>
            <a href="{{ url_for(add_nav_item_endpoint, nav_id=nav_item.nav_id) }}">Create Nav Item</a>
        </div>
    </div>
    <br>
    <a href="{{ url_for(edit_nav_endpoint, nav_id=nav_item.nav_id) }}">Back</a>
</div>
""")
