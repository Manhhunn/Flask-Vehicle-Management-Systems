from flask import Flask, render_template, jsonify
from dao import *
from Managerapp import app, dao



@app.route('/')
def hello_world():  # put application's code here
    return render_template('index.html')



if __name__ == '__main__':
    from Managerapp.admin import *
    app.run(debug=True)