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
from flask import Flask
from flask_navigate import Navigate, render_nav
from flask_bs import render_content_with_bootstrap

app = Flask(__name__)
app.config['SECRET_KEY'] = 'super_secret_testing_key'
nav = Navigate(app).init_app(app)


@app.route("/")
def hello():
    return render_content_with_bootstrap(body=render_nav())

if __name__ == "__main__":
    new_nav = nav.datastore.create_nav(name="Main", hidden=False)
    new_nav_item_1 = nav.datastore.create_nav_item(image_url=None, new_banner=False, repeat_image=False, parent_id=None,
                                                   text="Test 1", target_url="/", javascript_onclick=None,
                                                   css_classes="", custom_tag_id=None,
                                                   custom_tag_attributes=None, nav_id=new_nav.id,
                                                   active=True, drop_down=True)
    new_nav_item_2 = nav.datastore.create_nav_item(image_url=None, new_banner=False, repeat_image=False, parent_id=None,
                                                   text="Test 2", target_url='#', javascript_onclick=None,
                                                   css_classes="", custom_tag_id=None,
                                                   custom_tag_attributes=None, nav_id=new_nav.id)
    new_nav_item_1_a = nav.datastore.create_nav_item(image_url=None, new_banner=False, repeat_image=False,
                                                     parent_id=new_nav_item_1.id, text="Test 1 a", target_url=None,
                                                     javascript_onclick=None, css_classes="",
                                                     custom_tag_id=None, custom_tag_attributes=None, nav_id=new_nav.id,
                                                     endpoint="hello")
    app.run(port=5501, debug=False)
