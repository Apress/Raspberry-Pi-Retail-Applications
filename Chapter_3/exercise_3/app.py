from flask import Flask, render_template, request, redirect
from create_order import CreateOrder
import pyqrcode
import socket

hostname = ''
DEBUG = True

if not DEBUG:
   from gpiozero import Servo
   servo = Servo(25)

app = Flask(__name__)

item_dict = {'coke': {'price':1, 'available': True},
            'energy bar': {'price':2.5, 'available': True},
            'chewing gum': {'price':0.5, 'available': True}}

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

def control_servo(servo_comm):
   if not DEBUG:
      try:
         eval(servo_comm)
      except Exception as e:
         print(e)
   else:
      print(servo_comm)

@app.route("/")
def main():
   global hostname
   hostname = request.headers.get('Host')
   print(hostname)
   control_servo('servo.max')
   templateData = {
      'items' : item_dict
      }

   return render_template('main.html', **templateData)

@app.route("/success")
def success():
   global hostname
   control_servo('servo.min')
   return render_template('success.html')

@app.route("/cancel")
def cancel():
   return render_template('cancel.html')

# The function below is executed when someone requests a URL with the pin number and action in it:
@app.route("/<item>/<action>")
def action(item, action):
   global hostname

   print(item, item_dict[item]['price']) 

   response = CreateOrder().create_order(item_dict[item]['price'], item, hostname)
   order_id = ''
   print('Creating Order...')
   if response.status_code == 201:
      order_id = response.result.id
      for link in response.result.links:
         print(('\t{} link: {}\tCall Type: {}'.format(str(link.rel).capitalize(), link.href, link.method)))
      print('Created Successfully\n')
      print('Copy approve link and paste it in browser. Login with buyer account and follow the instructions.\nOnce approved hit enter...')
      return redirect(response.result.links[1].href, code=302)
   else:
      print('Link is unreachable')
      exit(1)


if __name__ == "__main__":
   qrcode = pyqrcode.create('http://' + get_ip()+ ':5000')
   print(qrcode.terminal(quiet_zone=1))   
   app.run(host='0.0.0.0', port=5000, debug=True)