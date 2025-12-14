from flask import Flask

app = Flask(__name__)
app.secret_key = "BG\xeb\xdd\t\xf1\x93\xbeWp\xbadasb\xffla V"
# app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:MHung2934!@localhost/FlaskProject3?charset=utf8mb4"
# app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True