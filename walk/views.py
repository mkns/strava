from django.shortcuts import render
import requests
import configparser
import time

def index(request):
    context = {}
    return render(request, "walk/index.html", context)

def prepupdate(request):
    return render(request, "walk/prepupdate.html")

def update(request):
    access_token = get_access_token(request)
    id = request.GET.get('id', '')
    id_list = id.split(",")
    for i in id_list:
        print(i)
        update_activity(access_token, i)
    context = {}
    return render(request, "walk/show.html", context)

def update_activity(access_token, activity_id):
    url = "https://www.strava.com/api/v3/activities/" + str(activity_id)
    print(url)
    headers = get_standard_get_header(access_token)
    data = {'gear_id': 'g6179895'}
    resp = requests.put(url, headers=headers, data=data).json()
    print(resp)

    return ""

def show(request):
    access_token = get_access_token(request)
    context = get_list_of_activities(request, access_token)
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
    activities = []
    gear = {}
    wrong = []
    for page in range(1, 5):
        url = "https://www.strava.com/api/v3/athlete/activities?before=" + str(now) + "&after=" + str(past) + "&page=" + str(page) + "&per_page=200"
        print(url)
        resp = requests.get(url, headers=headers).json()
        # print(resp)
        for detail in resp:

            # print(detail)
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
    print(resp)
    return resp['name']

def get_standard_get_header(access_token):
    headers = {
        'accept': 'application/json',
        'authorization': "Bearer " + access_token,
    }
    return headers
