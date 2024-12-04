from flask import Flask, render_template ,request
import pymysql
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import razorpay
razorpay_key_id="rzp_test_ukiKrRE4eZXpXh"
razorpay_key_secret="K0OxX2yb3FKixJmZJr4NrgFC"
client=razorpay.Client(auth=(razorpay_key_id,razorpay_key_secret))
verify_otp="0"
db_conig={
    'host':"localhost",
    'database':'ecommerce',
    'user':'root',
    'password':'root'
}
app = Flask(__name__)
@app.route("/")
def landing():
    return render_template("home.html") 
@app.route("/contactus")
def contactus():
    return render_template("contactus.html")
@app.route("/aboutus")
def aboutus():
    return render_template('aboutus.html')
@app.route("/home")
def home():
    return render_template("home.html")
@app.route("/login")
def login():
    return render_template("login.html")
@app.route("/register")
def register():
    return render_template("register.html")
@app.route("/registerdata",methods=["POST","GET"])
def registerdata():
    if request.method=="POST":
        name=request.form['name']
        username=request.form['username']
        email=request.form['email']
        mobile=request.form['mobile']
        password=request.form['password']
        cpassword=request.form['confirm-password']
        """
        print(name)
        print(username)
        print(email)
        print(mobile)
        print(password)
        print(cpassword)
        """
        if password==cpassword:
            otp1 = random.randint(111111, 999999)
            global verify_otp
            verify_otp=str(otp1)
            from_email = 'mannem.mahendra2407@gmail.com'
            to_email = email
            subject = 'OTP For Validation'
            body = f'OTP for Validation is {verify_otp}'

            msg = MIMEMultipart()
            msg['From'] = from_email
            msg['To'] = to_email
            msg['subject'] = subject
            msg.attach(MIMEText(body, 'plain'))

            server = smtplib.SMTP('smtp.gmail.com', '587')
            server.starttls()
            server.login('mannem.mahendra2407@gmail.com', 'dsju jftf aqnd wtje')
            server.send_message(msg)
            server.quit()

            return render_template("verifyemail.html",name = name,username=username,email=email,mobile=mobile,password=password)
        else:
            return 'make sure that password and confirm password are same'
        
    else:
        return "<h3 style='color : red'; >Data Get in Wrong Manner</h3>"

@app.route("/verifyemail",methods=["POST","GET"])                                  
def verifyemail():
        if request.method == "POST":
            name = request.form['name']
            username=request.form['username']
            email=request.form['email']
            mobile=request.form['mobile']
            password=request.form['password']
            otp=request.form['otp']
            if(otp == verify_otp):
                try:
                    conn=pymysql.connect(**db_conig)
                    cursor=conn.cursor()
                    q="INSERT INTO register(name,username,email,mobile,password) VALUES(%s,%s,%s,%s,%s)"
                    cursor.execute(q,(name,username,email,mobile,password))
                    conn.commit()
                except:
                    return "some random errors occured"

                else:
                    return render_template("login.html")
            else:
                return render_template("register.html")
        else:
            return "<h3 style='color : red';>Data Get in Wrong Manner</h3>"
@app.route("/userlogin",methods=["POST","GET"])
def userlogin():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        try:
            conn=pymysql.connect(**db_conig)
            cursor=conn.cursor()
            q="select * from register where username=%s"
            cursor.execute(q,(username,))
            row=cursor.fetchone()
            if(row==None):
                return "User DOesn't Exist,Create Account First"
            else:
                if password!=row[4]:
                    return "Incorrect Password"
                else:
                        conn=pymysql.connect(**db_conig)
                        cursor=conn.cursor()
                        q="INSERT Into userlogin(username,password) values(%s,%s)"
                        cursor.execute(q,(username,password))
                        conn.commit()
                        return render_template("userhome.html",name=username)

        except:
            return "some random errors occured"

        else:
            return render_template("login.html")
    else:
        return "<h3 style='color : red';>Data Get in Wrong Manner</h3>"
@app.route("/add_to_cart",methods=["POST","GET"])
def add_to_cart():
    if request.method=="POST":
        username=request.form["username"]
        productname=request.form["productname"]
        quantity=request.form["quantity"]
        price=request.form["price"]
        print(username)
        print(productname)
        print(quantity)
        print(price)
        totalprice=int(price)*int(quantity)
        totalprice=str(totalprice)

        try:
            conn=pymysql.connect(**db_conig)
            cursor=conn.cursor()
            q="INSERT Into cart(username,productname,quantity,price,totalprice) values(%s,%s,%s,%s,%s)"
            cursor.execute(q,(username,productname,quantity,price,totalprice))
            conn.commit()
        except:
            return "some random errors occured"

        else:
            return render_template("userhome.html",name=username)
    else:
        return "<h3 style='color : red';>Data Get in Wrong Manner</h3>"
@app.route("/cartpage",methods=["GET"])
def cartpage():
    username=request.args.get('username')
    print(username)
    try:
        conn=pymysql.connect(**db_conig)
        cursor=conn.cursor()
        q="select * from cart where username=(%s)"
        cursor.execute(q,(username))
        rows=cursor.fetchall()
        print(rows)
        subtotal=0
        for i in rows:
            subtotal+=int(i[4])
            result=subtotal*100
            order=client.order.create({
                    'amount':result,
                    'currency':'INR',
                    'payment_capture':'1'
                })
            print(order)
    except:
        return "Some Random Errors Occurred"
    else:
        return render_template("cart.html",data=rows,grand_total=subtotal,order=order)
@app.route("/sucess",methods = ["POST","GET"])
def sucess():
    payment_id = request.form.get("razorpay_payment_id")
    order_id = request.form.get("razorpay_order_id")
    signature = request.form.get("razorpay_signature")
    dict1 = {
        'razorpay_order_id' : order_id,
        'razorpay_payment_id' : payment_id,
        'razorpay_signature' : signature
    }
    try:
        client.utility.verify_payment_signature(dict1)
        return render_template("success.html")
    except:
        return render_template("failed.html")


if __name__ == "__main__":
    app.run(port=5001)