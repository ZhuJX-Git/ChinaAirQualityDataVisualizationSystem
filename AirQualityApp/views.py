from django.shortcuts import render
from django.db import connection, transaction
from django.views.decorators.csrf import csrf_exempt
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

@csrf_exempt
def logincheckcontroller(request):
    inputUsesrname = request.POST['inputUsername']
    inputPassword = request.POST['inputPassword']
    cursor = connection.cursor()
    cursor.execute(
        'SELECT * FROM "Users" WHERE "username" = %s AND "password" = %s',
        [inputUsesrname, inputPassword]
    )
    fetchResult = cursor.fetchone()
    if fetchResult == None:
        messages.error(request, 'Incorrect username or password')
        return redirect('/login/')
    else:
        return redirect('/home/')

@csrf_exempt
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
    value = [111, 121.6, 122, 116, 123.3, 110.4, 118.4, 116.8, 114.3,
             113.2, 111.8, 116.8, 113.4, 113, 121.3, 118.7, 119, 117.6, 113.8,
             115.1, 114.1, 115.2, 112.6, 114.8, 120.2, 118.2, 119.8, 114.7, 115.4,
             114.6, 112.7]
    attr = ['甘肃', '广东', '广西', '贵州', '海南',
            '河南', '湖北', '湖南', '宁夏', '青海',
            '陕西', '四川', '西藏', '新疆', '云南',
            '重庆', '北京', '天津', '河北', '山西', '内蒙古',
            '辽宁', '吉林', '黑龙江', '上海', '江苏', '浙江', '安徽', '福建'
        , '江西', '山东']
    sequence = list(zip(attr, value))

    map = (Map()
           .add(2020, sequence, "china",)
           # .set_global_opts(title_opts = opts.TitleOpts(title = 'Map'), visualmap_opts = opts.VisualMapOpts(max_ = 130, min_ = 95),)
           .set_global_opts(title_opts=opts.TitleOpts(title='Map'))

           )
    map.render(path = './templates/test.html')
    # return render(request, map.render_embed())
    return HttpResponse(map.render_embed())

