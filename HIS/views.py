# encoding: utf-8
# coding=utf-8
from django.shortcuts import render
from django.shortcuts import render_to_response,RequestContext, HttpResponse
from django.db import connection
from django.template import Context

import csv, time

from itertools import *

from HIS.models import SickRecord, Issue, Source
from HIS.form import SickRecordForm, IssueForm
from datetime import datetime

from django.views.decorators.csrf import csrf_protect

def new(request):
    form = SickRecordForm(data=request.POST)

    # 收案來源下拉選單
    sources = Source.objects.all().order_by('source_value')

    # 情緒問題
    issuesOpt = Issue.objects.all()

    msg = ''
    error = ''
    if request.method == 'POST':
        if form.is_valid():
            sickRecord = form.save(commit=False)
            sickRecord.source_id = request.POST.get('source')
            sickRecord.save()

            inpIss = request.POST.getlist('issues')
            for iss in inpIss:
                sickRecord.issues.add(Issue.objects.get(issue_key=iss))
            sickRecord.save()
            msg = '新增資料成功！'
            # return render_to_response("detail.html",Context({'sickRecord':sickRecord,'sources':sources, 'issuesOpt':issuesOpt, 'msg':msg, 'error':error}),context_instance=RequestContext(request))
            return render_to_response('detail.html', locals())
        else:
            message = form.errors
            print(message)
            error = message
            # return render_to_response("detail.html",Context({'sources':sources, 'issuesOpt':issuesOpt, 'msg':msg, 'error':error}),context_instance=RequestContext(request))
            return render_to_response('detail.html', locals())
    else:
        # return render_to_response("detail.html",Context({'sources':sources,'issuesOpt':issuesOpt}))
        return render_to_response('detail.html', locals())

def check(request):
    if not request.user.is_authenticated():
        return HttpResponse('')

    sickRecord = SickRecord()
    msg = ''
    if request.GET.get('sick_id'):
        sickId = request.GET.get('sick_id')
        sickTemp = SickRecord.objects.filter(sick_id=sickId).order_by('-id')
        if sickTemp:
            sickRecord.sick_id = sickId
            name = sickTemp[0].name
            id = sickTemp[0].pid
            sex = sickTemp[0].sex
            birthday = sickTemp[0].birthday
            source = sickTemp[0].source.id
            result = sickTemp[0].sick_result
            return HttpResponse('%s,%s,%s,%s,%s,%s,%s' % (sickId, name, id, sex,
                                                          birthday.strftime("%Y/%m/%d"),source, result))
        else :
            return HttpResponse('')

def queryBySql(query_string):
    cursor = connection.cursor()
    cursor.execute(query_string)
    rows = cursor.fetchall()
    # 使用字典
    # dist = {}
    # for row in rows:
    #     dist.update({row[0]:row[1]})

    return rows

def report(request):
    year = ''
    sourceInput = ''

    # 收案來源下拉選單
    sources = Source.objects.all().order_by('source_value')
    # for source in sources:
    #     print u'%s,%s' % (source.source_key,source.source_value)

    if request.method == 'POST':
        if request.POST.get('year'):
            year = request.POST['year']
        if request.POST.get('source'):
            sourceInput = request.POST['source']

        sourceSql = ''
        if sourceInput != '':
            sourceSql = 'and source_key = \'%s\'' % sourceInput

        # 篩檢人次
        timesSql = "select date_format(rec.sick_receive_date,\'%%Y/%%m\') date, count(*) " \
                   "from HIS_sickrecord rec " \
                   "where rec.sick_receive_date between \'%s/1/1\' and \'%s/12/31\' " \
                   "and exists (select 1 from HIS_source where rec.source_id = id %s) " \
                   "group by date order by rec.sick_receive_date asc " % (year, year, sourceSql)

        times = queryBySql(timesSql)

        # 篩檢人數
        countSql = "select date_format(rec.sick_receive_date,\'%%Y/%%m\') date, count(distinct sick_id) " \
                   "from HIS_sickrecord rec " \
                   "where rec.sick_receive_date between \'%s/1/1\' and \'%s/12/31\' " \
                   "and exists (select 1 from HIS_source where rec.source_id = id %s) " \
                   "group by date order by rec.sick_receive_date asc " % (year, year, sourceSql)

        count = queryBySql(countSql)

        # 探視人次
        careTimesSql = "select date_format(rec.sick_receive_date,\'%%Y/%%m\') date, count(*) " \
                   "from HIS_sickrecord rec " \
                   "where rec.sick_receive_date between \'%s/1/1\' and \'%s/12/31\' " \
                   "and exists (select 1 from HIS_source where rec.source_id = id %s) " \
                   "and rec.care_check = \'Yes\'" \
                   "group by date order by rec.sick_receive_date asc " % (year, year, sourceSql)

        careTimes = queryBySql(careTimesSql)

        # 探視人數
        careCountSql = "select date_format(rec.sick_receive_date,\'%%Y/%%m\') date, count(distinct sick_id) " \
                   "from HIS_sickrecord rec " \
                   "where rec.sick_receive_date between \'%s/1/1\' and \'%s/12/31\' " \
                   "and exists (select 1 from HIS_source where rec.source_id = id %s) " \
                   "and rec.care_check = \'Yes\'" \
                   "group by date order by rec.sick_receive_date asc " % (year, year, sourceSql)

        careCount = queryBySql(careCountSql)

        # return render_to_response("report.html",
        #                           Context({'times': times,'count':count,'careTimes':careTimes,'careCount':careCount, 'sources':sources, 'year':year, 'sourceInput':sourceInput}),
        #                           context_instance=RequestContext(request))
        return render_to_response('report.html',locals())
    else:
        # return render_to_response("report.html",
        #                           Context({'sources':sources}),
        #                           context_instance=RequestContext(request))
        return render_to_response('report.html',locals())
# @csrf_protect
def history(request):
    if request.method =='POST':
        sick_id = ''
        name = ''
        recDateSta = ''
        recDateEnd = ''
        carDateSta = ''
        carDateEnd = ''

        if request.POST.get('sick_id'):
            sick_id = 'and sick_id = \'%s\'' % request.POST.get('sick_id')

        if request.POST.get('name'):
            name = 'and name = \'%s\'' % request.POST.get('name')

        if request.POST.get('recDateSta'):
            recDateSta = 'and sick_receive_date >= \'%s\'' % request.POST.get('recDateSta')

        if request.POST.get('recDateEnd'):
            recDateEnd = 'and sick_receive_date < \'%s\'' % request.POST.get('recDateEnd')

        if request.POST.get('carDateSta'):
            carDateSta = 'and care_date >= \'%s\'' % request.POST.get('carDateSta')

        if request.POST.get('carDateEnd'):
            carDateEnd = 'and care_date < \'%s\'' % request.POST.get('carDateEnd')

        sql = 'select * from HIS_sickrecord where 1=1 %s %s %s %s %s %s ' % (sick_id, name, recDateSta, recDateEnd, carDateSta, carDateEnd)
        result = queryBySql(sql)
        # request.session['result'] = result
        # return render_to_response("history.html",
        #                           Context({'result':result,
        #                                    'sick_id':request.POST.get('sick_id'), 'name':request.POST.get('name'),
        #                                    'recDateSta':request.POST.get('recDateSta'), 'recDateEnd':request.POST.get('recDateEnd'),
        #                                    'carDateSta':request.POST.get('carDateSta'), 'carDateEnd':request.POST.get('carDateEnd')}),
        #                           context_instance=RequestContext(request))
        return render_to_response('history.html', locals())
    else:
        # result = request.session.get('result')
        # return render_to_response("history.html",
        #                           context_instance=RequestContext(request))
        return render_to_response('history.html', locals())

def delete(request):
    if request.GET.get('id'):
        delId = request.GET.get('id')
        delRec = SickRecord.objects.get(id=delId)
        delRec.delete()
        msg = '刪除資料成功!'
    # return render_to_response("history.html",
    #                               Context({'msg':msg}),
    #                               context_instance=RequestContext(request))
        return render_to_response('history.html',locals())

def edit(request):

    # 收案來源下拉選單
    sources = Source.objects.all().order_by('source_value')

    # 情緒問題
    issuesOpt = Issue.objects.all()
    inpIss = request.POST.getlist('issues')
    msg = ''
    error = ''
    if request.method == 'POST':
        editId = request.POST.get('id')
        sickRecord = SickRecord.objects.get(id=editId)
        form = SickRecordForm(data=request.POST, instance=sickRecord)
        if form.is_valid():
            sickRecord.source_id = request.POST.get('source')
            inpIss = request.POST.getlist('issues')
            sickRecord.issues.clear()
            for iss in inpIss:
                sickRecord.issues.add(Issue.objects.get(issue_key=iss))
            form.save()
            msg = '更新資料成功！！'
        else :
            message = form.errors
            print(message)
            error = message
        # return render_to_response("edit.html",
        #                           Context({'msg':msg,'error':error, 'sources':sources, 'issuesOpt':issuesOpt, 'sickRecord':sickRecord}),
        #                           context_instance=RequestContext(request))
        return render_to_response('edit.html',locals())
    else :
        editId = request.GET.get('id')
        sickRecord = SickRecord.objects.get(id=editId)
        # return render_to_response("edit.html",
        #                           Context({'sickRecord':sickRecord, 'sources':sources, 'issuesOpt':issuesOpt}),
        #                           context_instance=RequestContext(request))
        return render_to_response('edit.html',locals())

def export(request):
    response = HttpResponse(content_type='text/csv')
    if request.user.is_authenticated():
        response['Content-Disposition'] = 'attachment; filename="report.csv"'
        writer = csv.writer(response)
        writer.writerow(['收案日期','姓名','身分證字號','出身年月日','性別','病例號碼','收單來源','診斷','DT','探視','探視日期',
                         '情緒問題','晤談內容'])
        records = SickRecord.objects.all()
        for record in records :
            issueStr = ''
            for issue in record.issues.all():
                issueStr = issueStr + issue.issue_value + ','
            writer.writerow([record.sick_receive_date,record.name.encode('utf-8'), record.pid, record.birthday, record.sex.encode('utf-8'),
                             record.sick_id, record.source.source_value.encode('utf-8'), record.sick_result, record.care_dt, record.care_check,
                             record.care_date, issueStr.encode('utf-8'), record.care_content.encode('utf-8')])

    return response

def parser(request):
    i = 0
    f = open('/Users/ryan_ho/Downloads/HIS_report/all_1.csv', 'r')
    for row in csv.DictReader(f,['receiveDate','receiveSource','sickId','name','birthday','pid','sex','result','dt','emotion', 'check', 'content']):
        if i == 0:
            i = i + 1
            continue

        i = i + 1
        if row['sickId'] == '' and row['pid'] == '':
            continue

        record = SickRecord()
        record.sick_id = row['sickId']
        record.name = row['name']
        record.pid = row['pid']
        record.sex = row['sex']
        record.sick_result = row['result']
        record.care_dt = row['dt']
        record.care_check = row['check']
        record.care_content = row['content']
        # 儲存一對一資料,資料庫欄位名稱必須取名為TableName_id
        if row['receiveSource']:
            source = Source.objects.get(source_key=row['receiveSource'])
            record.source = source

        try:
            # 字串轉timestamp使用time.mktime()函數
            # time.mktime(time.strptime(row['receiveDate'] , "%Y/%m/%d %H:%M:%S"))
            # 再將時間timestamp轉字串,使用strftime

            reciveDateStr = row['receiveDate'].split('/')
            if len(reciveDateStr[0]) == 1:
                reciveDateStr[0] = '0' + reciveDateStr[0]
            if len(reciveDateStr[1]) == 1:
                reciveDateStr[1] = '0' + reciveDateStr[1]

            buffer = '20'+reciveDateStr[2]+'-'+reciveDateStr[0]+'-'+reciveDateStr[1]
            record.sick_receive_date = buffer
        except ValueError:
            print(ValueError.message)
            print('Sick ID %s receive_date error : ' % row['sickId'])

        try:
            record.birthday = datetime.fromtimestamp(time.mktime(time.strptime(row['birthday'] , "%Y%m%d"))).strftime("%Y-%m-%d")
        except ValueError:
            print(ValueError.message)
            print('Sick ID %s birthday error : ' % row['birthday'])
        # 在儲存多對多的物件前,必須要先儲存到db建立資料,之後才可以建立多對多的連結
        record.save()

        # add issue
        if row['emotion']:
            emotions = row['emotion'].split(',')
            for emotion in emotions:
                issue = Issue.objects.get(issue_key=emotion)
                record.issues.add(issue)
        record.save()
        # if i >= 3:
        #     break

    return render_to_response("detail.html",locals())