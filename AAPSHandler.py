from threading import Thread
import json
import requests
import datetime
import time
import random
import msvcrt
import os
import socket


class AAPSHandler:
    __SIMULATION_PERIOD = 2

    """
    This class can be used by a client to make requests to the uva_padova_API simply from Python code.
    In addition, the attributes of the class make input and output data more organized.

    Args:
        HOST_ADDRESS (str, optional): The IP address of the server that runs the uva_padova_API.py.
            Defaults to the loopback address.
        PORT (int, optional): The port number where the uva_padova_API.py can be accessed on the server.
            Defaults to 5000.

    Note:
        The methods don't check the correctness of the input parameters.
        To enter the input parameters correctly, please read the documentation of UVAPadova Simulator.

    Attributes:
        HOST_ADDRESS (str): The IP address of the server that runs the uva_padova_API.py.
        PORT (int): The port number where the uva_padova_API.py can be accessed on the server.
        listOfCarbohydrateIntakes (list(float)):
            A list which contains the carbohydrate intakes during the simulation line.
        listOfInsulinIntakes (list(float)): A list which contains the insulin intakes during the simulation line.
        listOfBloodGlucoseValues (list(float)):A list which contains the blood glucose values in 5 minute increments.

    """

    def __init__(self, HOST_ADDRESS: str = "127.0.0.1", PORT: int = 5000):
        self.HOST_ADDRESS = "http://" + HOST_ADDRESS
        self.PORT = PORT
        self.__received_bloodglucose = list()
        self.__carbohydrate_to_dose = list()
        self.__insulin_to_dose = list()
        self.__scheduler_Thread: Thread = None
        self.__cancellation_token: bool = None
        self.__basalRate = 0.0
        self.__summedValues = {
            "time": 0,
            "insulin": 0,
            "ch": 0
            }
        #self.plot_host = socket.gethostname()  # as both code is running on same pc
        #self.plot_port = 5002  # socket server port number

        #self.client_socket = socket.socket()  # instantiate
        #self.client_socket.connect(('127.0.0.1', 34000))  # connect to the server

        self.message = ''
        #keyboard.add_hotkey('i', lambda: print("Input the value:"), self.__insulin_to_dose.append(float(input())))

    def __del__(self):
        self.__cancellation_token: bool = False
        self.__scheduler_Thread.join()
        #self.client_socket.close()

    def initializePatient(self, patient_name: str, pump: str = None, sensor: str = None) -> bool:
        """
        This method initialize a new simulation (resets the simulation line).

        Args:
            patient_name (str): The identifier of the patient.
            pump (str, optional): The type of the insulin pump.
            sensor (str, optional): The type of the CGM sensor.

        Returns:
            bool: If the initialization was successful returns true, otherwise returns false.
        """

        self.__cancellation_token = False
        params = {'id': patient_name}
        if pump is not None:
            params["pump"] = pump
        if sensor is not None:
            params["sensor"] = sensor
        response = requests.get(url=self.HOST_ADDRESS+":"+str(self.PORT)+"/createSimulation", params=params)
        self.__cancellation_token = True
        self.__scheduler_Thread = Thread(target=self.__SimulationScheduler)
        self.__scheduler_Thread.start()
        return response.ok

    def addInsulin(self, amount: float):
        """This method doses insulin to the patient.

        Args:
            amount (float): The amount of insulin in units.
        """
        self.__insulin_to_dose.append(amount)

    def addCarbohydrate(self, amount: float):
        """This method intakes carbohydrate to the patient.

        Args:
            amount (float): The amount of carbohydrate in grams.
        """
        self.__carbohydrate_to_dose.append(amount)

    def getBloodGlucose(self, aggregated: bool = False) -> (str, bool):
        """This method... .

        Args:
            aggregated (bool): .

        Returns:
            str: If the request was successful returns true, otherwise returns false.
            bool: If the request was successful returns true, otherwise returns false.
        """
        if self.__received_bloodglucose:
            if aggregated:
                result = sum(self.__received_bloodglucose)/len(self.__received_bloodglucose)
            else:
                result = self.__received_bloodglucose.pop()
            self.__received_bloodglucose.clear()
            status = True
            result = result+(random.random()*3)
        else:
            result, status = "Blood glucose value isn't available.", False
        if status:
            result = str(int(time.time())) + '|' + str(result)
        return result, status

    def setBasal(self, rate: float):
        self.__basalRate = rate

    def __getBasalPerStep(self):
        return (self.__basalRate*self.__SIMULATION_PERIOD)/60

    def __SimulationScheduler(self):
        """This method extends the initialized simulation by 5 minutes.
        Insulin or/and carbohydrate intake can be added to the simulation.

        Note:
            Before calling this function, please initialize a patient by "initializePatient" function.
        """
        while self.__cancellation_token:
            time_at_start = time.time()
            params = {}
            if self.__carbohydrate_to_dose:
                params["ch"] = sum(self.__carbohydrate_to_dose)
                self.__carbohydrate_to_dose.clear()
                self.__summedValues["ch"] += params["ch"]
            params["insulin"] = sum(self.__insulin_to_dose)+self.__getBasalPerStep()
            self.__insulin_to_dose.clear()
            self.__summedValues["insulin"] += params["insulin"]
            params["steptime"] = self.__SIMULATION_PERIOD
            response = requests.get(url=self.HOST_ADDRESS + ":" + str(self.PORT) + "/simulate", params=params)
            if response.ok:
                result = response.json()
                result = json.loads(result)
                self.__received_bloodglucose.append(float(result["bloodGlucose"]))
            #self.__StatusPrinter(response, params)
            self.__summedValues["time"] += self.__SIMULATION_PERIOD
            time_at_end = time_at_start+self.__SIMULATION_PERIOD*60
            while time_at_end > time.time():
                if msvcrt.kbhit():
                    while msvcrt.kbhit():
                        key = msvcrt.getch().decode("utf-8")
                        self.__consoleInput(key)
                time.sleep(1)

    def __consoleInput(self, key):
        if key == "i":
            print("Input the insulin value in mg/dl:")
            self.__insulin_to_dose.append(float(input()))
            print("OK!")
        elif key == "c":
            print("Input the carbohydrate value in g:")
            self.__carbohydrate_to_dose.append(float(input()))
            print("OK!")
        elif ord(key) == 27:
            exit()

    def __StatusPrinter(self, response, params):
        os.system('cls')
        print(f"Elapsed minutes:{self.__summedValues['time']};"
              f"Insulin dosed:{round(self.__summedValues['insulin'],4)};Carbohydrate dosed:{self.__summedValues['ch']}")
        print("The current basal rate is: " + str(self.__basalRate))
        print("The last blood glucose value: " + str(json.loads(response.json())["bloodGlucose"])
              if response.ok else response.content)
        print("Insulin dose in the last "+str(self.__SIMULATION_PERIOD)+" minutes:", params["insulin"]
              if "insulin" in params else 0)
        print("Carbohydrate dose in the last " + str(self.__SIMULATION_PERIOD) + " minutes:", params["ch"]
              if "ch" in params else 0)
        print("Press i to dose insulin or press c to dose carbohydrate.")
        self.message = "in-" + str(params["insulin"] if "insulin" in params else 0) + ' '
        self.client_socket.send(self.message.encode())  # send message
        self.message = "bg-" + str(json.loads(response.json())["bloodGlucose"]) + ' '
        self.client_socket.send(self.message.encode())  # send message
        self.message = "me-" + str(params["ch"] if "ch" in params else 0) + ' '
        self.client_socket.send(self.message.encode())  # send message
        self.message = "ti-" + datetime.datetime.now().strftime('%H:%M:%S') + ' '
        self.client_socket.send(self.message.encode())

#handler = AAPSHandler()
#handler.initializePatient(patient_name="adolescent#001.mat")
#print("Ez megy??")
#while True:
#    print(handler.getBloodGlucose(aggregated=True))
#    time.sleep(300)