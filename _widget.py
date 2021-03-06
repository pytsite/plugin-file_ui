"""PytSite File UI Plugin Widgets
"""
__author__ = 'Oleksandr Shepetko'
__email__ = 'a@shepetko.com'
__license__ = 'MIT'

import htmler
from typing import List, Union
from pytsite import tpl, http
from plugins import file, widget, http_api


class FilesUpload(widget.Abstract):
    """Files Upload Widget
    """

    def __init__(self, uid: str, **kwargs):
        """Init.
        """
        self._max_files = int(kwargs.get('max_files', 1))
        if self._max_files < 1:
            self._max_files = 1

        self._max_file_size = int(kwargs.get('max_file_size', 2))
        self._accept_files = kwargs.get('accept_files', '*/*')
        self._add_btn_label = kwargs.get('add_btn_label', '')
        self._add_btn_icon = kwargs.get('add_btn_icon', 'fa fa-fw fa-plus')
        self._slot_css = kwargs.get('slot_css', '')
        self._show_numbers = False if self._max_files == 1 else kwargs.get('show_numbers', True)
        self._dnd = False if self._max_files == 1 else kwargs.get('dnd', True)
        self._skip_missing = kwargs.get('skip_missing', False)
        self._layout = kwargs.get('layout', 'thumbs')
        self._thumb_width = kwargs.get('thumb_width', 500 if self._layout == 'thumbs' else 50)
        self._thumb_height = kwargs.get('thumb_height', 500 if self._layout == 'thumbs' else 50)
        self._preview_images = kwargs.get('preview_images', False)

        super().__init__(uid, **kwargs)

        self._css += ' widget-files-upload'

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

    @property
    def thumb_width(self) -> int:
        return self._thumb_width

    @thumb_width.setter
    def thumb_width(self, value: int):
        self._thumb_width = value

    @property
    def thumb_height(self) -> int:
        return self._thumb_height

    @thumb_height.setter
    def thumb_height(self, value: int):
        self._thumb_height = value

    @property
    def preview_images(self) -> bool:
        return self._preview_images

    @preview_images.setter
    def preview_images(self, value: bool):
        self._preview_images = value

    @property
    def layout(self) -> str:
        return self._layout

    @layout.setter
    def layout(self, value: str):
        self._layout = value

    def _get_element(self, **kwargs) -> htmler.Element:
        self._css += ' layout-{}'.format(self._layout)

        self._data.update({
            'url': http_api.url('file_ui@post'),
            'max_files': self._max_files,
            'max_file_size': self._max_file_size,
            'accept_files': self._accept_files,
            'slot_css': self._slot_css,
            'show_numbers': self._show_numbers,
            'dnd': self._dnd,
            'preview_images': self._preview_images,
            'thumb_width': self._thumb_width,
            'thumb_height': self._thumb_height,
        })

        return htmler.TagLessElement(tpl.render('file_ui@file_upload_widget', {'widget': self}))

    def set_val(self, value: Union[list, tuple]):
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
            elif isinstance(val, file.model.AbstractFile):
                clean_val.append(val.uid)
            # Strings remain as is
            elif isinstance(val, str):
                try:
                    file.get(val)  # Check if the file exists
                    clean_val.append(val)
                except file.error.FileNotFound as e:
                    if not self._skip_missing:
                        raise e
            else:
                raise TypeError("String or file object expected, got '{}'".format(type(val)))

        # Sanitize storage type
        if self._max_files == 1:
            clean_val = clean_val[0] if clean_val else None

        super().set_val(clean_val)

    def _on_form_submit(self, request: http.Request):
        """Hook
        """
        # Delete files which are has been removed from the widget on the browser's side,
        # ONLY if the form is not in validation mode
        to_delete = request.inp.get(self._uid + '_to_delete')
        if to_delete:
            if isinstance(to_delete, str):
                to_delete = [to_delete]
            for uid in to_delete:
                try:
                    file.get(uid).delete()
                except file.error.FileNotFound:
                    pass

    def get_files(self) -> List[file.model.AbstractFile]:
        """Get value of the widget as a list of file objects
        """
        value = self.get_val()

        if not isinstance(value, (list, tuple)):
            value = [value] if value else []

        return [file.get(fid) for fid in value]


class ImagesUpload(FilesUpload):
    """Images Upload Widget
    """

    def __init__(self, uid: str, **kwargs):
        kwargs.setdefault('add_btn_icon', 'fa fa-fw fa-camera')
        kwargs.setdefault('preview_images', True)

        super().__init__(uid, accept_files='image/*', **kwargs)
