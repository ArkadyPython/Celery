from flask import Flask
from flask import request
from flask.views import MethodView
from flask import jsonify, send_file
from celery import Celery
from celery.result import AsyncResult
from upscale import upscale




app_name = 'app'
app = Flask(app_name)
app.config['UPLOAD_FOLDER'] = 'files'
celery = Celery(
    app_name,
    backend='redis://localhost:6379/3',
    broker='redis://localhost:6379/4'
)
celery.conf.update(app.config)

class ContextTask(celery.Task):
    def __call__(self, *args, **kwargs):
        with app.app_context():
            return self.run(*args, **kwargs)

celery.Task = ContextTask


@celery.task()
def upscale_photo(path_1, path_2):
    result = upscale(path_1, path_2)
    return result


class Task_Information_And_Links(MethodView):

    def get(self, task_id):
        task = AsyncResult(task_id, app=celery)
        json_data = request.json
        output_file_path = json_data['output_file_path']
        return jsonify({'status': task.status,
                       'output_file_path': output_file_path})

    def post(self):
        json_data = request.json
        input_file_path = json_data['input_file_path']
        output_file_path = json_data['output_file_path']
        task = upscale_photo.delay(input_file_path, output_file_path)
        return jsonify(
            {'task_id': task.id}
        )


class The_Processed_File(MethodView):

    def get(self, file_path):
        file_path = file_path
        return send_file(file_path, mimetype='image/gif')


TaskInformationAndLinks_view = Task_Information_And_Links.as_view('changephoto')
TheProcessedFile_view = The_Processed_File.as_view('newphoto')
app.add_url_rule('/upscale', view_func=TaskInformationAndLinks_view, methods=['POST'])
app.add_url_rule('/tasks/<task_id>', view_func=TaskInformationAndLinks_view, methods=['GET'])
app.add_url_rule('/processed/<file_path>', view_func=TheProcessedFile_view, methods=['GET'])


if __name__ == '__main__':
    app.run()