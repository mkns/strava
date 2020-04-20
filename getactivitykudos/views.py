from django.shortcuts import render
from django.http import HttpResponse
import requests
import configparser
import time

def activity(request):
    access_token = get_access_token(request)  
    activity_ids = get_list_of_activity_ids(request, access_token)
    athletes = {}
    for i in range(len(activity_ids)):
        data = get_activity_kudos(activity_ids[i], access_token)
        for detail in data:
            name = detail['firstname'] + " " + detail['lastname']
            if (name not in athletes):
                athletes[name] = 0
            athletes[name]+= 1
    total = 0
    for num in athletes.values():
        total += num
    context = { 'athletes': athletes, 'total': total }
    return render(request, "getactivitykudos/index.html", context)

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

def get_activity_kudos(activity_id, access_token):
    headers = get_standard_get_header(access_token)
    url = "https://www.strava.com/api/v3/activities/" + str(activity_id) + "/kudos?per_page=100"
    return requests.get(url, headers=headers).json()

def get_standard_get_header(access_token):
    headers = {
        'accept': 'application/json',
        'authorization': "Bearer " + access_token,
    }
    return headers

def get_list_of_activity_ids(request, access_token):
    now = int(time.time())
    past = now - (60*60*24*90)
    headers = get_standard_get_header(access_token)
    url = "https://www.strava.com/api/v3/athlete/activities?before=" + str(now) + "&after=" + str(past) + "&page1=&per_page=200"
    print(url)
    resp = requests.get(url, headers=headers).json()
    print(resp)
    list = []
    for detail in resp:
        list.append(detail['id'])
    return list #['3288134900'] # list
