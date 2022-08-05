import requests

url = "http://www.aetoweb.com/utilidades/DailyDataTendencias"

payload={}
headers = {
}

response = requests.request("GET", url, headers=headers, data=payload)

print(response.text)