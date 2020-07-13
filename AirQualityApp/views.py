from django.shortcuts import render
from django.db import connection, transaction
from django.contrib import messages
from django.shortcuts import redirect
from pyecharts.charts import Geo, Map
from pyecharts import options as opts
from django.http import HttpResponse

# Create your views here.
def entrypagecontroller(request):
    return render(request, 'EntryPage.html')

def loginpagecontroller(request):
    return render(request, 'LoginPage.html')

def registerpagecontroller(request):
    return render(request, 'RegisterPage.html')

def logincheckcontroller(request):
    inputUsesrname = request.POST['inputUsername']
    inputPassword = request.POST['inputPassword']
    cursor = connection.cursor()
    cursor.execute(
        'SELECT * FROM "Users" WHERE "username" = %s AND "password" = %s',
        [inputUsesrname, inputPassword]
    )
    fetchResult = cursor.fetchone()
    if fetchResult is None:
        messages.error(request, 'Incorrect username or password')
        return redirect('/login/')
    else:
        return redirect('/home/')

def registercheckcontroller(request):
    inputUsername = request.POST['inputUsername']
    inputPassword = request.POST['inputPassword']
    cursor = connection.cursor()
    cursor.execute(
        'SELECT * FROM "Users" WHERE "username" = %s',
        [inputUsername]
    )
    fetchResult = cursor.fetchone()
    if fetchResult:
        messages.error(request, 'User already exists, please try another username')
        return redirect('/register')
    cursor.execute(
        'INSERT INTO "Users" VALUES (%s, %s)',
        [inputUsername, inputPassword]
    )
    transaction.commit()
    return redirect('/entry')

def homepagecontroller(request):
    year = str(2019) + '%'
    cursor = connection.cursor()
    cursor.execute(
        'SELECT "Provinces"."name" AS "Province", AVG(tmpres1."Value") AS "Value" '
        'FROM "Cities", "Provinces", '
        '(SELECT "Monitors"."City", AVG(tmpres0."Value") AS "Value" '
        'FROM "Monitors", '
        '(SELECT "Monitor" AS "ID", AVG("Value") AS "Value" '
        'FROM "Data" '
        'WHERE "Date" LIKE %s AND "Type" = %s '
        'GROUP BY "Monitor") tmpres0 '
        'WHERE "Monitors"."ID" = tmpres0."ID" '
        'GROUP BY "Monitors"."City") tmpres1 '
        'WHERE "Cities"."province" = "Provinces"."province" AND "Cities"."name" = tmpres1."City" '
        'GROUP BY "Provinces"."name"',
        [year, 'AQI']
    )
    fetchResult = cursor.fetchall()
    unzip = zip(*fetchResult)
    o1, o2 = list(unzip)
    map = (Map()
           .add(2020, fetchResult, "china", is_roam = False, zoom = 1.2)
           .set_global_opts(title_opts = opts.TitleOpts(title = 'Map'), visualmap_opts = opts.VisualMapOpts(max_ = max(o2), min_ = min(o2)),)
           )
    return HttpResponse(map.render_embed())

