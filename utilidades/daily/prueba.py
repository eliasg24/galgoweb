from datetime import date
import requests

url = "http://www.aetoweb.com/utilidades/DailyDataTendencias"

payload={}
headers = {
}

response = requests.request("GET", url, headers=headers, data=payload)

print(response.text)



url = "http://www.aetoweb.com/utilidades/DailyDataTendenciasAplicaciones"

payload={}
headers = {
}

response = requests.request("GET", url, headers=headers, data=payload)

print(response.text)



url = "http://www.aetoweb.com/utilidades/DailyDataTendenciasUbicaciones"

payload={}
headers = {
}

response = requests.request("GET", url, headers=headers, data=payload)

print(response.text)




url = "http://www.aetoweb.com/utilidades/DailyDataTendenciasCompanias"

payload={}
headers = {
}

response = requests.request("GET", url, headers=headers, data=payload)

print(response.text)




hoy = date.today()

if hoy.day == 28:

    url = "http://www.aetoweb.com/utilidades/MonthDataRendimiento"

    payload={}
    headers = {
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    print(response.text)