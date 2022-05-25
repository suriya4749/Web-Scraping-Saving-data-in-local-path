__author__ = 'suriyakumar.s2'

# Import Functions
from datetime import datetime
from datetime import date
import requests, json, sys, urlparse as up,uuid,pandas as pd,csv,random,yaml,demjson,re
from operator import itemgetter
from common_files.common_code import *
from common_files.custom_functions import *
reload(sys)
sys.setdefaultencoding('UTF-8')


# Main Class

class flooranddecor_product_page():

    # Data Extractor Function

    def data_extractor(self, soup, url_meta_data):
        dataList, dataDict, input_data, hit_url,store_list = [], {}, json.loads(url_meta_data.get('totalInput')), url_meta_data.get('url', 'n/a'),[]
        dataDict['unique_id'] = str(url_meta_data.get('unique_idn', 'n/a'))
        dataDict['zip_input'] = str(url_meta_data.get('zipcode_id', 'n/a'))
        dataDict['store_input'] = str(url_meta_data.get('store_id', 'n/a'))
        dataDict['pro_url'] = hit_url
        dataDict['category_path'] = '#||#'.join([values.text.strip() for id, values in enumerate(soup.select('.b-breadcrumbs span')) if id != 0]) if soup.select('.b-breadcrumbs span') else 'n/a'
        dataDict['product_id'] = soup.select('.b-pdp_details-element_value')[0].text.strip() if soup.select('.b-pdp_details-element_value') else 'n/a' + '_' + input_data[0].get('uniqueIdentifier')
        dataDict['product_id_site'] = soup.select('.b-pdp_details-element_value')[0].text.strip() if soup.select('.b-pdp_details-element_value') else 'n/a'
        try:dataDict['product_dimensions'] = soup.select('.b-pdp_details-element_value')[1].text.strip() if soup.select('.b-pdp_details-element_value') else 'n/a'
        except:pass
        dataDict['product_name'] = soup.select('.b-pdp_title-name')[0].text.strip() if soup.select('.b-pdp_title-name') else 'n/a'
        # dataDict['product_description'] = soup.select('.b-pdp_specifications-txt')[0].text.strip() if soup.select('.b-pdp_specifications-txt') else 'n/a'
        dataDict['product_image'] = soup.select('a.b-pdp_thumbnail-item')[0].get('href') if soup.select('a.b-pdp_thumbnail-item') else 'n/a'
        dataDict['image_url_large'] = soup.select('a.b-pdp_thumbnail-item')[0].get('href') if soup.select('a.b-pdp_thumbnail-item') else 'n/a'
        dataDict['image_url_small'] = soup.select('a.b-pdp_thumbnail-item')[0].get('href') if soup.select('a.b-pdp_thumbnail-item') else 'n/a'
        try:
            price = soup.select('.b-pdp_price-cost')[0].text.strip()
            dataDict['price'] = re.sub('[A-Za-z]','',str(price)).replace(' /','').replace('$','')
            try:dataDict['anc_text'] = soup.select('.b-pdp_price-cost_unit')[0].text.strip().replace('/ ','')
            except:dataDict['anc_text'] = 'pieces'
            dataDict['lead_time'] = re.sub('days.*','days',remove_meta_char(soup.select('.b-pdp_delivery-desc.m-show')[1].text.strip()))
        except:pass
        try:dataDict['shipping_areas'] =soup.select('.m-available')[0].text.strip() if soup.select('.m-available') else 'n/a'
        except:pass
        try:dataDict['presence_of_upsell'] = soup.select('.b-pdp_details-element_value')[1].text.strip() if soup.select('.b-pdp_details-element_value') else 'n/a'
        except:pass
        try:
            list1 = []
            for one in soup.select('section.b-pdp_specifications-container article.b-pdp_specifications-item'):
                value = remove_meta_char(one.select('span.b-pdp_specifications-number')[0].text.strip()).encode('ascii','ignore').decode()
                list1.append(value)
            dataDict['features'] = '#||#'.join(list1)
        except:pass
        try:dataDict['price_promo'] = soup.select('.b-pdp_calc-field_cost')[0].text.strip() if soup.select('.b-pdp_calc-field_cost') else 'n/a'
        except:pass
        dataDict['brand'] = soup.select('.b-pdp_title-brand img')[0].get('alt') if soup.select('.b-pdp_title-brand img') else 'n/a'
        td_List = []
        if soup.select('.b-pdp_specifications-inner'):
            for i in soup.select('.b-pdp_specifications-inner section.b-pdp_specifications-container article.b-pdp_specifications-item'):
                if i.select('.b-pdp_specifications-name') and i.select('.b-pdp_specifications-number'):
                    tdData = remove_meta_char(i.select('.b-pdp_specifications-name')[0].text) + ':' + remove_meta_char(i.select('.b-pdp_specifications-number')[0].text)
                    td_List.append(tdData)
            dataDict['technical_details'] = '#||#'.join(td_List)
        if len(dataDict) > 0: dataList.append(dataDict)
        store_list = self.storeValidator(soup,url_meta_data)
        if store_list: dataList += store_list
        return dataList

    def storeValidator(self,soup,url_meta_data):
        dataList = []
        dataDict = {}
        myuuid = uuid.uuid4()
        myuuid_v1 = uuid.uuid1()
        cookie = '__pxvid=' + str(myuuid_v1) + '; _pxvid=' + str(myuuid) + ';'
        header = {"cookie": cookie, "authority": "www.flooranddecor.com", "method": "GET", "scheme": "https",
                  "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                  "accept-encoding": "gzip, deflate, br", "accept-language": "en-US,en;q=0.9",
                  "cache-control": "max-age=0", "sec-ch-ua-mobile": "?0", "sec-ch-ua-platform": "Windows",
                  "sec-fetch-dest": "document", "sec-fetch-mode": "navigate", "sec-fetch-site": "none",
                  "sec-fetch-user": "?1", "upgrade-insecure-requests": "1",
                  "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36 Edg/95.0.1020.44"}
        zipCode = str(url_meta_data.get('zipcode_id', 'n/a'))
        prodId = soup.select('.b-pdp_details-element_value')[0].text.strip()
        payload = '{"zipCode":"' + str(zipCode) + '","usedQuantity":0,"method":"getStoresAvailability","productID":"' + prodId + '","ajax":true}'
        try:achText = soup.select('.b-pdp_price-cost_unit')[0].text.strip().replace('/ ', '')
        except:achText = 'pieces'
        storeUrl = 'https://www.flooranddecor.com/on/demandware.store/Sites-floor-decor-Site/default/Product-Service#' + str(url_meta_data.get('uniqueIdentifier', 'n/a')) + '&anch=' + achText
        payloadParam = str(payload)
        response = requests.post(storeUrl, headers=header, data=payloadParam, verify=False).text
        store_name = str(url_meta_data.get('storeName', 'n/a'))
        dataDict['anchor_text'] = ancTxt = re.findall('anch=.*', str(storeUrl))[0].replace('anch=', '')
        if 'ft' == ancTxt:
            ancTxt = 'feet'
        if 'sqft' == ancTxt:
            ancTxt = 'boxes'
        dataDict['stock_sta'] = '0' + ' ' + str(ancTxt) + ' in ' + str(store_name)
        try:
            storeJson = json.loads(response)
            storeChunk = storeJson['storesData']
            inpZip = str(url_meta_data.get('zipcode_id', 'n/a'))
            for i in storeChunk:
                dataDict = {}
                if i.has_key('store'):
                    siteZip = i['store']
                    if siteZip.has_key('address'):
                        storeAddress = siteZip['address']
                        if inpZip in str(storeAddress):
                            quantity = i['atcQuantity']
                            storeName = i['store']['name']
                            dataDict['stock_status'] = str(quantity) + ' ' + str(ancTxt) + ' in ' + str(storeName)
        except:pass
        if len(dataDict) > 0: dataList.append(dataDict)
        return dataList

# Parse Function

def parse(html_source, attribute_list, url_meta_data):
    soup = BeautifulSoup(html_source)
    flooranddecor_product_page_object = flooranddecor_product_page()
    output = flooranddecor_product_page_object.data_extractor(soup, url_meta_data)
    x = re.sub("u'","'",str(output)).replace("'",'"')
    print x
    df = pd.read_json(x)
    TodayDate = date.today()
    ranNum = random.randint(111111, 999999)
    df.to_csv(r"C:\Users\suriyakumar.s2\Downloads\Flooranddecor_Output\Output_Flooranddecor_PDP_" + str(TodayDate) +'_' + str(ranNum) + ".csv" , encoding='utf-8', index=False,sep=',')
    return [url_meta_data, df]


# Main Function
#
if __name__ == '__main__':
    ### Main URL
    tsv_data = pd.read_csv(r"C:\Users\suriyakumar.s2\Downloads\Testing_Fnd_Input.tsv", sep='\t')
    MainUrl = (tsv_data['url'])
    StoreId = (tsv_data['storeid_input'])
    Zipcode = (tsv_data['zipcode_input'])
    uniqueid = (tsv_data['uniqueIdentifier'])
    sto_name = (tsv_data['store_name'])
    for Url,StoId,ZipId,Unid,stoName in zip(MainUrl,StoreId,Zipcode,uniqueid,sto_name):
        InputUrl =  Url
        url = InputUrl
        url_meta_data = {"store_id":StoId,"zipcode_id":ZipId,"unique_idn":Unid,"storeName":stoName,"type":"product_page","url":InputUrl,"domain":"sephora_fr","volatility":0,"lastCrawlTime":0,"uniqueLastCrawlTime":0,"pageDepth":["product_page","variation","review_rate"],"requestMetaData":{"webMethod":"get","allowRedirect":"True","verify":"False"},"gatewayType":"PYTHONREQUEST","validateParsedOutput":"False","uniqueIdentifier":"633","totalInput":"[{\"Input_Category\":\"Face\",\"color\":\"n/a\",\"brand_Input\":\"Lancome\",\"type\":\"product_page\",\"scope_name\":\"PNC\",\"gatewayType\":\"PYTHONREQUEST\",\"brand_group\":\"Competitor\",\"fetchNextCrawlUrl\":\"TRUE\",\"mainurl\":\"n/a\",\"Sub_category\":\"Cheek\",\"pageDepth\":\"product_page,variation,review_rate\",\"uniqueIdentifier\":\"633\",\"cookieparameter\":\"n/a\",\"Status\":\"Exact\",\"top_sku\":\"n/a\",\"region_input\":\"FR\",\"buffer_column_1\":\"03 Belle De Jour\",\"base_id\":\"PC835\",\"webMethod\":\"get\",\"cookieParam\":\"n/a\",\"sku_type\":\"n/a\",\"Channel\":\"n/a\",\"buffer_column_5\":\"46\",\"buffer_column_4\":\"EUR\",\"buffer_column_3\":\"n/a\",\"buffer_column_2\":\"n/a\",\"url\":\"https://www.sephora.fr/p/belle-de-teint-P2129023.html#id=633\",\"domain_input\":\"n/a\",\"normalizedpname\":\"Belle De Teint\",\"validateParsedOutput\":\"FALSE\",\"Brand\":\"Lancome\",\"variation_flag\":\"all_flag\",\"domain\":\"sephora_fr\",\"cookie_input\":\"n/a\",""\"variation_1\":\"976 Be Dior\",\"Frequency\":\"n/a\",\"variation_3\":\"n/a\",\"variation_2\":\"n/a\",\"Top_Category\":\"Make Up\"}]","retryCount":5,"fetchNextCrawlUrl":"True","region":"us","batch":"29Oct2019","subBatch":"Final","retailer":"sephora_fr","project":"LVMH Europe - P&C adhoc study (EOY price, promo)","productInfo":"False","sidDGFlag":"True","dgRelation":"False","environment":"Prod-LVMH-Spot","encoding":"UTF-8","projectId":"P14268188449537303","startTime":1578212682000,"validation_check":{},"childFlag":"False","parentUrlForCrawlDataLog":"https://www.sephora.fr/p/belle-de-teint-P2129023.html#id=633"}
        myuuid = uuid.uuid4()
        myuuid_v1 = uuid.uuid1()
        ranNum = random.randint(111111, 999999)
        cookie = '__pxvid=' + str(myuuid_v1) + '; _pxvid=' + str(myuuid) + ';'
        headers = {"cookie":cookie,"authority":"www.flooranddecor.com","method":"GET","scheme":"https","accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9","accept-encoding":"gzip, deflate, br","accept-language":"en-US,en;q=0.9","cache-control":"max-age=0","sec-ch-ua-mobile":"?0","sec-ch-ua-platform":"Windows","sec-fetch-dest":"document","sec-fetch-mode":"navigate","sec-fetch-site":"none","sec-fetch-user":"?1","upgrade-insecure-requests":"1","user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36 Edg/95.0.1020.44"}
        # headers = {"Cookie":cookie,"Authority":"www.flooranddecor.com","User-Agent":"Mozilla/5.0 (X11; CrOS x86_64 14268.67.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.111 Safari/537.36"}
        response = requests.get(url, headers=headers, verify=False).text
        # response = open('bodydump.html', 'r').read()
        parse(response, "[]", url_meta_data)