from django.shortcuts import render
from django.db import connection, transaction
from django.contrib import messages
from django.shortcuts import redirect
from pyecharts.charts import Map, Timeline
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
    cursor = connection.cursor()
    # 第一步得到时间跨度，即minYear和maxYear
    cursor.execute(
        'SELECT MIN("Date") AS "Min", MAX("Date") AS "Max" '
        'FROM "Data"'
    )
    fetchResult = cursor.fetchone();
    minYear, maxYear = int(fetchResult[0][0:4]), int(fetchResult[1][0:4]) # 上一步得到的结果格式为'YYYYMMDD'，因此需要将年份提取出来并转换为int
    # 新建一个Timeline格式的图表
    timeLine = Timeline()
    # 接下来需要创建每一年的Map格式的图表，添加到Timeline中
    for year in range(minYear, maxYear + 1):
        curYear = str(year) + '%'
        # 执行原生SQL查询，最终得到的结果是当前年份的每个省份的平均AQI指数
        # 具体的查询逻辑：1）首先在Data表中筛选出当前年份的所有的AQI数据，然后按照监测站点进行分组，计算每个分组的平均AQI指数，也就是每个站点一年的平均值 2）结合Monitors表，根据每个站点所在的城市，就可以汇总计算出每个城市的年平均AQI指数
        # 3）最后再结合省份信息，汇总计算出每个省的年平均AQI指数
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
            [curYear, 'AQI']
        )
        fetchResult = cursor.fetchall()
        # 利用上述查询的数据创建一个Map格式的图表，具体的参数参考pyecharts的官网，在上面给出了详细的参数介绍
        map = (Map()
               .add('AQI', fetchResult, "china", is_roam=False, zoom=1)
               .set_global_opts(title_opts=opts.TitleOpts(title = "{}年全国空气质量指数".format(year)), visualmap_opts=opts.VisualMapOpts(max_= 120, min_= 30),)
               )
        # 最后将每个Map加入到Timeline中，生成带有时间轴的地图
        timeLine.add(map, "{}年".format(year))
    return HttpResponse(timeLine.render_embed()) # 这一步没有返回具体的html网页，而是通过调用render_embed()方法，将生成的html格式的Timeline图表显示在当前的url下



