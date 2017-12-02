"""PytSite File HTTP API Endpoints
"""
from typing import List as _List
from os import unlink as _unlink
from pytsite import util as _util, routing as _routing
from plugins import file as _file, auth as _auth

__author__ = 'Alexander Shepetko'
__email__ = 'a@shepetko.com'
__license__ = 'MIT'


class Post(_routing.Controller):
    """Upload a file
    """

    def exec(self) -> _List[str]:
        if _auth.get_current_user().is_anonymous:
            raise self.forbidden()

        if not self.request.files:
            raise RuntimeError('No files received')

        r = []
        for field_name, f in self.request.files.items():
            tmp_file_path = _util.mk_tmp_file()[1]
            f.save(tmp_file_path)

            file = _file.create(tmp_file_path, f.filename, 'Uploaded via HTTP API')
            _unlink(tmp_file_path)

            r.append({
                'uid': str(file.uid),
            })

        # Request was from CKEditor
        if self.arg('CKEditor') and self.arg('CKEditorFuncNum'):
            script = 'window.parent.CKEDITOR.tools.callFunction("{}", "{}", "");' \
                .format(self.arg('CKEditorFuncNum'), _file.get(r[0]['uid']).get_url())

            # CKEditor requires such response format
            r = '<script type="text/javascript">{}</script>'.format(script)

        return r


class Get(_routing.Controller):
    """Get information about a file
    """

    def exec(self) -> dict:
        if _auth.get_current_user().is_anonymous:
            raise self.forbidden()

        try:
            return _file.get(self.arg('uid')).as_jsonable(**dict(self.args))

        except _file.error.FileNotFound as e:
            raise self.not_found(str(e))
