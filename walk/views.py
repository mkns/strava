from django.shortcuts import render
import requests
import configparser
import time

def index(request):
    context = {}
    return render(request, "walk/index.html", context)

def show(request):
    access_token = get_access_token(request)
    activities = get_list_of_activities(request, access_token)
    context = {'activities': activities}
    return render(request, "walk/show.html", context)

def get_access_token(request):
    config = get_config()
    code = request.GET.get('code', '')
    url = 'https://www.strava.com/oauth/token'
    data = {
        'client_id': config['default']['client_id'],
	    'client_secret': config['default']['client_secret'],
	    'code': code,
	    'grant_type': 'authorization_code',
    }
    responseData = requests.post(url, data).json()
    access_token = responseData['access_token']
    return access_token

def get_config():
    config = configparser.ConfigParser()
    config.read('strava.conf')
    return config

def get_list_of_activities(request, access_token):
    now = int(time.time())
    past = now - (60*60*24*365)
    headers = get_standard_get_header(access_token)
    list = []
    for page in range(1, 10):
        url = "https://www.strava.com/api/v3/athlete/activities?before=" + str(now) + "&after=" + str(past) + "&page=" + str(page) + "&per_page=200"
        print(url)
        resp = requests.get(url, headers=headers).json()
        # print(resp)
        for detail in resp:
            # print(detail)
            if(detail['type'] == "Walk") and detail['gear_id'] == 'g4493370':
                list.append(detail)
    return list

def get_standard_get_header(access_token):
    headers = {
        'accept': 'application/json',
        'authorization': "Bearer " + access_token,
    }
    return headers
