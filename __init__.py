"""PytSite File UI Plugin
"""

# Public API
from . import _widget as widget

__author__ = 'Alexander Shepetko'
__email__ = 'a@shepetko.com'
__license__ = 'MIT'


def _init():
    from pytsite import tpl, lang
    from plugins import assetman, http_api
    from . import _http_api_controllers

    lang.register_package(__name__)
    tpl.register_package(__name__)

    assetman.register_package(__name__)
    assetman.t_less(__name__ + '@**')
    assetman.t_js(__name__ + '@**')
    assetman.js_module('file_ui-widget-files-upload', __name__ + '@js/widget-files-upload')

    http_api.handle('POST', 'file', _http_api_controllers.Post(), 'file_ui@post')
    http_api.handle('GET', 'file/<uid>', _http_api_controllers.Get(), 'file_ui@get')


_init()
