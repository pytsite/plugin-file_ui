"""PytSite File HTTP API Endpoints
"""
__author__ = 'Oleksandr Shepetko'
__email__ = 'a@shepetko.com'
__license__ = 'MIT'

from os import unlink
from pytsite import util, routing, http
from plugins import file, auth


class Post(routing.Controller):
    """Upload a file
    """

    def exec(self):
        if auth.get_current_user().is_anonymous:
            raise self.forbidden()

        if not self.request.files:
            raise RuntimeError('No files received')

        r = []
        for field_name, f in self.request.files.items():
            tmp_file_path = util.mk_tmp_file()[1]
            f.save(tmp_file_path)

            f = file.create(tmp_file_path, f.filename, 'Uploaded via HTTP API')
            unlink(tmp_file_path)

            r.append({
                'uid': str(f.uid),
            })

        # Request was from CKEditor
        if self.arg('CKEditor') and self.arg('CKEditorFuncNum'):
            script = 'window.parent.CKEDITOR.tools.callFunction("{}", "{}", "");' \
                .format(self.arg('CKEditorFuncNum'), file.get(r[0]['uid']).get_url())

            # CKEditor requires such response format
            r = http.Response('<script type="text/javascript">{}</script>'.format(script), mimetype='text/html')

        return r


class Get(routing.Controller):
    """Get information about a file
    """

    def exec(self) -> dict:
        if auth.get_current_user().is_anonymous:
            raise self.forbidden()

        try:
            return file.get(self.arg('uid')).as_jsonable(**self.args)

        except file.error.FileNotFound as e:
            raise self.not_found(str(e))
