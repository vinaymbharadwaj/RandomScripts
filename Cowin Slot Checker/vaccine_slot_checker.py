import requests
import json
import sys
import time
from datetime import datetime, timedelta
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


def get_slot_details(pincode, date):
    url = 'https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByPin'
    params = dict(
        pincode=pincode,
        date=date
    )
    ret_value = {}
    try:
        resp = requests.get(url=url, params=params)
        ret_value = resp.json()
        #print(json.dumps(ret_value, indent=2))
    except Exception as e:
        print(e)
        print(resp.text)   
    return ret_value

def window_alert(session_data):
    app = QApplication(sys.argv)
    w = QWidget()
    w.setGeometry(100,100,500,500)
    w.setWindowTitle("Cowin Alert")
    b = QLabel(w)
    if(session_data):
        b.setText(json.dumps(session_data, indent=2))
    else:
        b.setText("No vaccine available")
    b.move(50,20)
    w.show()
    sys.exit(app.exec_())

def main():
    # Check input file
    input_file = "script_input.json"
    input_json = json.load(open(input_file,"r"))
    n = datetime.now()
    today = n.strftime("%d-%m-%Y")
    # How long do you want the script to run?
    time_change = timedelta(hours=24)
    new_time = n + time_change
    i = 1
    while(datetime.now() < new_time):
        print("Check number "+str(i))
        i+=1
        vaccine_center_data = get_slot_details(pincode=input_json["pincode"], date=today)
        if(vaccine_center_data):
            for center in vaccine_center_data["centers"]:
                for session in center["sessions"]:
                    if(session["available_capacity"] > 0 and session["min_age_limit"] <= input_json["age_limit"]):
                        session_data = {
                            "Name": center["name"],
                            "Address": center["address"],
                            "Availability": session["available_capacity"],
                            "VaccineName": session["vaccine"],
                            "Time": datetime.now().strftime("%H:%M:%S")
                        }
                        print(json.dumps(session_data, indent=2))
                        window_alert(session_data)
        time.sleep(input_json["check_interval_minutes"]*60)

if __name__ == "__main__":
    main()