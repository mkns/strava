from django.shortcuts import render, redirect
import requests
import configparser
import time
import json
from datetime import date

def index(request):
    context = {}
    my_cookie = cookie(request)
    if my_cookie.get('redirect'):
        return my_cookie['redirect']
    response = render(request, "walk/index.html", context)
    response.set_cookie(key='access_token', value=my_cookie['access_token'])
    return response

def update(request):
    my_cookie = cookie(request)
    if my_cookie.get('redirect'):
        return my_cookie['redirect']

    id = request.GET.get('id', '')
    id_list = id.split(",")
    for i in id_list:
        print(i)
        update_activity(my_cookie['access_token'], i)
    response = redirect("show")
    return response

def update_activity(access_token, activity_id):
    url = "https://www.strava.com/api/v3/activities/" + str(activity_id)
    print(url)
    headers = get_standard_get_header(access_token)
    data = {'gear_id': 'g6179895'}
    requests.put(url, headers=headers, data=data).json()
    return True

def show(request):
    my_cookie = cookie(request)
    if my_cookie.get('redirect'):
        return my_cookie['redirect']
    context = get_list_of_activities(request, my_cookie['access_token'])
    return render(request, "walk/show.html", context)

def get_access_token(request, code):
    config = get_config()
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
    activities = []
    gear = {}
    wrong = []
    for page in range(1, 3):
        url = "https://www.strava.com/api/v3/athlete/activities?before=" + str(now) + "&after=" + str(past) + "&page=" + str(page) + "&per_page=200"
        print(url)
        resp = requests.get(url, headers=headers).json()
        # print(resp)
        for detail in resp:
            # merrells are g6179895
            if(detail['type'] == "Walk"): # and detail['gear_id'] == 'g4493370':
                if detail['gear_id'] not in gear:
                    gearname = get_gear(access_token, detail['gear_id'])
                    gear[detail['gear_id']] = gearname
                detail['gearname'] = gear[detail['gear_id']]
                activities.append(detail)
                if detail['gear_id'] == 'g4493370':
                    wrong.append(str(detail['id']))
    return {'activities': activities, 'wrong': ",".join( wrong )}

def get_gear(access_token, gear_id):
    url = "https://www.strava.com/api/v3/gear/" + str(gear_id)
    print(url)
    headers = get_standard_get_header(access_token)
    resp = requests.get(url, headers=headers).json()
    return resp['name']

def get_standard_get_header(code):
    headers = {
        'accept': 'application/json',
        'authorization': "Bearer " + code,
    }
    return headers

def cookie(request, activity_id=0):
    config = get_config()
    access_token = False
    code = request.GET.get('code', False)
    if code:
        access_token = get_access_token(request, code)
    else:
        if request.COOKIES.get('access_token'):
            access_token = request.COOKIES.get('access_token')    
    if not access_token:
        return {'redirect': redirect('https://www.strava.com/oauth/authorize?client_id=' + config['default']['client_id'] + '&amp;response_type=code&amp;redirect_uri=http://' + config['default']['hostname'] + '/walk/&amp;approval_prompt=force&amp;scope=read,activity:read,activity:read_all,activity:write')}
    return {'access_token': access_token}

def greatrunsolo(request):
    context = {}
    my_cookie = cookie(request)
    if my_cookie.get('redirect'):
        return my_cookie['redirect']

    now = int(time.time())
    d = date(2020, 5, 18)
    past = time.mktime(d.timetuple())

    headers = get_standard_get_header(my_cookie['access_token'])
    activities = []
    url = "https://www.strava.com/api/v3/athlete/activities?before=" + str(now) + "&after=" + str(past) + "&per_page=200"
    print(url)
    resp = requests.get(url, headers=headers).json()
    total_distance = 0
    for detail in resp:
        if(detail['type'] == "Run"):
            activities.append(detail)
            total_distance += detail['distance']
    context['activities'] = activities
    context['total_distance'] = total_distance
    return render(request, "walk/greatrunsolo.html", context)
