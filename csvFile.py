# encoding: utf-8
import csv

def getReceiveSource():
    tmp = []
    for row in csv.DictReader(f,['receiveDate','receiveSource','sickId','name','birthday','pid','sex','result','dt','emotion', 'check', 'content']):
        source = row['receiveSource']
        if not tmp.__contains__(source):
            tmp.append(source)
    f.close()

    for t in tmp:
        print(t)

def getEmotion():
    tmp = []
    for row in csv.DictReader(f,['receiveDate','receiveSource','sickId','name','birthday','pid','sex','result','dt','emotion', 'check', 'content']):
        # parser emotion
        if row['emotion'] == '':
            continue

        emotions = row['emotion'].split(',')
        for emotion in emotions:
            if not tmp.__contains__(emotion):
                tmp.append(emotion)
        # if row['sickId'] == '' and row['pid'] == '':
        #     continue
    f.close()

    for t in tmp:
        print(t)


# Main
f = open('/Users/ryan_ho/Downloads/HIS_report/20141231.csv', 'r')
# 查看收案來源非重複的選項
getReceiveSource()

# 查看情緒問題非重複的選項
# getEmotion()