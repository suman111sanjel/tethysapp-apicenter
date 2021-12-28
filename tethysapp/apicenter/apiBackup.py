from django.http import JsonResponse, HttpResponse
import datetime as dt
import psycopg2, json,decimal, datetime, csv
from rest_framework.authentication import TokenAuthentication,SessionAuthentication
from rest_framework.decorators import api_view, authentication_classes
import scipy.stats as sp
import numpy as np
from datetime import timedelta
# from rest_framework import

def check_for_decimals(obj):
    if isinstance(obj, decimal.Decimal):
        return float(obj)
    raise TypeError

def getRecentDate(comid, cty):
    conn = psycopg2.connect(host="192.168.10.6", database="servirFlood", user="postgres", password="changeit2")
    cur = conn.cursor()
    query = 'select max(rundate) as rundate from forecast' + cty + ' where comid = ' + comid + ' order by rundate desc'

    try:
        cur.execute(query)
        a = cur.fetchall()
        bb = (str(a[0])[19:-3]).split(",")
        b = bb[0].strip() + "-" + "{:02d}".format(int(bb[1])) + "-" + "{:02d}".format(int(bb[2]))
    except:
        runDate = dt.datetime.now().date() - timedelta(1)
        b = runDate.strftime('%Y-%m-%d')

    conn.close()
    return b

# @login_required()
@api_view(['GET'])
@authentication_classes((TokenAuthentication, SessionAuthentication,))
def getFeatures(request):
    cty =request.GET.get('cty')
    country = cty + "dnetwork"
    json_obj = {}
    conn = psycopg2.connect(host="192.168.10.6", database="servirFlood", user="postgres", password="changeit2")
    cur = conn.cursor()
    query = 'select comid, risk, ST_AsGeoJSON(geom) AS geometry FROM ' + country
    cur.execute(query)
    rows = cur.fetchall()
    colnames = [desc[0] for desc in cur.description]
    geomIndex = colnames.index("geometry")

    feature_collection = {'type': 'FeatureCollection', 'features': []}
    for row in rows:
        feature = {
            'type': 'Feature',
            'geometry': json.loads(row[geomIndex]),
            'properties': {},
        }
        for index, colname in enumerate(colnames):
            if colname not in ('geometry', 'geom'):
                if isinstance(row[index], datetime.datetime):
                    value = str(row[index])
                else:
                    value = row[index]
                feature['properties'][colname] = value

        feature_collection['features'].append(feature)
    conn.close()
    json_obj["feature"] = feature_collection
    return JsonResponse(feature_collection)
    # return json.dumps(feature_collection, indent=None, default=check_for_decimals)

@api_view(['GET'])
@authentication_classes((TokenAuthentication, SessionAuthentication,))
def getreturnPeriod(request):
    comid = request.GET.get('comid')
    cty = request.GET.get('cty')
    conn = psycopg2.connect(host="192.168.10.6", database="servirFlood", user="postgres", password="changeit2")
    cur = conn.cursor()
    query = "SELECT max, two, ten, twenty FROM returnreriods" + cty + " where comid = " + str(comid)
    cur.execute(query)
    rows = cur.fetchall()
    return_max = rows[0][0]
    return_20 = rows[0][3]
    return_10 = rows[0][2]
    return_2 = rows[0][1]

    content = {
        "return_max" : return_max,
        "return_2" : return_2,
        "return_10" : return_10,
        "return_20" : return_20
    }
    return JsonResponse(content)
    # return return_max, return_2, return_10, return_20

@api_view(['GET'])
@authentication_classes((TokenAuthentication, SessionAuthentication,))
def getHistoric(request):
    comid = request.GET.get('comid')
    cty = request.GET.get('cty')
    hdates = []
    hvalues= []

    conn = psycopg2.connect(host="192.168.10.6", database="servirFlood", user="postgres", password="changeit2")
    cur = conn.cursor()
    query = "select historydate, historyvalue from history" + cty + " where comid = " + str(comid) + " order by historydate"
    cur.execute(query)
    rows = cur.fetchall()
    for row in rows:
        mydate = str(dt.datetime.strftime(row[0], '%Y-%m-%d %H:%M:%S'))
        hdates.append(mydate)
        hvalues.append(row[1])
        # print (str(row[0]) + " : " + str(row[1]))
    # return hdates,hvalues, hdates[0], hdates[-1]
    content = {
        "mydate": mydate,
        "hdates": hdates,
        "hvalues": hvalues
    }
    return JsonResponse(content)

@api_view(['GET'])
@authentication_classes((TokenAuthentication, SessionAuthentication,))
def getFlowDurationCurve(request):
    comid = request.GET.get('comid')
    cty = request.GET.get('cty')
    hdates = []
    hvalues= []
    sorted_daily_avg1 =[]
    conn = psycopg2.connect(host="192.168.10.6", database="servirFlood", user="postgres", password="changeit2")
    cur = conn.cursor()
    query = "select historydate, historyvalue from history" + cty +" where comid = " + str(comid) + " order by historydate"
    cur.execute(query)
    rows = cur.fetchall()
    for row in rows:
        mydate = str(dt.datetime.strftime(row[0], '%Y-%m-%d %H:%M:%S'))
        hdates.append(mydate)
        hvalues.append(row[1])
    sorted_daily_avg = np.sort(hvalues)[::-1]
    ranks = len(sorted_daily_avg) - sp.rankdata(sorted_daily_avg, method='average')
    # calculate probability of each rank
    prob = [100 * (ranks[i] / (len(sorted_daily_avg) + 1))
            for i in range(len(sorted_daily_avg))]
    for i in range (len(sorted_daily_avg)):
        sorted_daily_avg1.append(sorted_daily_avg[i])
    conn.close()
    content = {
        "prob": prob,
        "sorted_daily_avg1": sorted_daily_avg1
    }
    return JsonResponse(content)
    # return prob, sorted_daily_avg1

@api_view(['GET'])
@authentication_classes((TokenAuthentication, SessionAuthentication,))
def getForecast(request):
    comid = request.GET.get('comid')
    cty = request.GET.get('cty')
    runDate = request.GET.get('forecastDate')

    if runDate is None:
        # runDate = dt.datetime.now().date() - timedelta(days=0)
        runDate = getRecentDate(comid, cty)

    dates = []
    hres_dates = []
    mean_values = []
    hres_values = []
    min_values = []
    max_values = []
    std_dev_lower_values = []
    std_dev_upper_values = []
    return_obj = {}
    # print (runDate)
    conn = psycopg2.connect(host="192.168.10.6", database="servirFlood", user="postgres", password="changeit2")
    cur = conn.cursor()
    query = "SELECT forecastdate, high_res, maxval, meanval, minval, std_dev_range_lower, std_dev_range_upper FROM public.forecast" + cty + " where comid =" \
            + str(comid) + " and rundate = '" + str(runDate) + "' order by forecastdate"

    cur.execute(query)
    rows = cur.fetchall()
    for row in rows:
        hres_dates.append(str(dt.datetime.strftime(row[0],'%Y-%m-%d %H:%M:%S')))
        # hres_values.append(row[1])

        if 'nan' not in str(row[2]):
            dates.append(str(dt.datetime.strftime(row[0],'%Y-%m-%d %H:%M:%S')))
            max_values.append(float(row[2]))
            mean_values.append(float(row[3]))
            min_values.append(float(row[4]))
            std_dev_lower_values.append(row[5])
            std_dev_upper_values.append(row[6])
            hres_values.append(row[1])
    content = {
        "hres_dates": hres_dates,
        "dates": dates,
        "max_values": max_values,
        "mean_values": mean_values,
        "min_values": min_values,
        "std_dev_lower_values": std_dev_lower_values,
        "std_dev_upper_values": std_dev_upper_values,
        "hres_values": hres_values,
        "runDate": runDate
    }
    return JsonResponse(content)

@api_view(['GET'])
@authentication_classes((TokenAuthentication, SessionAuthentication,))
def getForecastCSV(request):
    comid = request.GET.get('comid')
    cty = request.GET.get('cty')
    runDate = request.GET.get('forecastDate')

    if runDate is None:
        runDate =  getRecentDate(comid, cty)  #dt.datetime.now().date() - timedelta(days=0)

    conn = psycopg2.connect(host="192.168.10.6", database="servirFlood", user="postgres", password="changeit2")
    cur = conn.cursor()
    query = "SELECT forecastdate, high_res, maxval, meanval, minval, std_dev_range_lower, std_dev_range_upper FROM public.forecast" + str(cty) + " where comid =" \
            + str(comid) + " and rundate = '" + str(runDate) + "' order by forecastdate"

    cur.execute(query)
    rows = cur.fetchall()

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="forecastData_' + str(comid) + '.csv"'
    header = ['Dates', 'hres','max','mean','min','std_dev_lower','std_dev_upper']
    writer = csv.writer(response)
    writer.writerow(header)

    for row in rows:
        hres_dates = (str(dt.datetime.strftime(row[0],'%Y-%m-%d %H:%M:%S')))
        # dates.append(str(dt.datetime.strftime(row[0],'%Y-%m-%d %H:%M:%S')))
        max_values= (float(row[2]))
        mean_values=(float(row[3]))
        min_values=(float(row[4]))
        std_dev_lower_values=(row[5])
        std_dev_upper_values=(row[6])
        hres_values=(row[1])
        writer.writerow([hres_dates,hres_values,max_values,mean_values,min_values,std_dev_lower_values,std_dev_upper_values])
    conn.close()
    return response

@api_view(['GET'])
@authentication_classes((TokenAuthentication, SessionAuthentication,))
def getreturnPeriodCSV(request):
    comid = request.GET.get('comid')
    cty = request.GET.get('cty')

    conn = psycopg2.connect(host="192.168.10.6", database="servirFlood", user="postgres", password="changeit2")
    cur = conn.cursor()
    query = "SELECT max, two, ten, twenty FROM returnreriods" + str(cty) + " where comid = " + str(comid)
    cur.execute(query)
    rows = cur.fetchall()
    return_max = rows[0][0]
    return_20 = rows[0][3]
    return_10 = rows[0][2]
    return_2 = rows[0][1]

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="retuenPeriod' + str(comid) + '.csv"'
    header = ['max', 'twenty','ten','two']
    writer = csv.writer(response)
    writer.writerow(header)
    writer.writerow([return_max, return_20, return_10, return_2])

    conn.close()
    return response

@api_view(['GET'])
@authentication_classes((TokenAuthentication, SessionAuthentication,))
def getHistoricCSV(request):
    comid = request.GET.get('comid')
    cty = request.GET.get('cty')
    hdates = []
    hvalues= []
    conn = psycopg2.connect(host="192.168.10.6", database="servirFlood", user="postgres", password="changeit2")
    cur = conn.cursor()
    query = "select historydate, historyvalue from history" + str(cty) + " where comid = " + str(comid) + " order by historydate"
    cur.execute(query)
    rows = cur.fetchall()

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="historicData_' + str(comid) + '.csv"'
    header = ['Dates', 'Values']
    writer = csv.writer(response)
    writer.writerow(header)
    for row in rows:
        mydate = str(dt.datetime.strftime(row[0], '%Y-%m-%d %H:%M:%S'))
        # hdates.append(mydate)
        # hvalues.append(row[1])
        writer.writerow([mydate, row[1]])
    conn.close()
    return response

@api_view(['GET'])
@authentication_classes((TokenAuthentication, SessionAuthentication,))
def getFlowDurationCurveCSV(request):
    comid = request.GET.get('comid')
    cty = request.GET.get('cty')
    hdates = []
    hvalues= []
    sorted_daily_avg1 =[]
    conn = psycopg2.connect(host="192.168.10.6", database="servirFlood", user="postgres", password="changeit2")
    cur = conn.cursor()
    query = "select historydate, historyvalue from history" + str(cty) + " where comid = " + str(comid) + " order by historydate"
    cur.execute(query)
    rows = cur.fetchall()
    for row in rows:
        mydate = str(dt.datetime.strftime(row[0], '%Y-%m-%d %H:%M:%S'))
        hdates.append(mydate)
        hvalues.append(row[1])
    sorted_daily_avg = np.sort(hvalues)[::-1]
    ranks = len(sorted_daily_avg) - sp.rankdata(sorted_daily_avg, method='average')
    # calculate probability of each rank
    prob = [100 * (ranks[i] / (len(sorted_daily_avg) + 1))
            for i in range(len(sorted_daily_avg))]
    for i in range (len(sorted_daily_avg)):
        sorted_daily_avg1.append(sorted_daily_avg[i])
    conn.close()
    content = {
        "prob": prob,
        "sorted_daily_avg1": sorted_daily_avg1
    }
    return JsonResponse(content)
    # return prob, sorted_daily_avg1