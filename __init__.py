"""PytSite File UI Plugin
"""
__author__ = 'Alexander Shepetko'
__email__ = 'a@shepetko.com'
__license__ = 'MIT'

# Public API
from . import _widget as widget


def plugin_load():
    from pytsite import lang
    from plugins import assetman

    lang.register_package(__name__)

    assetman.register_package(__name__)
    assetman.t_less(__name__)
    assetman.t_js(__name__)
    assetman.js_module('file_ui-widget-files-upload', __name__ + '@js/widget-files-upload')


def plugin_install():
    from plugins import assetman

    assetman.build(__name__)
    assetman.build_translations()


def plugin_load_wsgi():
    from pytsite import tpl
    from plugins import http_api
    from . import _http_api_controllers

    tpl.register_package(__name__)

    http_api.handle('POST', 'file', _http_api_controllers.Post, 'file_ui@post')
    http_api.handle('GET', 'file/<uid>', _http_api_controllers.Get, 'file_ui@get')
