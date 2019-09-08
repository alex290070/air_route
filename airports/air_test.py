import json
from collections import deque
from pprint import pprint

from django.conf import settings
from django.core.cache import cache
from django.shortcuts import redirect, render
from django.urls import path

from urllib.parse import urlparse
import string

from django.core.validators import URLValidator
from django.core.exceptions import ValidationError


with open('airbaltic.json') as f:
    a_data=json.load(f)
with open('ryanair.json') as f:
    r_data=json.load(f)
with open('wizzair.json') as f:
    w_data=json.load(f)

if not settings.configured:
    settings.configure(
        DEBUG=True,
        ROOT_URLCONF=__name__,
        TEMPLATES=[{
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': ['']
        }]
    )

def redirect_view(request, airsrc, airdest):
    link = cache.get(airsrc, airdest)
    try:
        return redirect(link)
    except:
        return redirect(to='/')

# ===== LOAD DICT OF CITY =====
def load_airbaltic_city(file):
    tmp={}
    for k, v in file.items():
        if 'country' and 'code' in v:
            city= v['city']
            iata= v['code']
            tmp[city] = iata
            tmp[iata] = city
    return tmp

def load_ryanair_city(file):
    tmp={}
    for v in file.values():
        for i in v:
            for k, v, in i.items():
                if 'iataCode'and 'cityCode'  in k:
                    iata = i['iataCode']
                    city = i['cityCode']
                    city=city.split('_')
                    city=' '.join(city)
                    city=city.title()
                    tmp[city] = iata
                    tmp[iata] = city
    return tmp

def load_wizzair_city(file):
    tmp={}
    for i in file:
        if 'iata' and 'aliases':
            iata= i['iata']
            cityAliases=i['aliases']
            if cityAliases[0]:
                city = cityAliases[0]
                tmp[city] = iata
                tmp[iata] = city
    return tmp

# ===== LOAD DIRECTION =====
def airbaltic_direction(file):
    tmp={}
    print('airbaltic data load ...')
    for _ , v in file.items():
        if 'destinations' in v:
            c=v['code']
            d=v['destinations']
        ls=[a[0:3] for a, b in d.items()]
        tmp[c]=ls
    print(' ...done')
    return tmp

def ryanair_direction(file):
    tmp={}
    print('ryanair data load...')
    for v in file.values():
        for i in v:
            for k_v, v_v in i.items():
                if 'iataCode' in k_v:
                    c = i['iataCode']
                if 'routes' in k_v:
                    r= i['routes']
                    g= [i_r.split(':', maxsplit=1) for i_r in r]
                    y = [b.split('|')[0] for a, b in g if a == 'airport']
                    tmp[c]=y
    print(' ...done')
    return tmp

def wizzair_direction(file):
    tmp = {}
    print('wizzair data load ...')
    for i in file:
        if 'iata' and 'connections' in i:
            c=i['iata']
            r=[k['iata'] for k in i['connections']]
            tmp[c]=r
    print(' ...done')
    return tmp

# find shortest path
def find_path(graph, start, end):
    dist = {start: [start]}
    q = deque([start])
    while len(q):
        at = q.popleft()
        for next in graph[at]:
            if next not in graph:
                continue
            if next not in dist:
                dist[next] = [*dist[at], next]
                q.append(next)
    return dist[end]

def calculate_route(routes, a, b, cities):
    try:
        if a in cities and b in cities:
            start = cities[a]
            end = cities[b]
            print('start=',start, ', end=', end)
            return find_path(routes, start, end)
    except:
        print('ERROR: path not found.')
        return None

def city_route(result, cities):
    u = []
    for i in result:
        u.append(cities[i])
    return u

# LOAD DATA
try:
    a_city_dict=load_airbaltic_city(a_data)
    r_city_dict=load_ryanair_city(r_data)
    w_city_dict=load_wizzair_city(w_data)
    print('load city from json-files done.')
    # load direction from json-files (ci - direct)
    a_direct=airbaltic_direction(a_data)
    r_direct=ryanair_direction(r_data)
    w_direct=wizzair_direction(w_data)
    print('load direction from json-files done.')
except:
    print('ERROR... load data not complete.')

def index(request):
    airsrc, airdest = None, None
    cache.add(airsrc, airdest)

    airsrc = request.POST.get("airsrc")
    airdest = request.POST.get("airdest")
    try:
        airsrc= str(airsrc.title())
        airdest= str(airdest.title())
    except:
        pass
    if airsrc and airdest:
        if True: #try:
            a_result=calculate_route(a_direct, airsrc, airdest, a_city_dict)
            print('Airbaltic result = ', a_result)
            if a_result is not None:
                a_print = city_route(a_result, a_city_dict)
            else:
                a_print = ['Route not found.']
            r_result=calculate_route(r_direct, airsrc, airdest, r_city_dict)
            print('Ryanair result = ', r_result)
            if r_result is not None:
                r_print = city_route(r_result, r_city_dict)
            else:
                r_print = ['Route not found.']
            w_result=calculate_route(w_direct, airsrc, airdest, w_city_dict)
            print('Wizzair result = ', w_result)
            if w_result is not None:
                w_print = city_route(w_result, w_city_dict)
            else:
                w_print = ['Route not found.']
            return render(request, 'index.html', {'air_a': a_print , 'a':'Airbaltic: ','air_r': r_print , 'r':'Ryanair: ','air_w': w_print , 'w':'Wizzair: '})
        #except:
        #    return render(request, 'index.html', {'err':'Please enter correct name of city: '+'\"'+airsrc+'\"'+' or '+'\"'+airdest+'\"'+'.'})
    else:
        return render(request, 'index.html')

urlpatterns = [
    path('', index),
    path(r'<airsrc, airdest>', redirect_view),
]

# =======================
if __name__ == '__main__':
    import sys
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)

    '''
    #if airsrc and airdest:
    airsrc = 'SALZBURG'.title()
    airdest = 'PALMA'.title()
    if True:
        if True:
            if True: #try:

            u=[]
            if True: #try:
                for cities, direction in zip(all_cities, all_direct):
                    r_c=rewrite_code(direction, airsrc, airdest, cities)
                    print(r_c)
                    #r_c_2 = rewrite_code_2(r_c, air_ci)
                    #h=del_same_city(r_c_2)
                    #u.append(h)

'''
