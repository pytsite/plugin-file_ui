"""PytSite File UI Plugin
"""
__author__ = 'Oleksandr Shepetko'
__email__ = 'a@shepetko.com'
__license__ = 'MIT'

# Public API
from . import _widget as widget


def plugin_load_wsgi():
    from plugins import http_api
    from . import _http_api_controllers

    http_api.handle('POST', 'file', _http_api_controllers.Post, 'file_ui@post')
    http_api.handle('GET', 'file/<uid>', _http_api_controllers.Get, 'file_ui@get')
