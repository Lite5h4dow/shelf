from flask import Flask, request, jsonify, make_response
from flask.templating import render_template
from pysondb import db
import json
import os
import time
import board
import neopixel
import math

#importing config file and defaulting to None if file isnt there
config = None
if (os.path.exists("./config.json")):
    with open("./config.json", "r") as jsonfile: 
        config=json.load(jsonfile)

app = Flask(__name__)
pixel_pin = board.D18

d = db.getDb("./db.json")
num_pixels = 144
group_size = d.getAll().count
tail = 6
Order = neopixel.RGB
pixels = neopixel.NeoPixel(
            pixel_pin, num_pixels, brightness=0.1, auto_write=False, pixel_order=Order
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
    positions = [p['position'] for p in d.getAll()]
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
    for group in range (math.floor(scan_to / group_size)):
        for position in range(scan_to if scan_to <= usable_pixels() else usable_pixels()):
            usable_tail = wrap_calc(position, group) +1
            if usable_tail <= tail:
                r = g = b = math.ceil(255 / usable_tail)
                pixels[position] = (r,g,b)
            else:
                pixels[position] = (0,0,0)
        pixels.show()
        time.sleep(0.001)



class Phone:
    def __init__(self, name, position, colour):
        self.name = name
        self.position = position
        self.colour = colour

    def data(self):
        return {"name": self.name, "position": self.position, "color": self.colour}

@app.get("/getPhones")
def getPhones():
    response = make_response(jsonify(d.getAll()))
    response.headers["Content-Type"] = "application/json"
    return response

@app.post("/addPhone")
def addPhone():
    if request.json == None:
        return "Invalid Request", 400

    name = request.json["name"] if "name" in request.json else "unknown phone"
    colour = request.json["colour"] if "colour" in request.json else {"r":255, "g":255, "b":255}
    position = request.json["position"] if "position" in request.json else findUnused()
    p = Phone(name, position, colour)
    d.add(p.data())

    return "Added phone", 200

@app.post("/editPhone")
def editPhone():
    if request.json == None:
        return "Invalid Request", 400

    p = d.getById(request.json['id'])
    
    if p == None:
        return "Phone Dosent Exist", 400

    d.updateById(request.json["id"], request.json)

    return "updatedPhone", 200
    
@app.post("/deletePhone")
def deletePhone():
    if request.json == None:
        return "Invalid Request", 400

    d.deleteById(request.json["id"])
    return "Deleted", 200

@app.put("/scanTo")
def scanTo():
    if request.json == None:
        return "invalid request", 400
    
    if "position" not in request.json:
        return "position missing", 400

    scan_to(request.json.position)
    return 200

@app.route("/")
def index():
    return render_template("index.html", phones=d.getAll())

@app.get("pin")
def pinUnlock():
    if request.json == None:
        return "no json provided", 400

    if "pin" not in request.json:
        return "no pin provided", 400


    lock = board.D12
    if request.json.pin == 1234:
        lock.HIGH
    else 
        lock.LOW


if __name__ == "__main__":
    app.run(debug=True)
