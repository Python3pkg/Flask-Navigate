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
from wtforms_alchemy import ModelForm
from wtforms import SubmitField
from flask import current_app
from flask_wtf_flexwidgets import FlexStringWidget, FlexBoolWidget, FlexSubmitWidget

try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict

from werkzeug.local import LocalProxy
from ._compat import PY2, text_type, itervalues, iteritems
from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Text, MetaData
from sqlalchemy.orm import relationship

_navigate = LocalProxy(lambda: current_app.extensions['navigate'])

_datastore = LocalProxy(lambda: _navigate.datastore)


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


nav_metadata = MetaData()
Base = declarative_base(metadata=nav_metadata)


class Nav(Base):
    __tablename__ = 'fnav_nav'
    id = Column(Integer(), primary_key=True)
    name = Column(String(256), info={
                            'label': "Name",
                            'widget': FlexStringWidget(),
                        },
                  nullable=False
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


class OrderedModelForm(ModelForm):
    def __iter__(self):
        field_order = getattr(self, 'field_order', None)
        if field_order:
            temp_fields = OrderedDict()
            for name in field_order:
                if name == '*':
                    for key, f in iteritems(self._fields):
                        print(f.type)
                        if key not in field_order:
                            temp_fields[key] = f
                else:
                    temp_fields[name] = self._fields[name]
            self._fields = temp_fields
        return iter(itervalues(self._fields))


class NavForm(OrderedModelForm):
    class Meta:
        model = Nav
    field_order = ('name', 'active', 'hidden', 'vertical', 'custom_tag_id', 'custom_tag_attributes', 'css_classes',
                   'image_url', 'repeat_image', '*')
    submit = SubmitField('Save', widget=FlexSubmitWidget())

    @property
    def data_without_submit(self):
        return dict((name, f.data) for name, f in iteritems(self._fields) if not f.type == 'SubmitField')


class NavItem(Base):
    __tablename__ = 'fnav_nav_item'
    id = Column(Integer(), primary_key=True)
    image_url = Column(String(256), info={
                            'label': "Image URL",
                            'widget': FlexStringWidget(),
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


class NavItemForm(OrderedModelForm):
    class Meta:
        model = NavItem

    field_order = ('text', 'active', 'new_banner', 'drop_down', 'custom_tag_id', 'custom_tag_attributes', 'css_classes',
                   'image_url', 'repeat_image', 'target_url', 'javascript_onclick', 'endpoint', '*')
    submit = SubmitField('Save')

    @property
    def data_without_submit(self):
        return dict((name, f.data) for name, f in iteritems(self._fields) if not f.type == 'SubmitField')
