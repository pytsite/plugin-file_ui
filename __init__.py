"""PytSite File UI Plugin
"""
__author__ = 'Alexander Shepetko'
__email__ = 'a@shepetko.com'
__license__ = 'MIT'

from pytsite import plugman as _plugman

if _plugman.is_installed(__name__):
    # Public API
    from . import _widget as widget


def plugin_load():
    from pytsite import tpl, lang
    from plugins import assetman, http_api
    from . import _http_api_controllers

    lang.register_package(__name__)
    tpl.register_package(__name__)

    assetman.register_package(__name__)
    assetman.t_less(__name__)
    assetman.t_js(__name__)
    assetman.js_module('file_ui-widget-files-upload', __name__ + '@js/widget-files-upload')

    http_api.handle('POST', 'file', _http_api_controllers.Post, 'file_ui@post')
    http_api.handle('GET', 'file/<uid>', _http_api_controllers.Get, 'file_ui@get')
