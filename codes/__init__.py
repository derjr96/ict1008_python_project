from flask import Flask

#app = Flask(__name__, template_folder='C:/Users/root/Documents/GitHub/ict1008_python_project/templates')
app = Flask(__name__, template_folder="../templates")


from codes import routes
