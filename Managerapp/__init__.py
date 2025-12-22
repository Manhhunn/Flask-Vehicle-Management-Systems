from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.secret_key = "BG\xeb\xdd\t\xf1\x93\xbeWp\xbadasb\xffla V"
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:MHung2934!@localhost/cnpmdb5?charset=utf8mb4"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True

app.config["VNPAY_TmnCode"] = "Z7BOO9SJ"
app.config["VNPAY_HashSecret"] = "SO3KMJLH9XNCBGTC3HUH9LIEFIW61F0P"
app.config["VNPAY_Url"] = "https://sandbox.vnpayment.vn/paymentv2/vpcpay.html"

app.config["VNPAY_ReturnUrl"] = "http://127.0.0.1:5000/api/payment/vnpay_return"

db = SQLAlchemy(app)
login =LoginManager(app)
import Managerapp.admin