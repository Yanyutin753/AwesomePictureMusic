import random
import time
import lxml.etree
import os
import requests
import ssl
import uuid

ctx = ssl.create_default_context()
ctx.set_ciphers('DEFAULT')
header = {
    'referer': 'https://wwwfabiaoqing.com/',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/110.0',
    'cookie': 'PHPSESSID=akq55n83606e4meu0j2f12u9cv; '
              '__gads=ID=fb227ec439856242:T=1713402383:RT=1713407297:S=ALNI_MZZMrSkACpBOC2cFdAkVT2VkDTV8g; '
              '__gpi=UID=00000df092d300db:T=1713402383:RT=1713407297:S=ALNI_MYSCxg5yMp5TONvV2iFlahIanmWcg; '
              '__eoi=ID=d67eb71081d8ca35:T=1713402383:RT=1713407297:S=AA-AfjZX9wJ4uMAcSmg803k0a9lO; '
              'pp_main_e43fea2d4219a4cf92f1c615841461c7=1; sb_main_146c99b60bf94bef16d507e440a567e6=1; '
              'sb_count_146c99b60bf94bef16d507e440a567e6=5; '
              'dom3ic8zudi28v8lr6fgphwffqoz0j6c=51382414-d538-48de-81dc-edd35ea5ee60%3A2%3A1; '
              'pp_sub_e43fea2d4219a4cf92f1c615841461c7=4',
    'Connection': 'close'
}

requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS = 'ALL'
if not os.path.exists('bqb_pic3'):
    os.mkdir('bqb_pic3')
# page_n = int(input('请输入你需要爬取的网页数量'))
page_n = 55069
for i in range(52973, page_n):
    # url_bqb = f'https://www.fabiaoqing.com/bqb/lists/type/hot/page/{i}.html'
    url_bqb = f'https://www.fabiaoqing.com/bqb/detail/id/{i}.html'

    response = requests.get(url_bqb, headers=header)
    html_parser = lxml.etree.HTMLParser()
    html = lxml.etree.fromstring(response.text, parser=html_parser)
    # 将返回的字符串类型返回html进行解析
    bqb_title = html.xpath("//div[@class ='bqppdiv1']/p/text()")
    bqb_pic = html.xpath("//div[@class ='bqppdiv1']/img/@data-original")
    print("title:", i)
    print(bqb_pic)
    print(bqb_title)
    for title, pic in zip(bqb_title, bqb_pic):
        pic_stream = requests.get(pic, headers=header, stream=True)
        # 将pic的末尾三位作为文件名后缀 不一定是三位，把文件名中倒数一个点后的字符作为文件名后缀
        # stra = pic[-3:]
        # 使用uuid作为文件名
        stra = pic.split('.')[-1]
        filename = str(uuid.uuid4()) + '.' + stra
        with open(os.path.join('bqb_pic3', filename), 'wb+') as writer:
            writer.write(pic_stream.raw.read())
        print(f'{filename}下载成功')
        time.sleep(random.uniform(0.1, 0.4))
