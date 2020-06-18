from flask import Flask, request, redirect, render_template
from flask_restful import Resource, Api
from  requests import get, put
import datetime
import pickle


app = Flask(__name__)
api = Api(app)

mainDict = dict()
cheatTypes = ["Wallhack", "Aimbot", "Silent Aimbot", "VSAT", "Auto Crash Game"]

#####################################
def Init():
    global mainDict
    if "STATS" not in mainDict:
        mainDict["STATS"] = dict()

def ReadBDDFromFile():
    global mainDict

    file = open("BDDBO2.pkl", "rb")
    mainDict = pickle.load(file)
    file.close()

def WriteBDDToFile():
    global mainDict

    file = open("BDDBO2.pkl", "wb")
    pickle.dump(mainDict, file)
    file.close()
#####################################


ReadBDDFromFile()
Init()


#####################################
def AddUser(steamId):
    global mainDict
    mainDict[steamId] = dict()
    mainDict[steamId]["steamId"] = steamId
    mainDict[steamId]["lastName"] = GetUserNameFromSteam(steamId)
    mainDict[steamId]["recordsCount"] = 0

def CheckUserExist(steamId):
    global mainDict
    return (steamId in mainDict)

def AddRecord(steamId, cheatType):
    global mainDict

    if not CheckUserExist(steamId):
        AddUser(steamId)

    timestamp = datetime.datetime.now().strftime("%A, %d. %B %Y %H:%M:%S")
    mainDict[steamId][timestamp] = cheatType

    mainDict[steamId]["recordsCount"] = mainDict[steamId]["recordsCount"] + 1
    mainDict[steamId]["lastRecordTime"] = timestamp
    mainDict[steamId]["lastRecordType"] = cheatType

    WriteBDDToFile()

def GetUserNameFromSteam(steamId):
    return "UNKNOWN_YET"

def GetUser(steamId):
    global mainDict
    return mainDict[steamId]
#####################################


#####################################
def AddGame(cheated):
    global mainDict

    if not CheckTodayExist():
        AddNewDay()

    timestamp = datetime.datetime.now().strftime("%d/%m/%Y")
    
    if cheated:
        mainDict["STATS"][timestamp]["cheatedGamesCount"] = mainDict["STATS"][timestamp]["cheatedGamesCount"] + 1
    else:
        mainDict["STATS"][timestamp]["legitGamesCount"] = mainDict["STATS"][timestamp]["legitGamesCount"] + 1

    WriteBDDToFile()

def GetTodayStats():
    global mainDict

    if not CheckTodayExist():
        AddNewDay()

    timestamp = datetime.datetime.now().strftime("%d/%m/%Y")

    if(mainDict["STATS"][timestamp]["legitGamesCount"] == 0) and (mainDict["STATS"][timestamp]["cheatedGamesCount"] == 0):
        return 0.0
    else:
        return (mainDict["STATS"][timestamp]["cheatedGamesCount"] / (mainDict["STATS"][timestamp]["cheatedGamesCount"] + mainDict["STATS"][timestamp]["legitGamesCount"])) * 100

def AddNewDay():
    global mainDict

    timestamp = datetime.datetime.now().strftime("%d/%m/%Y")
    
    mainDict["STATS"][timestamp] = dict()
    mainDict["STATS"][timestamp]["legitGamesCount"] = 0
    mainDict["STATS"][timestamp]["cheatedGamesCount"] = 0

    WriteBDDToFile()

def CheckTodayExist():
    return (datetime.datetime.now().strftime("%d/%m/%Y") in mainDict["STATS"])
#####################################


#####################################
def GenerateStatsImg():
    return True
#####################################


@app.route('/')
def index():
    global mainDict, cheatTypes
    return render_template("index.html", mainDict = mainDict, cheatTypes = cheatTypes, todayStats = GetTodayStats())


@app.route('/addRecord',methods = ['POST'])
def addRecord():
    global mainDict, cheatTypes
    reqParam = request.form

    if reqParam['steamId'] != "":
        AddRecord(reqParam['steamId'], reqParam['cheatType'])

    return redirect("http://localhost:8666/", code=302)


@app.route('/updateTodayStats',methods = ['POST'])
def updateTodayStats():
    global mainDict, cheatTypes
    reqParam = request.form

    AddGame(int(reqParam['cheated']))
    

    return redirect("http://localhost:8666/", code=302)


@app.route('/getUserStats',methods = ['POST'])
def getUserStats():
    global mainDict, cheatTypes
    reqParam = request.form

    return render_template("specificUserStats.html", user = GetUser(reqParam['steamId']))


if __name__ == '__main__':
     app.run(port='8666', host='0.0.0.0')
