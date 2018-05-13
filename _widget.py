"""PytSite File UI Plugin Widgets
"""
__author__ = 'Alexander Shepetko'
__email__ = 'a@shepetko.com'
__license__ = 'MIT'

from typing import List as _List, Union as _Union
from pytsite import tpl as _tpl, html as _html, router as _router
from plugins import file as _file, widget as _widget, http_api as _http_api


class FilesUpload(_widget.Abstract):
    """Files Upload Widget
    """

    def __init__(self, uid: str, **kwargs):
        """Init.
        """
        self._model = kwargs.get('model')
        if not self._model:
            raise ValueError('Model is not specified.')

        self._max_files = int(kwargs.get('max_files', 1))
        if self._max_files < 1:
            self._max_files = 1

        self._max_file_size = int(kwargs.get('max_file_size', 2))
        self._accept_files = kwargs.get('accept_files', '*/*')
        self._add_btn_label = kwargs.get('add_btn_label', '')
        self._add_btn_icon = kwargs.get('add_btn_icon', 'fa fa-fw fa-plus')
        self._slot_css = kwargs.get('slot_css', 'col-xs-B-12 col-xs-6 col-md-3 col-lg-2')
        self._show_numbers = False if self._max_files == 1 else kwargs.get('show_numbers', True)
        self._dnd = False if self._max_files == 1 else kwargs.get('dnd', True)
        self._skip_missing = kwargs.get('skip_missing', False)

        super().__init__(uid, **kwargs)

        self._js_modules.append('file_ui-widget-files-upload')
        self._css = ' '.join((self._css, 'widget-files-upload'))

        self._data.update({
            'url': _http_api.url('file_ui@post'),
            'max_files': self._max_files,
            'max_file_size': self._max_file_size,
            'accept_files': self._accept_files,
            'slot_css': self._slot_css,
            'show_numbers': self._show_numbers,
            'dnd': self._dnd,
        })

    @property
    def accept_files(self) -> str:
        return self._accept_files

    @accept_files.setter
    def accept_files(self, value: str):
        self._accept_files = value

    @property
    def add_btn_label(self) -> str:
        return self._add_btn_label

    @add_btn_label.setter
    def add_btn_label(self, value: str):
        self._add_btn_label = value

    @property
    def add_btn_icon(self) -> str:
        return self._add_btn_icon

    @add_btn_icon.setter
    def add_btn_icon(self, value: str):
        self._add_btn_icon = value

    @property
    def max_files(self) -> int:
        return self._max_files

    @max_files.setter
    def max_files(self, value: int):
        self._max_files = value

    @property
    def max_file_size(self) -> int:
        return self._max_file_size

    @max_file_size.setter
    def max_file_size(self, value: int):
        self._max_file_size = value

    @property
    def slot_css(self) -> str:
        return self._slot_css

    @slot_css.setter
    def slot_css(self, value: str):
        self._slot_css = value

    @property
    def show_numbers(self) -> bool:
        return self._show_numbers

    @show_numbers.setter
    def show_numbers(self, value: bool):
        self._show_numbers = value

    @property
    def dnd(self) -> bool:
        return self._dnd

    @dnd.setter
    def dnd(self, value: bool):
        self._dnd = value

    def _get_element(self, **kwargs) -> _html.Element:
        return _html.TagLessElement(_tpl.render('file_ui@file_upload_widget', {'widget': self}))

    def set_val(self, value: _Union[list, tuple]):
        """Set value of the widget
        """
        if value is None:
            return

        # Always process value as multiple files
        if not isinstance(value, (list, tuple)):
            value = [value]

        # Filter out empty values, sanitize valid values
        clean_val = []
        for val in value:
            # Empty value
            if not val:
                continue
            # Files object convert to string UIDs
            elif isinstance(val, _file.model.AbstractFile):
                clean_val.append(val.uid)
            # Strings remain as is
            elif isinstance(val, str):
                try:
                    _file.get(val)  # Check if the file exists
                    clean_val.append(val)
                except _file.error.FileNotFound as e:
                    if not self._skip_missing:
                        raise e
            else:
                raise TypeError("String or file object expected, got '{}'".format(type(val)))

        # Sanitize storage type
        if self._max_files == 1:
            clean_val = clean_val[0] if clean_val else None

        super().set_val(clean_val)

    def form_submit(self, form_uid: str):
        """Hook
        """
        # Delete files which are has been removed from the widget on the browser's side,
        # ONLY if the form is not in validation mode
        to_delete = _router.request().inp.get(self._uid + '_to_delete')
        if to_delete:
            if isinstance(to_delete, str):
                to_delete = [to_delete]
            for uid in to_delete:
                try:
                    _file.get(uid).delete()
                except _file.error.FileNotFound:
                    pass

    def get_files(self) -> _List[_file.model.AbstractFile]:
        """Get value of the widget as a list of file objects
        """
        value = self.get_val()

        if not isinstance(value, (list, tuple)):
            value = [value] if value else []

        return [_file.get(fid) for fid in value]


class ImagesUpload(FilesUpload):
    """Images Upload Widget
    """

    def __init__(self, uid: str, **kwargs):
        super().__init__(uid, model='image', accept_files='image/*', **kwargs)
        self._add_btn_icon = 'fa fa-fw fa-camera'
