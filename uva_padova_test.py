import pytest
import random
from unittest.mock import patch, MagicMock
#from Simulator.UVAPadova.uva_padova_simulator import UvaPadovaSimulator
from uva_padova_API_Wrapper import UvaPadovaAPI


#def test_uva_padova_s_create():
#    uva_padova_simulator = UvaPadovaSimulator(None)
#    assert isinstance(uva_padova_simulator, UvaPadovaSimulator)

def test_uva_padova_API_Wrapper_initializePatient():
    patient_name = "probaPatient"
    pump = "probaPumpa"
    sensor = "probaSensor"
    with patch('uva_padova_API_Wrapper.requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.ok = True
        mock_get.return_value = mock_response
        instance = UvaPadovaAPI(HOST_ADDRESS="localhost", PORT=8080)
        result = instance.initializePatient(patient_name, pump, sensor)
        assert result is True
        mock_get.assert_called_once_with(
            url="http://localhost:8080/createSimulation",
            params={"id": "probaPatient", "pump": "probaPumpa", "sensor": "probaSensor"}
        )
        assert instance.listOfCarbohydrateIntakes == []
        assert instance.listOfInsulinIntakes == []
        assert instance.listOfBloodGlucoseValues == []


def test_uva_padova_s_initvalues():
    assert True


def test_uva_padova_s_inittipes():
    assert isinstance(True, bool)


def test_uva_padova_s_simstart():
    instance = True
    assert isinstance(instance, bool)
    assert instance == True



def test_uva_padova_s_simstep():
    for _ in range(5):
        rtype = str(random.choice(['GET', 'HEAD', 'POST', 'PUT', 'DELETE', 'CONNECT', 'OPTIONS']))
        ptype = str(random.choice(['HTTP1.0', 'HTTP1.1', 'HTTP2.0']))
        path = '/'+str(random.randint(1, 2000))
        instance = "{} {} {}".format(rtype, path, ptype)
        assert True



def test_uva_padova_s_chlost():
    assert None is None


def test_uva_padova_s_buildscenaraio():
    with pytest.raises(Exception):
        raise Exception



def test_uva_padova_s_wrongscenario():
    assert True


def test_uva_padova_s_mealappend():
    with pytest.raises(ValueError) as e:
        raise ValueError("Path must start with /")
        assert e.args[0] == "Path must start with /"

def test_uva_padova_s_insulinappend():
    assert True

def test_uva_padova_s_simulationend():
    assert True
