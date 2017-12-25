# coding=utf-8
import codecs
import requests
import re
import math
import transform
cooE = ['121.46858093012334', '31.231549504632518']

# 调用百度地api
def search_bd(keywords):
    #http://api.map.baidu.com/geocoder/v2/?address=北京市海淀区上地十街10号&output=json&ak=您的ak&callback=showLocation
    text=''
    if keywords=='':
        print ('invalid address')
        return ''
    try:
        apiKey = '9Rcrs3WWnGeIjaGzlbAQHq3SM5I2h7do'
        while(text==''):
            url = 'http://api.map.baidu.com/geocoder/v2/?address=' + keywords + '&output=json&ak=' + apiKey + '&callback=showLocation'
            try:
                rep = requests.get(url)
            except:
                pass
            text = rep.text
    except:
        print ('search_bd error')
        pass
    return text

#正则表达式获取地址经纬度
def get_lng_lat(text):
    rap = []
    try:
        pattern = re.compile(r'.*?lng":(.*?),"lat":(.*?)}.*?')
        match = pattern.match(text)
        if match:
            group = match.group(1,2)
            lng = float(group[0])
            lat = float(group[1])
            rap = transform.bd09_to_wgs84(lng,lat)
            return rap
    except:
        print('Get lng and lat error!')
        pass

#将经纬度放入列表rat中
def getcoo(group):
    ret = []
    try:
        ret.append(group[0])
        ret.append(group[1])
    except:
        print ('getcoo error')
        pass
    return ret

#利用经纬度计算两地址的距离
def dist(group1,group2):  # 经度1，纬度1，经度2，纬度2 （十进制度数）
    from math import radians, cos, sin, asin, sqrt
    #向元组中读取两个地址的经纬度
    lon1 = float(group1[0])
    lat1 = float(group1[1])
    lon2 = float(group2[0])
    lat2 = float(group2[1])
    # 将十进制度数转化为弧度
    # math.degrees(x):为弧度转换为角度
    # math.radians(x):为角度转换为弧度
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    # haversine公式
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin( dlat /2 ) **2 + cos(lat1) * cos(lat2) * sin( dlon /2 ) **2
    c = 2 * asin(sqrt(a))
    r = 6371 # 地球平均半径，单位为公里
    return c * r

def func():
    try:
        f = codecs.open('read.txt', 'r', 'utf-8')
        f2 = codecs.open('results.txt', 'w','utf-8')
    except:
        print('fileopen fail')
        return
    try:
        text = f.read()
        f.close()
        spText = text.splitlines()
        tup = (2,3,8)# tuple(C, D, I)
        cnt=0
        for row in spText:
            print(row)
            cnt+=1
            t = row.split('\t') #通过指定分隔符对字符串进行切片，并返回分割后的字符串列表（list），默认分隔符为空格
            if(t[2]=='' or t[3]=='' or (t[7]=='' and t[8]=='')):
                f2.write(str(cnt) + '\t' +'\n')
                continue
            #print t[2]+' '+t[3]+' '+t[8]#CDEI-2348
            ret = []
            for i in tup:
                repText = search_bd(t[i])#调用百度api函数
                try:
                    group = get_lng_lat(repText)#得到经纬度，以[lon，lat]元组的形式返回
                except:
                    print ('coomatch_bd error')
                    if i==8:#if error while search I(t[8], community address), then search H(t[7], community name)
                        sign=0
                        try:
                            repText = search_bd(t[7])
                            print(t[7])
                            group = get_lng_lat(repText)
                        except:
                            print('tried, but error again')
                            sign=1
                            pass
                        if sign==0:print('tried again, and correct')
                    pass
                ret.append(t[i])#append the community address we searched
                if(group):#if origin data have been processed
                    coo = getcoo(group)
                    ret.append(coo[0])#append lng
                    ret.append(coo[1])#append lat
                else:
                    ret.append('None')
                    ret.append('None')
                    ret.append('None')
                if i == 2:
                    if(group): cooC = coo#if origin data have been processed
                    else:cooC = None
                elif i == 3:
                    if (group):cooD = coo
                    else:cooD = None
                else:
                    if (group):cooI = coo
                    else:cooI = None
            # compute distance of CI, DI, EI
            if(cooC and cooI):
                ret.append(str(dist(cooC, cooI)))#compute the distance between C and I
            else:
                ret.append(None)
            if (cooD and cooI):
                ret.append(str(dist(cooD, cooI)))
            else:
                ret.append(None)
            if (cooE and cooI):
                ret.append(str(dist(cooE, cooI)))
            else:
                ret.append(None)

            # ret = [originAddress, foundAddress, longitude, latitude, distance, CI, DI, EI], size = 8
            # print ret + '\n'
            wline = ''#initialize the string we'll write to file (just one line)
            try:
                for content in ret:
                    wline += ('' if wline == '' else '\t') + (content if content else 'None')
                f2.write(str(cnt) + '\t' + wline + '\n')
            except:
                print ('writefile error')

        f2.close()
    except:
        print ('readfile error')
        pass


if __name__ == '__main__':
    func()
