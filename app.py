from flask import Flask, request, jsonify, make_response
from pysondb import db
import json
import os

app = Flask(__name__)

#importing config file and defaulting to None if file isnt there
config = None
if (os.path.exists("./config.json")):
    with open("./config.json", "r") as jsonfile: 
        config=json.load(jsonfile)

d = db.getDb("./db.json")

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

if __name__ == "__main__":
    app.run(debug=True)
