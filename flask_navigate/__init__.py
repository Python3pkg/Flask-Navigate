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
from flask import current_app, Blueprint, render_template, request, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_security import current_user
from werkzeug.local import LocalProxy
from jinja2 import Template
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Text, create_engine, MetaData
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from ._compat import PY2, text_type
from sqlalchemy.engine.reflection import Inspector
from wtforms_alchemy import ModelForm
from flask_wtf_flexwidgets import render_form_template, FlexStringWidget, FlexBoolWidget
from flask_bs import Bootstrap, render_content_with_bootstrap
# Find the stack on which we want to store the database connection.
# Starting with Flask 0.9, the _app_ctx_stack is the correct one,
# before that we need to use the _request_ctx_stack.
try:
    from flask import _app_ctx_stack as stack
except ImportError:
    from flask import _request_ctx_stack as stack

_navigate = LocalProxy(lambda: current_app.extensions['navigate'])

_datastore = LocalProxy(lambda: _navigate.datastore)

_default_config = {
    'DATABASE': 'sqlite',
    'DATABASE_URI': 'sqlite:///nav.db',
    'DATABASE_TABLE_PREFIX': 'fnav',
    'SUBDOMAIN': None,
    'URL_PREFIX': '/nav',
    'BLUEPRINT_NAME': 'nav',
    'RENDER_URL': '/',
    'ADMIN_USES_APP_ROUTES': False,
    'ADMIN_LIST_NAV_URL': '/admin',
    'ADMIN_ADD_NAV_URL': '/admin/nav/add',
    'ADMIN_EDIT_NAV_URL': '/admin/nav/edit',
    'ADMIN_DELETE_NAV_URL': '/admin/nav/delete',
    'ADMIN_LIST_NAV_ITEM_URL': '/admin/nav/item/list',
    'ADMIN_ADD_NAV_ITEM_URL': '/admin/nav/item/add',
    'ADMIN_EDIT_NAV_ITEM_URL': '/admin/nav/item/edit',
    'ADMIN_DELETE_NAV_ITEM_URL': '/admin/nav/item/delete',
}


def get_config(app):
    """Conveniently get the navigate configuration for the specified
    application without the annoying 'NAV_' prefix.
    :param app: The application to inspect
    """
    items = app.config.items()
    prefix = 'NAV_'

    def strip_prefix(tup):
        return tup[0].replace('NAV_', ''), tup[1]

    return dict([strip_prefix(i) for i in items if i[0].startswith(prefix)])


def _get_state(app, datastore, **kwargs):
    for key, value in get_config(app).items():
        kwargs[key.lower()] = value

    kwargs.update(dict(
        app=app,
        datastore=datastore,
    ))

    return _NavigateState(**kwargs)


class _NavigateState(object):

    def __init__(self, **kwargs):
        self.blueprint_name = ""
        self.url_prefix = ""
        self.subdomain = ""
        self.render_url = ""
        self.admin_uses_app_routes = False
        self.admin_list_nav_url = '/admin/'
        self.admin_add_nav_url = '/admin/nav/add'
        self.admin_edit_nav_url = '/admin/nav/edit'
        self.admin_delete_nav_url = '/admin/nav/delete'
        self.admin_list_nav_item_url = '/admin/nav/item/list'
        self.admin_add_nav_item_url = '/admin/nav/item/add'
        self.admin_edit_nav_item_url = '/admin/nav/item/edit'
        self.admin_delete_nav_item_url = '/admin/nav/item/delete'
        for key, value in kwargs.items():
            setattr(self, key.lower(), value)


class Navigate(object):

    def __init__(self, app=None, datastore=None, **kwargs):
        self.app = app
        self.datastore = datastore
        self._engine = None
        self._db = None
        if app is not None and datastore is not None:
            self._state = self.init_app(app, datastore, **kwargs)

    def init_app(self, app, datastore=None, register_blueprint=True):
        datastore = datastore or self.datastore
        if datastore is None:
            self._engine = create_engine('sqlite:///:memory:')
            Session = sessionmaker(bind=self._engine)
            self._db = Session()
            self.datastore = SQLAlchemyNavDataStore(self._db, nav_model=Nav, nav_item_model=NavItem)
            datastore = self.datastore
            Base.metadata.bind = self._engine
        inspector = Inspector.from_engine(self._engine)
        nav_model_created = False
        nav_item_model_created = False
        for table_name in inspector.get_table_names():
            if self.datastore.nav_model.__tablename__ == table_name:
                nav_model_created = True
            if self.datastore.nav_item_model.__tablename__ == table_name:
                nav_item_model_created = True

        if not nav_model_created or not nav_item_model_created:
            Base.metadata.create_all()

        for key, value in _default_config.items():
            app.config.setdefault('NAV_' + key, value)

        if hasattr(app, 'teardown_appcontext'):
            app.teardown_appcontext(self.teardown)
        else:
            app.teardown_request(self.teardown)

        state = _get_state(app, datastore)

        if register_blueprint:
            app.register_blueprint(create_blueprint(state, __name__))
            # app.context_processor(_context_processor)

        state.render_template = self.render_template
        app.extensions['navigate'] = state

        if not app.extensions.get('bootstrap', False):
            b = Bootstrap(app=app)
        return state

    def render_template(self, *args, **kwargs):
        return render_template(*args, **kwargs)

    def __getattr__(self, name):
        return getattr(self._state, name, None)

    def connect(self):
        return SQLAlchemy(self.app)

    def teardown(self, exception):
        ctx = stack.top
        if hasattr(ctx, 'sqlite3_db'):
            ctx.sqlite3_db.close()

    @property
    def connection(self):
        ctx = stack.top
        if ctx is not None:
            if not hasattr(ctx, 'sqlite3_db'):
                ctx.sqlite3_db = self.connect()
            return ctx.sqlite3_db


class Datastore(object):
    def __init__(self, db):
        self.db = db

    def commit(self):
        pass

    def add(self, model):
        raise NotImplementedError

    def delete(self, model):
        raise NotImplementedError

    def create_all(self):
        raise NotImplementedError

    def drop_all(self):
        raise NotImplementedError


class SQLAlchemyDatastore(Datastore):
    def commit(self):
        self.db.commit()

    def add(self, model):
        self.db.add(model)
        self.commit()
        return model

    def delete(self, model):
        self.db.delete(model)

    def create_all(self):
        self.db.create_all()

    def drop_all(self):
        self.db.drop_all()


class NavDatastore(object):
    def __init__(self, nav_model, nav_item_model):
        self.nav_model = nav_model
        self.nav_item_model = nav_item_model

    def _create_nav_defaults(self, **kwargs):
        kwargs.setdefault('active', True)
        kwargs.setdefault('hidden', False)
        kwargs.setdefault('vertical', False)
        kwargs.setdefault('css_classes', 'nav')
        return kwargs

    def _create_nav_item_defaults(self, **kwargs):
        kwargs.setdefault('parent', None)
        kwargs.setdefault('css_classes', 'nav_item')
        return kwargs

    def get_nav(self, id_or_name):
        raise NotImplementedError

    def get_all_nav(self):
        raise NotImplementedError

    def create_nav(self, **kwargs):
        kwargs = self._create_nav_defaults(**kwargs)
        nav = self.nav_model(**kwargs)
        return self.__getattribute__('add')(nav)

    def create_nav_item(self, **kwargs):
        kwargs = self._create_nav_item_defaults(**kwargs)
        nav_item = self.nav_item_model(**kwargs)
        return self.__getattribute__('add')(nav_item)


class SQLAlchemyNavDataStore(SQLAlchemyDatastore, NavDatastore):
    """A SQLAlchemy datastore implementation for Flask-Navigate that assumes the
    use of the Flask-SQLAlchemy extension.
    """
    def __init__(self, db, nav_model, nav_item_model):
        SQLAlchemyDatastore.__init__(self, db)
        NavDatastore.__init__(self, nav_model, nav_item_model)

    def get_nav(self, identifier):
        if type(identifier) == int:
            return self.db.query(self.nav_model).get(identifier)
        elif type(identifier) == str:
            return self.db.query(self.nav_model).filter(self.nav_model.name == identifier).first()
        return None

    def get_all_nav(self):
        return self.db.query(self.nav_model).all()


class NavMixin(object):
    """
    This provides default implementations for the methods that Flask-Nav expect Nav objects to have.
    """

    if not PY2:  # pragma: no cover
        # Python 3 implicitly set __hash__ to None if we override __eq__
        # We set it back to its default implementation
        __hash__ = object.__hash__

    @property
    def is_vertical(self):
        return self.__getattribute__('vertical')

    @property
    def is_active(self):
        return self.__getattribute__('active')

    @property
    def click_action(self):
        return self.__getattribute__('action')

    def get_id(self):
        try:
            return text_type(self.__getattribute__('id'))
        except AttributeError:
            raise NotImplementedError('No `id` attribute - override `get_id`')

    def __eq__(self, other):
        """
        Checks the equality of two `NavMixin` objects using `get_id`.
        """
        if isinstance(other, NavMixin):
            return self.get_id() == other.get_id()
        return NotImplemented

    def __ne__(self, other):
        """
        Checks the inequality of two `NavMixin` objects using `get_id`.
        """
        equal = self.__eq__(other)
        if equal is NotImplemented:
            return NotImplemented
        return not equal


def create_blueprint(state, import_name):
    """Creates the navigate extension blueprint"""

    bp = Blueprint(state.blueprint_name, import_name,
                   url_prefix=state.url_prefix,
                   subdomain=state.subdomain,
                   template_folder='templates')

    if state.admin_uses_app_routes:
        admin_routing = current_app
    else:
        admin_routing = bp

    admin_routing.route(state.admin_list_nav_url,
                        methods=['GET'],
                        endpoint='admin_list_nav')(admin_list_nav)
    admin_routing.route(state.admin_add_nav_url,
                        methods=['GET', 'POST'],
                        endpoint='admin_add_nav')(admin_add_nav)
    admin_routing.route(state.admin_edit_nav_url + slash_url_suffix(state.admin_edit_nav_url, '<nav_id>'),
                        methods=['GET', 'POST'],
                        endpoint='admin_edit_nav')(admin_edit_nav)
    admin_routing.route(state.admin_delete_nav_url + slash_url_suffix(state.admin_delete_nav_url, '<nav_id>'),
                        methods=['GET', 'POST'],
                        endpoint='admin_delete_nav')(admin_delete_nav)
    admin_routing.route(state.admin_add_nav_item_url + slash_url_suffix(state.admin_add_nav_item_url, '<nav_id>'),
                        methods=['GET', 'POST'],
                        endpoint='admin_add_nav_item')(admin_add_nav_item)
    admin_routing.route(state.admin_edit_nav_item_url + slash_url_suffix(state.admin_edit_nav_item_url,
                                                                         '<nav_item_id>'),
                        methods=['GET', 'POST'],
                        endpoint='admin_edit_nav_item')(admin_edit_nav_item)
    admin_routing.route(state.admin_delete_nav_item_url + slash_url_suffix(state.admin_delete_nav_item_url,
                                                                           '<nav_item_id>'),
                        methods=['GET', 'POST'],
                        endpoint='admin_delete_nav_item')(admin_delete_nav_item)
    return bp


def admin_list_nav():
    navigation_menus = _datastore.get_all_nav()
    return nav_admin_list_template.render(navs=navigation_menus, add_nav_endpoint=_navigate.blueprint_name +
                                          '.admin_add_nav', url_for=url_for)


def admin_add_nav():
    form = NavForm()
    if request.method == 'GET':
        form.populate_obj(Nav())
        rendered_form = render_form_template(form)

        return nav_admin_add_nav_template.render(form=rendered_form)
    else:
        if form.validate_on_submit():
            return redirect(url_for('admin_list_nav'))
        else:
            return nav_admin_add_nav_template.render(form=render_form_template(form))


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


def render_nav(nav=1):
    nav_obj = _datastore.get_nav(nav)
    if nav_obj:
        return nav_template.render(nav=nav_obj, request_path=request.path, user=current_user, url_for=url_for)
    return """Nav Menu Not Found"""

nav_metadata = MetaData()
Base = declarative_base(metadata=nav_metadata)


class Nav(Base):
    __tablename__ = 'fnav_nav'
    id = Column(Integer(), primary_key=True)
    name = Column(String(256), info={
                            'label': "Name",
                            'widget': FlexStringWidget(),
                        }
                 )
    active = Column(Boolean(), info={
                            'label': "Active",
                            'widget': FlexBoolWidget(),
                        })
    hidden = Column(Boolean(), info={
                            'label': "Hidden",
                            'widget': FlexBoolWidget(),
                        })
    vertical = Column(Boolean(), info={
                            'label': "Vertical",
                            'widget': FlexBoolWidget(),
                        })
    custom_tag_id = Column(String(256), info={
                            'label': "Custom HTML Tag ID",
                            'widget': FlexStringWidget(),
                        })
    custom_tag_attributes = Column(Text(), info={
                            'label': "Custom HTML Tag Attributes",
                            'widget': FlexStringWidget(),
                        })
    css_classes = Column(String(256), info={
                            'label': "CSS Classes",
                            'widget': FlexStringWidget(),
                        })
    image_url = Column(String(256), info={
                            'label': "Image URL",
                            'widget': FlexStringWidget(),
                        })
    repeat_image = Column(Boolean(), info={
                            'label': "Repeat Image",
                            'widget': FlexBoolWidget(),
                        })

    def top_level_items(self):
        return _datastore.db.query(NavItem).filter(NavItem.nav_id == self.id).filter(NavItem.parent_id == None).all()


class NavForm(ModelForm):
    class Meta:
        model = Nav


class NavItem(Base):
    __tablename__ = 'fnav_nav_item'
    id = Column(Integer(), primary_key=True)
    image_url = Column(String(256), info={
                            'label': "Image URL",
                            'widget': FlexStringWidget,
                        }
                       )
    new_banner = Column(Boolean(), info={
                            'label': "Display New Banner",
                            'widget': FlexBoolWidget(),
                        })
    drop_down = Column(Boolean(), info={
                            'label': "Is Drop Down",
                            'widget': FlexBoolWidget(),
                        })
    active = Column(Boolean(), info={
                            'label': "Active",
                            'widget': FlexBoolWidget(),
                        })
    # Will stretch if False
    repeat_image = Column(Boolean(), info={
                            'label': "Repeat Image",
                            'widget': FlexBoolWidget(),
                        })
    parent_id = Column(Integer(), ForeignKey('fnav_nav_item.id'), default=None)
    parent = relationship('NavItem', foreign_keys='NavItem.parent_id', uselist=False)
    text = Column(String(256), info={
                            'label': "Text",
                            'widget': FlexStringWidget(),
                        })
    target_url = Column(String(256), info={
                            'label': "URL Target",
                            'widget': FlexStringWidget(),
                        })
    javascript_onclick = Column(Text(), info={
                            'label': "Javascript ONCLICK=",
                            'widget': FlexStringWidget(),
                        })
    custom_tag_attributes = Column(Text(), info={
                            'label': "Custom HTML Tag Attributes",
                            'widget': FlexStringWidget(),
                        })
    css_classes = Column(String(256), info={
                            'label': "CSS Classes",
                            'widget': FlexStringWidget(),
                        })
    custom_tag_id = Column(String(256), info={
                            'label': "Custom HTML Tag ID",
                            'widget': FlexStringWidget(),
                        })
    nav_id = Column(Integer(), ForeignKey('fnav_nav.id'))
    nav = relationship('Nav', backref='items')
    endpoint = Column(String(256), info={
                            'label': "url_for Endpoint",
                            'widget': FlexStringWidget(),
                        })

    def children(self):
        return _datastore.db.query(NavItem).filter(NavItem.parent_id == self.id).all()

    def get_classes(self):
        classes = []
        if self.drop_down:
            classes.append('dropdown')
        if self.new_banner:
            classes.append('new_banner')
        if self.active:
            classes.append('active')
        if self.css_classes != "":
            classes.append(self.css_classes)
        return ' '.join(classes)


class NavItemForm(ModelForm):
    class Meta:
        model = NavItem


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


nav_template = Template("""
{% macro render_nav(nav, page, user) %}
    <nav class="navbar navbar-inverse navbar-fixed-top">
        <div class="container">
            <div class="navbar-header">
                <button type="button" class="navbar-toggle collapsed" data-toggle="collapse" data-target="#navbar"
                        aria-expanded="false" aria-controls="navbar">
                    <span class="sr-only">Toggle navigation</span>
                    <span class="icon-bar"></span>
                    <span class="icon-bar"></span>
                    <span class="icon-bar"></span>
                </button>
                <a class="navbar-brand" href="/">{% if nav.brand %}{{ nav.brand }}{% endif %}</a>
            </div>
            <div id="navbar" class="navbar-collapse collapse">
                <ul class="nav navbar-nav">
                    {{ render_nav_items(nav.items, page, user) }}
                </ul>
            </div>
        </div>
    </nav>
{% endmacro %}

{% macro render_nav_item_admin(item) %}
    <a href="{{ url_for('admin.edit_nav_item', nav_item_id=item.id) }}">{{ item.name }}</a>
    <a href="{{ url_for('admin.delete_nav_item', nav_item_id=item.id) }}">Delete</a><br>
    {% if item.children %}
        {% if item.children.all()|count > 0 %}
            <p>
                {% for child in item.children.all() %}
                    {{ render_nav_item_admin(child) }}
                {% endfor %}
            </p>
        {% endif %}
    {% endif %}
{% endmacro %}

{% macro render_nav_items(items, page, user, cycle=0) -%}
    {% for item in items -%}
        {% if cycle == 0 -%}
            {% if item.parent_id == None -%}
                {% if item.authentication -%}
                    {% if user.is_authenticated -%}
                        {% if item.administrator -%}
                            {% if user.administrator -%}
                                {{ render_nav_item(item, page, user, cycle) }}
                            {% endif -%}
                        {% else -%}
                            {{ render_nav_item(item, page, user, cycle) }}
                        {% endif -%}
                    {% endif -%}
                {% else %}
                    {{ render_nav_item(item, page, user, cycle) }}
                {% endif -%}
            {% endif -%}
        {% else -%}
            {% if item.authentication -%}
                {% if user.is_authenticated -%}
                    {% if item.administrator -%}
                        {% if user.administrator -%}
                            {{ render_nav_item(item, page, user, cycle) }}
                        {% endif -%}
                    {% else -%}
                        {{ render_nav_item(item, page, user, cycle) }}
                    {% endif -%}
                {% endif -%}
            {% else -%}
                {{ render_nav_item(item, page, user, cycle) }}
            {% endif -%}
        {% endif -%}
    {% endfor -%}
{% endmacro -%}

{% macro render_nav_item(item, page, user, cycle) -%}
        <li class="{{ item.get_classes() }}">
            <a {% if item.drop_down -%}href="#" class="dropdown-toggle" data-toggle="dropdown" role="button"
                aria-expanded="false"
                {% else -%}
                href="{% if item.target_url != "" and item.target_url != None -%}{{ item.target_url }}{% elif item.endpoint != "" and item.endpoint != None -%}{{ url_for(item.endpoint) }}{% endif -%}"{% endif -%}>
                {{ item.text }}{% if item.drop_down -%}<span class="caret"></span>{% endif -%}</a>
            {% if item.drop_down -%}
                <ul class="dropdown-menu" role="menu">
                    {{ render_nav_items(item.children(), page, user, cycle + 1) }}
                </ul>
            {% else -%}
            {% endif -%}
        </li>
{% endmacro -%}

{{ render_nav(nav, request_path, user) }}""")


def slash_url_suffix(url, suffix):
    """Adds a slash either to the beginning or the end of a suffix
    (which is to be appended to a URL), depending on whether or not
    the URL ends with a slash."""

    return url.endswith('/') and ('%s/' % suffix) or ('/%s' % suffix)