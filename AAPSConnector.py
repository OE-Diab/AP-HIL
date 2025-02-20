import time

import requests
from flask import Flask, Response, request
from http import HTTPStatus
from AAPSHandler import AAPSHandler

server = Flask(__name__)

handler_instance = AAPSHandler()


@server.route('/')
def index():
    return Response("The server refuses the attempt to brew coffee with a teapot.", 418)

@server.route('/', methods=["POST"])
def checkServerStatus():
    return Response("", HTTPStatus.OK)

@server.route('/basal', methods=["POST"])
def setBasal():
    if "insulin" in request.values:
        insulinRate = request.values.get("insulin")
        print("Insulin received: " + insulinRate)
        handler_instance.setBasal(float(insulinRate))
    return Response("", HTTPStatus.OK)

@server.route('/initialize', methods=["POST"])
def initializeSimulation():
    status = handler_instance.initializePatient(patient_name="adolescent#001.mat")
    if status:
        return Response(" ", HTTPStatus.OK)
    else:
        return Response(" ", HTTPStatus.BAD_REQUEST)


@server.route('/bolus', methods=["POST"])
def dosingInsulin():
    dataWasReceived = False
    if "insulin" in request.values:
        insulin = request.values.get("insulin")
        handler_instance.addInsulin(float(insulin))
        dataWasReceived = True
    if "carbs" in request.values:
        carbs = request.values.get("carbs")
        handler_instance.addInsulin(float(carbs))
        dataWasReceived = True
    if dataWasReceived:
        return Response("", HTTPStatus.OK)
    else:
        return Response("", HTTPStatus.PRECONDITION_FAILED)


@server.route('/getBG', methods=["POST"])
def requestBloodGlucose():
    result, status = handler_instance.getBloodGlucose()
    print("BG sent: "+result)
    if status:
        return Response(result, HTTPStatus.OK)
    else:
        return Response(result, HTTPStatus.BAD_REQUEST)


server.run(host="0.0.0.0", port=5001)