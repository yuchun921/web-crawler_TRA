import requests
from bs4 import BeautifulSoup
import time

url = "https://tip.railway.gov.tw/tra-tip-web/tip"
stat = {}  # 存火車站名和火車站代碼
today = time.strftime('%Y/%m/%d')
stime = "06:00"  # 起始時間
etime = "12:00"  # 結束時間


def getTrip():  # 爬蟲動作會在內執行
    req = requests.get(url)
    if req.status_code != 200:  # 確認回傳代碼是否成功
        print("url發生錯誤"+url)
        return

    soup = BeautifulSoup(req.text, "html5lib")  # 將HTML解析取得bs4物件，透過解析後的物件擷取資料
    # 取得車站名稱和代碼
    stations = soup.find(id="cityHot").find("ul").find_all("li")
    for station in stations:  # for將車站名跟代碼取出
        satname = station.find("button").text
        satid = station.find("button")['title']  # 使用[ ]取得屬性值
        stat[satname] = satid  # 將車站名稱放在字典變數的key，代碼放在value

    # 取得csrf代碼，要跟表單一起傳送
    csrf = soup.find(id="queryForm").find("input", {"name": "_csrf"})["value"]

    # 回傳的表單是字典型態變數
    formdata = {
        # 固定資料，可以直接寫死
        "trainTypeList": "ALL",
        "transfer": "ONE",
        "startOrEndTime": "true",
        # 非固定資料，放入上面設的變數
        "startStation": stat["臺北"],  # 剛才建立好的stat字典尋找起站，站名寫在字典key值位置
        "endStation": stat["新竹"],  # 剛才建立好的stat字典尋找迄站，站名寫在字典key值位置
        "rideDate": today,  # 搜尋的日期
        "startTime": stime,  # 搜尋的起始時間
        "endTime": etime  # 搜尋的結束時間
    }
    # 找到傳送表單的網址
    queryUrl = soup.find(id="queryForm")["action"]

    # 可以傳送表單給臺鐵主機了
    # 使用函式 POST(網址,表單資訊)
    # 傳送表單查詢車次的網址(和get(url)不同)
    qReq = requests.post("https://tip.railway.gov.tw"+queryUrl, data=formdata)

    # 一樣用bs4解析物件
    qSoup = BeautifulSoup(qReq.text, "html5lib")

    # 回傳的車次清單放在tag <tr class="trip-column">中
    trs = qSoup.find_all("tr", "trip-column")  # find_all找到每一列車次資料
    print(today, stime, "~", etime, stat["臺北"], "至", stat["新竹"], "的車次")
    for tr in trs:  # 用for取出車次資料
        td = tr.find_all("td")  # 多個tag <td>包在<tr>中，因此用find_all找出所有<tr>
        # 列印出格式依序為 車重車次、出發時間、抵達時間 的內容
        # 車種車次在第一個<td>，索引值=0，其內容在子標籤ul、li、a中，用.text取得字串
        print("%s : %s, %s" % (td[0].ul.li.a.text, td[1].text, td[2].text))


# 呼叫函式
getTrip()
