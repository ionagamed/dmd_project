from flask import Flask


from .controllers import queries


app = Flask('DMD Frontend', template_folder='./dmd_project/templates')
app.config['DEBUG'] = True


app.register_blueprint(queries, url_prefix='/')
