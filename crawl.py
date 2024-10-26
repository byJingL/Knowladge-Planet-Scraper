import re
import requests
import json
import os
import pdfkit
from bs4 import BeautifulSoup
from urllib.parse import quote
from time import sleep
import random
import datetime

# 请先登录你有权限查看的星球的账号，进入该星球页面
# 打开Inspect -> Network, 刷新页面,找到 topics?...
# General -> Request URL
# Request Headers -> Cookie -> abtest_env, zsxq_access_token
# Line 193, 199
ZSXQ_ACCESS_TOKEN = '86587BAD-427F-D721-836C-DDD7A25C9925_533F24D9AE640E7F'
ABTEST_ENV = 'product'
USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36'
ONLY_DIGESTS = False
ONLY_OWNER = True
# 仅精华
REQUEST_URL_DIGEST = 'https://api.zsxq.com/v2/groups/48884144148118/topics?scope=digests&count=20'
# 仅星主
REQUEST_URL_OWNER = 'https://api.zsxq.com/v2/groups/48884144148118/topics?scope=by_owner&count=20'
# 全部
REQUEST_URL_ALL = 'https://api.zsxq.com/v2/groups/48884144148118/topics?scope=all&count=20'
PDF_FILE_NAME = 'xxx.pdf'


def get_data(url, headers, before=None, after=None):
    """
    before 默认为None，否则请填入内容，格式为：'2021-06-31 21:00'，所有小于等于该时间的才会被获取
    after 默认为None，否则请填入内容，格式为：'2021-05-27 20:00'，所有大于等于该时间的才会被获取
    """
    global htmls, num

    i = 0
    while i < 10:
        rsp = requests.get(url, headers=headers)
        if rsp.json().get("succeeded") == False:
            sleep(0.01)
            print("访问失败，重来一遍...")
            rsp = requests.get(url, headers=headers)
            i += 1
        else:
            break

    with open('temp_content.json', 'w',
              encoding='utf-8') as f:  # 将返回数据写入 temp_content.json 方便查看
        f.write(json.dumps(rsp.json(), indent=2, ensure_ascii=False))

    with open('temp_content.json', encoding='utf-8') as f:
        all_contents = json.loads(f.read())
        contents = all_contents.get('resp_data').get('topics')
        if contents is not None:
            for topic in contents:
                create_time = topic.get("create_time", "")
                if create_time != "":
                    create_time = create_time[:16].replace("T", " ")
                    create_time_time = datetime.datetime.strptime(
                        create_time, '%Y-%m-%d %H:%M')
                    if after is not None:
                        after_time = datetime.datetime.strptime(
                            after, '%Y-%m-%d %H:%M')
                        if after_time > create_time_time: continue
                    if before is not None:
                        before_time = datetime.datetime.strptime(
                            before, '%Y-%m-%d %H:%M')
                        if create_time_time > before_time: continue

                content = topic.get(
                    'question',
                    topic.get('talk', topic.get('task',
                                                topic.get('solution'))))
                # print(content)
                text = content.get('text', '')
                text = re.sub(r'<[^>]*>', '', text).strip()
                text = text.replace('\n', '<br>')
                if text != "":
                    pos = text.find("<br>")
                    title = str(num) + " " + text[:pos]
                else:
                    title = str(num) + "Error: 找不到内容"

                if content.get('images'):
                    soup = BeautifulSoup(html_template, 'html.parser')
                    for img in content.get('images'):
                        url = img.get('large').get('url')
                        img_tag = soup.new_tag('img', src=url)
                        soup.body.append(img_tag)
                        html_img = str(soup)
                        html = html_img.format(title=title,
                                               text=text,
                                               create_time=create_time)
                else:
                    html = html_template.format(title=title,
                                                text=text,
                                                create_time=create_time)

                if topic.get('question'):
                    answer = topic.get('answer').get('text', "")

                    # 去除回答中的超链接标签和URL链接
                    # 方式一：使用正则表达式匹配并替换e标签
                    # pattern = r'<e type="web" href="[^"]*" title="([^"]*)"[^>]*/>'
                    # from urllib.parse import unquote
                    # answer = re.sub(pattern, lambda m: unquote(m.group(1)), answer)

                    # 方式二：使用BeautifulSoup处理:
                    # 处理answer中的超链接
                    if '<e type="web"' in answer:
                        # 将e标签格式转换为HTML格式以便BeautifulSoup处理
                        answer = answer.replace('<e type="web"', '<a').replace('/>', '></a>')
                        # 解析处理后的HTML
                        soup = BeautifulSoup(answer, 'html.parser')
                        # 找到所有的超链接标签
                        for link in soup.find_all('a'):
                            # 获取标签的title属性值（URL解码后）
                            title = link.get('title', '')
                            from urllib.parse import unquote
                            title = unquote(title)  # URL解码
                            # 用title替换整个链接标签
                            link.replace_with(title)
                        # 获取处理后的文本
                        answer = str(soup)

                    # 添加问题和答案到 HTML 中，并在两者之间添加分界线
                    soup = BeautifulSoup(html, 'html.parser')
                    hr_tag = soup.new_tag('hr')
                    soup.body.append(hr_tag)

                    # 添加答案内容
                    answer_tag = soup.new_tag('p')
                    answer_tag.string = answer
                    soup.body.append(answer_tag)
                    html_answer = str(soup)
                    html = html_answer.format(title=title,
                                              text=text,
                                              create_time=create_time)

                htmls.append(html)

                num += 1
        else:
            print("*" * 16, "访问失败", "*" * 16)
            print("失败url:", url)
            print(all_contents)
            print(rsp.status_code)
            print("*" * 40)

    next_page = rsp.json().get('resp_data').get('topics')
    if next_page:
        create_time = next_page[-1].get('create_time')
        if create_time[20:23] == "000":
            end_time = create_time[:20] + "999" + create_time[23:]
        else:
            res = int(create_time[20:23]) - 1
            end_time = create_time[:20] + str(res).zfill(3) + create_time[
                23:]  # zfill 函数补足结果前面的零，始终为3位数
        end_time = quote(end_time)
        if len(end_time) == 33:
            end_time = end_time[:24] + '0' + end_time[24:]
        next_url = start_url + '&end_time=' + end_time
        print("next_url:", next_url)
        sleep(random.randint(1, 5) / 100)
        get_data(next_url, headers, before, after)

    return htmls


def make_pdf(htmls, pdf_filepath=PDF_FILE_NAME):
    html_files = []
    for index, html in enumerate(htmls):
        file = str(index) + ".html"
        html_files.append(file)
        with open(file, "w", encoding="utf-8") as f:
            f.write(html)

    options = {
        "user-style-sheet": "default.css",
        "page-size": "A4",

        # 调整页边距使内容更集中
        "margin-top": "0.8in",
        "margin-right": "0.7in",
        "margin-bottom": "0.8in",
        "margin-left": "0.7in",

        "encoding": "UTF-8",
        "enable-smart-shrinking": "",  # 启用智能收缩
        "minimum-font-size": "16",  # 设置最小字号

        "custom-header": [("Accept-Encoding", "gzip")],
        "cookie": [("cookie-name1", "cookie-value1"),
                   ("cookie-name2", "cookie-value2")],
        "outline-depth": 10,
    }
    try:
        print("生成PDF文件中，请耐心等待...")
        if os.path.exists(pdf_filepath): os.remove(pdf_filepath)
        pdfkit.from_file(html_files, pdf_filepath, options=options)
    except Exception as e:
        print("生成pdf报错")
        print(e)

    for i in html_files:
        os.remove(i)

    print("已制作电子书在当前目录！")


if __name__ == '__main__':
    # 这个模板是默认的，无需修改
    html_template = """
        <!DOCTYPE html>
        <html lang="en">
            <head>
                <meta charset="UTF-8">
            </head>
            <body>
                <h1>{title}</h1>
                <p>{create_time}</p>
                <p>{text}</p>
            </body>
        </html>
    """
    headers = {
        'Cookie': "zsxq_access_token=%s; abtest_env=%s" % (ZSXQ_ACCESS_TOKEN, ABTEST_ENV),
        'User-Agent': USER_AGENT
    }

    start_url = ''
    if ONLY_DIGESTS:
        start_url = REQUEST_URL_DIGEST
    elif ONLY_OWNER:
        start_url = REQUEST_URL_OWNER
    else:
        start_url = REQUEST_URL_ALL

    # 只取大于等于 after ，小于等于 before 的日期时间的文章，可以省略这俩参数，获取所有的历史文章
    # 下面这里我演示的是一段时间的拆分获取 pdf，可以批量生成多个，用于内容跨度时间长，内容非常多的星球，你可以自己看着改
    # time_period = [
    #     ("2024-07-22 00:00", "2024-10-26 23:59"),
    # ]
    # for period in time_period:
    #     pdf_filepath = "%s%s-%s.pdf" % (PDF_FILE_NAME, period[0][:10].replace(
    #         "-", ""), period[1][:10].replace("-", ""))
    #     htmls = []
    #     num = 1
    #     make_pdf(get_data(start_url,
    #                       headers,
    #                       before=period[1],
    #                       after=period[0]),
    #              pdf_filepath=pdf_filepath)

    # 如果你想获取该星球的所有内容，请用这几句代码，但当内容较多的时候，生成 pdf 会极慢
    htmls = []
    num = 1
    make_pdf(get_data(start_url, headers))
