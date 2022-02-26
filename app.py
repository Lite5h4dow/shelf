from flask import Flask, request, jsonify, make_response
from flask.templating import render_template
from tinydb import TinyDB,Query 
# import json
# import os
import uuid
import time
import board
import neopixel
import math

#importing config file and defaulting to None if file isnt there
# config = None
# if (os.path.exists("./config.json")):
#     with open("./config.json", "r") as jsonfile: 
#         config=json.load(jsonfile)
# 
app = Flask(__name__, static_url_path="", static_folder="static", template_folder="templates")
app.debug = True
pixel_pin = board.D18

d = TinyDB("./db.json")
num_pixels = 416 * 6
group_size = 3
group_pixels = 13
tail = 3 
Order = neopixel.RGB
pixels = neopixel.NeoPixel(
            pixel_pin, num_pixels, brightness=1, auto_write=False, pixel_order=Order
        )


''' Utility function that puts all 
non-positive (0 and negative) numbers on left 
side of arr[] and return count of such numbers '''
def segregate(arr, size):
    j = 0
    for i in range(size):
        if (arr[i] <= 0):
            arr[i], arr[j] = arr[j], arr[i]
            j += 1 # increment count of non-positive integers 
    return j 
  
  
''' Find the smallest positive missing number 
in an array that contains all positive integers '''
def findMissingPositive(arr, size):
    # Mark arr[i] as visited by 
    # making arr[arr[i] - 1] negative. 
    # Note that 1 is subtracted 
    # because index start 
    # from 0 and positive numbers start from 1 
    for i in range(size):
        if (abs(arr[i]) - 1 < size and arr[abs(arr[i]) - 1] > 0):
            arr[abs(arr[i]) - 1] = -arr[abs(arr[i]) - 1]
              
    # Return the first index value at which is positive 
    for i in range(size):
        if (arr[i] > 0):
              
            # 1 is added because indexes start from 0 
            return i + 1
    return size + 1
  
''' Find the smallest positive missing 
number in an array that contains 
both positive and negative integers '''
def findMissing(arr, size):
      
    # First separate positive and negative numbers 
    shift = segregate(arr, size)
      
    # Shift the array and call findMissingPositive for 
    # positive part 
    return findMissingPositive(arr[shift:], size - shift) 

def findUnused():
    positions = [p['position'] for p in d.all()]
    return findMissing(positions, positions.__len__())

#returns the ammount of pixels are available to be allocated to groups
def usable_pixels():
    return int(num_pixels - (num_pixels % group_size))

#returns the maximum ammount of usable groups in the provided pixel count
def max_groups():
    return math.floor(usable_pixels() / group_size)

#returns the group that the current led is in
def current_group(pos):
    return math.floor(pos/group_size)

#returns position relative to the brightest group
def wrap_calc(pos, brightest):
    group = current_group(pos)
    sigma = brightest - group
    return sigma if sigma >= 0 else sigma + max_groups()

# run scan animation
def scan_to(scan_to):
    g = current_group(scan_to)
    tail_end = g-tail

    for group in range(g+1):
        a = [(0,0,0)] * ((g-tail)*group_pixels) if (g-tail) < 0 else []
        b = []
        for i in range(tail-g):
            rc = (255/(tail+1) * i)
            gc = (255/(tail+1) * i)
            bc = (255/(tail+1) * i)
            t = [(rc,gc,bc)] * group_pixels
            b = b + t

        c = [(255,255,255)] * group_pixels
        inter = a+b+c
        remainder = [(0,0,0)] * (num_pixels - len(inter))

        whole = inter+remainder
        for i, val in enumerate(whole):
            pixels[i] = val

        print(whole)
        time.sleep(0.001)
        pixels.show()

def light_position(position):
    before = [(0,0,0)] * (current_group(position) * group_pixels)
    g = [(255,255,255)] * group_pixels
    splat = before + g
    after = [(0,0,0)] * (num_pixels - len(splat))
    result = splat + after
    
    print(result)

    for i, val in enumerate(result):
        pixels[i] = val
    pixels.show()

def byPosition(phone):
    return phone['position']

class Phone:
    def __init__(self, name, position, colour):
        self.uuid = str(uuid.uuid4())
        self.name = name
        self.position = position
        self.colour = colour

    def data(self):
        return {"uuid":self.uuid, "name": self.name, "position": self.position, "color": self.colour}

phone = Query()

@app.get("/getPhones")
def getPhones():
    response = make_response(jsonify(d.getAll()))
    response.headers["Content-Type"] = "application/json"
    return response

@app.post("/editPhone")
def editPhone():
    if request.json == None:
        return "Invalid Request", 400

    p = d.search(phone.uuid == request.json['uuid'])[0]
    
    if p == None:
        return "Phone Dosent Exist", 400

    d.update(request.json, phone.uuid == request.json["uuid"])

    return "updatedPhone", 200
    
@app.post("/deletePhone/<uuid>")
def deletePhone(uuid):
    d.remove(phone.uuid == uuid)
    return "Deleted", 200

@app.post("/scanTo/<position>")
def scanTo(position):
    print("would scan")
    scan_to(int(position))
    return "",200

@app.get("/")
def index():
    phones = d.all()#.sort(key=byPosition)
    if phones == None:
        phones = []
    return render_template("index.html", phones=phones)

@app.post("/")
def addPhone():
    if request.args == None:
        return "Invalid Request", 400

    name = request.form.get('name') if request.form.get('name') else "unknown phone"
    colour = request.form.get('colour') if request.form.get('colour') else "#FFFFFF"
    position = request.form.get('position') if request.form.get('position') else findUnused()
    p = Phone(name, position, colour)
    d.insert(p.data())
    phones = d.all()#.sort(key=byPosition)
    if phones == None:
        phones = []

    return render_template("index.html", phones=phones)

@app.post("/lightPosition/<position>")
def lightPosition(position):
    light_position(int(position))
    return "", 200



# @app.get("pin")
# def pinUnlock():
#     if request.json == None:
#         return "no json provided", 400
# 
#     if "pin" not in request.json:
#         return "no pin provided", 400
# 
# 
#     lock = board.D12
#     if request.json.pin == 1234:
#         lock.HIGH
#     else: 
#         lock.LOW

if __name__ == "__main__":
    app.run(debug=True)
