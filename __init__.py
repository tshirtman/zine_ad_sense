# -*- coding: utf-8 -*-
"""
    zine.plugins.ad_sense
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2011 by gabriel pettier
    :license: GPL, see LICENSE for more details.
"""
from os.path import dirname, join
from random import choice

from zine.api import *
from zine.views.admin import render_admin_response
from zine.utils.admin import flash
from zine.utils.http import redirect
from zine.utils.forms import TextField
from zine.config import ConfigurationTransactionError
from zine.privileges import BLOG_ADMIN

TEMPLATES = join(dirname(__file__), 'templates')

def add_ad_sense_link(req, navigation_bar):
    if not req.user.has_privilege(BLOG_ADMIN):
        return
    for link_id, url, title, children in navigation_bar:
        if link_id == 'options':
            children.insert(-3, ('ad sense', url_for('ad_sense/config'),
                                 _('Ad sense')))


@require_privilege(BLOG_ADMIN)
def view_ad_sense_config(req):
    client_code = req.args.get('client_code')
    banner_slot = req.args.get('banner_slot')
    width = req.args.get('width')
    height = req.args.get('height')
    if client_code and banner_slot and width and height:
        try:
            req.app.cfg.change_single('ad_sense/client_code', client_code)
            req.app.cfg.change_single('ad_sense/banner_slot', banner_slot)
            req.app.cfg.change_single('ad_sense/width', width)
            req.app.cfg.change_single('ad_sense/height', height)
            flash(_('Config updated!'), 'info')
        except ConfigurationTransactionError, e:
            flash(_('The code could not be changed.'), 'error')
        return redirect(url_for('ad_sense/config'))

    return render_admin_response('admin/ad_sense.html',
            'config.ad_sense',
            client_code=req.app.cfg['ad_sense/client_code'],
            banner_slot=req.app.cfg['ad_sense/banner_slot'],
            width=req.app.cfg['ad_sense/width'],
            height=req.app.cfg['ad_sense/height']
            )


def add_adsense_banner(post):
    conf = get_application().cfg
    client_code = conf['ad_sense/client_code']
    banner_slot =  conf['ad_sense/banner_slot']
    banner_width = conf['ad_sense/width']
    banner_height = conf['ad_sense/height']
    if choice((True, False)):
        return '''
            <span class="ad">
            <script type="text/javascript"><!--
            google_ad_client = "'''+client_code+'''";
            google_ad_slot = "'''+banner_slot+'''";
            google_ad_width = '''+banner_width+''';
            google_ad_height = '''+banner_height+''';
            //-->
            </script>
            <script type="text/javascript"
            src="http://pagead2.googlesyndication.com/pagead/show_ads.js">
            </script>
            </span>
        '''
    else:
        return ''


def setup(app, plugin):
    """This function is called by Zine in the application initialization
    phase. Here we connect to the events and register our template paths,
    url rules, views etc.
    """
    app.connect_event('after-entry-rendered', add_adsense_banner)

    # our fish has a configurable skin. So we register one for it which
    # defaults to blue.
    app.add_config_var('ad_sense/client_code', TextField(default=''))
    app.add_config_var('ad_sense/banner_slot', TextField(default=''))
    app.add_config_var('ad_sense/width', TextField(default=''))
    app.add_config_var('ad_sense/height', TextField(default=''))

    app.connect_event('modify-admin-navigation-bar', add_ad_sense_link)

    # for the admin panel we add a url rule. Because it's an admin panel
    # page located in options we add such an url rule.
    app.add_url_rule('/options/ad_sense', prefix='admin',
                     endpoint='ad_sense/config',
                     view=view_ad_sense_config)

    # add our templates to the searchpath so that Zine can find the
    # admin panel template for the fish config panel.
    app.add_template_searchpath(TEMPLATES)
