from django.shortcuts import render, redirect
import requests
import configparser
import time
import json
import ast
from datetime import date, datetime

def index(request):
    context = {}

    # Check for code - if we got it, get an token and hold it for now
    # If no code, check for cookie - if we got one, check it hasn't expired, and hold it
    # If cookie has expired, refresh it, and get a new token
    # If none of those, redirect to Strava authorization page
    # Still here? We have an token, so check it works by hitting the Athlete page
    # If that is successful, store it in a cookie and send them to the index page
    config = get_config()
    token = False
    code = request.GET.get('code', False)
    if code:
        token = get_token(request, code, "access")
    else:
        if request.COOKIES.get('token'):
            token = ast.literal_eval(request.COOKIES.get('token'))
            if token['expires_at'] < time.time():
                token = get_token(request, token['refresh_token'], "refresh")
        else:
            return redirect('https://www.strava.com/oauth/authorize?client_id=' + config['default']['client_id'] + '&amp;response_type=code&amp;redirect_uri=http://' + config['default']['hostname'] + '/walk/&amp;approval_prompt=force&amp;scope=read,activity:read,activity:read_all,activity:write')

    # TODO: check the token actually works

    response = render(request, "walk/index.html", context)
    response.set_cookie(key='token', value=token)
    return response

def update(request):
    access_token = get_access_token(request)

    id = request.GET.get('id', '')
    id_list = id.split(",")
    for i in id_list:
        print(i)
        update_activity(access_token, i)
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
    access_token = get_access_token(request)
    context = get_list_of_activities(request, access_token)
    return render(request, "walk/show.html", context)

def get_access_token(request):
    return ast.literal_eval(request.COOKIES.get('token')).get('access_token')

def get_token(request, code, type):
    config = get_config()
    url = 'https://www.strava.com/oauth/token'
    data = {
        'client_id': config['default']['client_id'],
	    'client_secret': config['default']['client_secret'],
    }
    if type == 'refresh':
        data['grant_type'] = 'refresh_token'
        data['refresh_token'] = code
    else:
        data['grant_type'] = 'authorization_code'
        data['code'] = code
    print(data)
    response_data = requests.post(url, data).json()
    print(response_data)
    return response_data

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
        response = requests.get(url, headers=headers)
        if (response.status_code != 200):
            return redirect("./")
        responseData = response.json()
        for detail in responseData:
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

def greatrunsolo(request):
    context = {}
    access_token = get_access_token(request)

    now = int(time.time())
    d = date(2020, 5, 18)
    past = time.mktime(d.timetuple())

    headers = get_standard_get_header(access_token)
    activities = []
    url = "https://www.strava.com/api/v3/athlete/activities?before=" + str(now) + "&after=" + str(past) + "&per_page=200"
    print(url)
    response = requests.get(url, headers=headers)
    if (response.status_code != 200):
        return redirect("./")

    responseData = response.json()
    total_distance = 0
    for detail in responseData:
        if(detail['type'] == "Run"):
            detail['nicedate'] = datetime.fromisoformat(detail['start_date_local'][:-1]).strftime("%b %d %Y %H:%M:%S") # for some reason i have to hack off the Z
            format_distance(detail)
            activities.append(detail)
            total_distance += detail['distance']
    context['activities'] = activities
    context['total_distance'] = '{:.2f}'.format(total_distance/1000)
    return render(request, "walk/greatrunsolo.html", context)

def runs(request):
    context = {}
    access_token = get_access_token(request)

    now = int(time.time())
    d = date(2020, 1, 1)
    past = time.mktime(d.timetuple())

    headers = get_standard_get_header(access_token)
    activities = []
    url = "https://www.strava.com/api/v3/athlete/activities?before=" + str(now) + "&after=" + str(past) + "&per_page=200"
    print(url)
    response = requests.get(url, headers=headers)
    if (response.status_code != 200):
        return redirect("./")

    responseData = response.json()
    total_distance = 0
    for detail in responseData:
        if(detail['type'] == "Run"):
            detail['nicedate'] = datetime.fromisoformat(detail['start_date_local'][:-1]).strftime("%b %d %Y %H:%M:%S") # for some reason i have to hack off the Z
            format_distance(detail)
            activities.append(detail)
            total_distance += detail['distance']
    context['activities'] = activities
    context['total_distance'] = '{:.2f}'.format(total_distance/1000)
    return render(request, "walk/runs.html", context)

def private(request):
    context = {}
    access_token = get_access_token(request)

    now = int(time.time())
    d = date(2020, 1, 1)
    past = time.mktime(d.timetuple())

    headers = get_standard_get_header(access_token)
    activities = []
    url = "https://www.strava.com/api/v3/athlete/activities?before=" + str(now) + "&after=" + str(past) + "&per_page=200"
    print(url)
    response = requests.get(url, headers=headers)
    if (response.status_code != 200):
        return redirect("./")

    responseData = response.json()
    total_distance = 0
    for detail in responseData:
        if(detail['private'] == True):
            detail['nicedate'] = datetime.fromisoformat(detail['start_date_local'][:-1]).strftime("%b %d %Y %H:%M:%S") # for some reason i have to hack off the Z
            format_distance(detail)
            activities.append(detail)
            total_distance += detail['distance']
    context['activities'] = activities
    context['total_distance'] = '{:.2f}'.format(total_distance/1000)
    return render(request, "walk/private.html", context)


def format_distance(detail):
    distance = float(format(detail['distance'])) / 1000
    detail['nicedistance'] = '{:.2f}'.format(distance)

def is_response_valid(response):
    if response.get('errors'):
        return False
    return True
