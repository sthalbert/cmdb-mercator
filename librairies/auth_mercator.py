import requests

def header_mercator():
    vheaders = {}
    vheaders['accept'] = 'application/json'
    vheaders['content-type'] = 'application/x-www-form-urlencoded'
    vheaders['cache-control'] = 'no-cache'

    auth = requests.post("http://127.0.0.1:8080/api/login",
                         headers=vheaders,
                         data= {'email':'admin@admin.com', 'password':'password'} )

    header = {}
    header['Content-Type'] = 'application/json'
    header['Authorization'] = "Bearer " + auth.json()['access_token']

    return header