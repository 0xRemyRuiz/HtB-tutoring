import requests, json
from fake_useragent import UserAgent
from datetime import datetime
import datetime as dt


# ###
# Utils
# ###
def my_p(name, txt):
    screenWidthConstant = 366
    txt = txt if txt != None else ""
    message = name.upper()+": "+txt
    l = (len(message) if len(message) < screenWidthConstant else screenWidthConstant)
    print("#"+"_"*l)
    print("#"+" "*l)
    print("#"+message)
    print("#"+"_"*l)

def strHMS_toint(time_str):
    """Get seconds from time."""
    split = time_str.split(':')
    if len(split) > 2:
        return int(split[0]) * 3600 + int(split[1]) * 60 + int(split[2])
    if len(split) > 1:
        return int(split[0]) * 60 + int(split[1])
    return int(split[0])

def check_timestamp_against_timedelta(timestamp, delay):
    timeDiff = datetime.now() - datetime.fromtimestamp(timestamp)
    # print(timeDiff, delay, timeDiff > delay)
    return timeDiff > delay

def buildRegexSelector(input):
    if len(input) == 1: return input[0] 
    output = ''
    for d in input[:-1]:
        output += d+'|' # add the "or" operator in between
    # adding the last element afterward to avoid having a hanging pipe at the end
    output += input[-1]
    return output

def ytscrape(url):
    # def get_json_from_html(html: str, key: str, num_chars: int = 2, stop: str = '"') -> str:
    #     pos_begin = html.find(key) + len(key) + num_chars
    #     pos_end = html.find(stop, pos_begin)
    #     return html[pos_begin:pos_end]

    def get_session() -> requests.Session:
        session = requests.Session()
        session.headers[
            "User-Agent"
        ] = UserAgent().random
        session.headers["Accept-Language"] = "en"
        return session
    def get_initial_data(session: requests.Session, url: str) -> str:
        session.cookies.set("CONSENT", "YES+cb", domain=".youtube.com")
        response = session.get(url, params={"ucbcb":1})

        html = response.text
        return html

    session = get_session()
    html = get_initial_data(session, url)
    # with open('.\\tmp-html2.html', 'w') as myfile:
    #     json.dump(myfile, html, sort_keys=True))
    return json.dumps(html, sort_keys=True)
    # return html
    # client = json.loads(
    #     get_json_from_html(html, "INNERTUBE_CONTEXT", 2, '"}},') + '"}}'
    # )["client"]
    # session.headers["X-YouTube-Client-Name"] = "1"
    # session.headers["X-YouTube-Client-Version"] = client["clientVersion"]
    # j = json.loads(
    #     get_json_from_html(html, "var ytInitialData = ", 0, "};") + "}"
    # )
    # print(j["videosCountText"])
    # return json.loads(
    #     get_json_from_html(html, "var ytInitialData = ", 0, "};") + "}"
    # )
