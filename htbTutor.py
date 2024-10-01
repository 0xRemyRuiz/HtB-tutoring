import os, re, json, scrapetube, yt_dlp, requests, math, random, hashlib, time, platform
from tinydb import TinyDB, Query
from datetime import datetime
import datetime as dt # FUNNY THAT I NEED THAT TO ACCESS STATIC FUNCTIONS...

from const import *
from utils import *


ippsecChannelId = 'UCa6eh7gCkpPo5XXUDfygQQA'

# ###
# Globals
# ###
db = TinyDB(f'{loc}tinydb.json')


# ###
# Config
# ###
_difficulty = {
    'name': [
        'very easy',
        'easy',
        'medium',
        'hard',
        'insane'
    ]
}
_difficulty['s'] = buildRegexSelector(_difficulty['name'])
_platform = {
    'name': [
        'linux',
        'windows',
        'freebsd',
        'openbsd',
        'android',
        'solaris',
        'other'
    ]
}
_platform['s'] = buildRegexSelector(_platform['name'])

# ###
# Arguments
# ###
# TODO: use args here
verbose = False
yt_dlp_verbose = False
cachingToFile = True
showSummary = False
processingOnly = False
noOutput = True
jsonOutput = True
diffArray = _difficulty['name']

# chosenDiffRegex = f'{diffArray[0]}|{diffArray[1]}'
chosenDiffRegex = _difficulty['s']
chosenPlatformRegex = f'linux|windows'
# chosenPlatformRegex = _platform['s']
outputDepthLimit = 3
filterOutAlreadyDone = True

htbMachinesRawCacheName = 'htbMachinesRawCache.html'
htbMachinesRawCacheLocation = f'{loc}{htbMachinesRawCacheName}'
ippsecVideosUrl = 'https://www.youtube.com/@ippsec/videos'
ippsecChannelUrl = 'https://www.youtube.com/channel/'+ippsecChannelId
htbHost = 'www.hackthebox.com'

# ###
# Methods
# ###
def refreshIppsecDatabase(dbVideos):
    query = Query()
    ippsecMeta = 'ippsecMeta'
    ippsecMetaFound = db.search(query._type == ippsecMeta)
    if len(ippsecMetaFound) and ippsecMetaFound[0]['ts']:
        ippsecMetaFoundTime = time.mktime(datetime.strptime(ippsecMetaFound[0]['ts'], "%Y-%m-%d %H:%M:%S.%f").timetuple())
        if len(ippsecMetaFound) and check_timestamp_against_timedelta(ippsecMetaFoundTime, dt.timedelta(days=3)) == False:
            # hard skip everything
            if verbose == True: my_p('refreshIppsecDatabase()', f'[INFO] hard skip for channel ID {ippsecChannelId}')
            return

    def decorateBlob(blob, video, dbVideo):
        # TODO: precheck with time to hard skip the web request
        if dbVideo and dbVideo[0] and dbVideo[0]["id"]:
            if verbose == True: my_p('decorateBlob()', f'[INFO] hard skip video {dbVideo[0]["id"]}')
            return dbVideo[0]
        try:
            with yt_dlp.YoutubeDL({"quiet": not(yt_dlp_verbose), "no-warnings": True}) as ydl:
                info_dict = ydl.extract_info(f'https://www.youtube.com/watch?v={video["videoId"]}', download=False)
                if not dbVideo:
                    blob['_added'] = str(datetime.now())
                    blob['score'] = 0 # initialize the score
                    blob['hash'] = ''
                    try: blob['length'] = strHMS_toint(video['lengthText']['simpleText'])
                    except: blob['length'] = 0
                    try: blob['title'] = info_dict['title']
                    except: blob['title'] = ""
                    try: blob['categories'] = info_dict['categories']
                    except: blob['categories'] = []
                    try: blob['tags'] = info_dict['tags']
                    except: blob['tags'] = []
                    try: blob['description'] = info_dict['description']
                    except: blob['description'] = ""
                    try: blob['chapters'] = info_dict['chapters']
                    except: blob['chapters'] = []
                    try: blob['comment_count'] = int(info_dict['comment_count'])
                    except: blob['comment_count'] = 1
                    try: blob['like_count'] = int(info_dict['like_count'])
                    except: blob['like_count'] = 1
                    try: blob['view_count'] = int(info_dict['view_count'])
                    except: blob['view_count'] = 0

                    # add an "htb-tag" with the name of the machine it matched with
                    match = re.search(r'hack ?the ?box ?\- ?([a-z0-9]+)', video['title']['runs'][0]['text'], flags=re.IGNORECASE)
                    if not match: match = re.search(r'HTB(!\-)+\- ?([a-z0-9]+)', video['title']['runs'][0]['text'], flags=re.IGNORECASE)
                    # TODO: this below does not seem to work all!
                    if match != None: blob['htb-tag'] = match[1].lower()
                # if it's not an update then add basic props
                else:
                    # TODO: update db to keep track of evolution (and show trends?)
                    #       this has to be moved at one point
                    # TODO: handle history push like strategy
                    blob = dbVideo[0]
                    try: blob['comment_count'] = int(info_dict['comment_count'])
                    except: blob['comment_count'] = 1
                    try: blob['like_count'] = int(info_dict['like_count'])
                    except: blob['like_count'] = 1
                    try: blob['view_count'] = int(info_dict['view_count'])
                    except: blob['view_count'] = 0
                # TODO: fix the score
                blob['score'] = math.log10(blob['comment_count']) * math.log10(blob['like_count']) * math.log10(blob['view_count']) * math.log10(blob['length'])
                print('DEBUG: score', f"{math.log10(blob['comment_count'])} * {math.log10(blob['like_count'])} * {math.log10(blob['view_count'])} * {math.log10(blob['length'])} = {blob['score']}")
        except:
            return None

        return blob

    if verbose == True: my_p('refreshIppsecDatabase()', f'[INFO] refresh from youtube based on channel ID {ippsecChannelId}')
    # TODO: try to find a way to have a "quick" compare before fetching all videos
    videos = []
    try:
        videos = list(scrapetube.get_channel(ippsecChannelId))
    except:
        if verbose == True: my_p('refreshIppsecDatabase()', f'[ERROR] failed to scrape channel ID {ippsecChannelId}')
        return # exit

    # x is to follow advancement and is to be incremented and compared to total videos
    x = 1
    totalNumberOfVIdeos = len(videos)
    for video in videos:
        # percentage of advancement
        if verbose == True: print('refreshIppsecDatabase()', f'[INFO] {round(x * (100 / totalNumberOfVIdeos))}%')
        x += 1 # advance

        # update only if needed
        update = False
        # compare with the previously scraped videos from ippsec videos page
        dbVideo = [v for v in dbVideos if v['id'] == video['videoId']]
        # video found in db meaning so we need to update the found record
        if len(dbVideo) != 0: update = True

        blob = {
            '_type': 'video',
            'id': video['videoId']
        }
        # TODO: refactor for a pseudo-"controller-model" pattern
        def hashIt(entry):
            try:
                blob = {
                    '_type': entry['_type'],
                    'id': entry['id'],
                    '_added': entry['_added'],
                    'score': entry['score'],
                    'length': entry['length'],
                    'title': entry['title'],
                    'categories': entry['categories'],
                    'tags': entry['tags'],
                    'description': entry['description'],
                    'chapters': entry['chapters'],
                    'comment_count': entry['comment_count'],
                    'like_count': entry['like_count'],
                    'view_count': entry['view_count']
                }
            except:
                blob = {}
                # blob = b''
            return hashlib.md5(json.dumps(blob, sort_keys=True).encode('utf-8')).hexdigest()

        # TODO: hard skip if last mod is < 3 days
        # TODO: rename and refactor please...
        blob = decorateBlob(blob, video, dbVideo)
        if blob == None:
            if verbose == True: print('refreshIppsecDatabase()', f'[WARN] something broke for {video["videoId"]}')
            continue

        blob['hash'] = hashIt(blob)
        try:
            if blob['length'] > 0:
                if blob['hash'] == '':
                    if verbose == True: print('refreshIppsecDatabase()', f'[WARN] hashing failed for video: {video["videoId"]}')
                # if hash perfectly matches the already present in db we skip item
                elif update and blob['hash'] == dbVideo[0]['hash']:
                    if verbose == True: print('refreshIppsecDatabase()', f'[INFO] SKIP video: {video["videoId"]}')
                    continue # skip
            else:
                if verbose == True: my_p('refreshIppsecDatabase()', f'[WARN] failed to parse basic infos for video: {video["videoId"]}, continuing...')
                if verbose == True: print('Reason', f'video length is inconsistant see: length = {blob["length"]}')
                print(blob)
        except Exception as err:
            if verbose == True: my_p('refreshIppsecDatabase()', f'[WARN] failed to parse basic infos for video: {video["videoId"]}, continuing...')
            if verbose == True: print('Reason', err)
            print(blob)

        if not update:
            if verbose == True: my_p('refreshIppsecDatabase()', f'[INFO] inserting a new video with {video["videoId"]} as ID')
            db.insert(blob)
        else:
            if verbose == True: my_p('refreshIppsecDatabase()', f'[INFO] updating video {video["videoId"]}')
            db.update(blob, query.id == video['videoId'])
    
    # after all update timestamp
    query = Query()
    obj = {'_type': ippsecMeta, 'ts': str(datetime.now())}
    if len(ippsecMetaFound) != 0:
        db.update(obj, query._type == ippsecMeta)
        if verbose == True: my_p('refreshIppsecDatabase()', f'[INFO] update lastIppsecRefresh')
    else:
        db.insert(obj)
        if verbose == True: my_p('refreshIppsecDatabase()', f'[INFO] insert lastIppsecRefresh')

def get_HtB_machines_response():
    htbMachinesUrl = f'https://{htbHost}/machines'
    if verbose == True: my_p('get_HtB_machines_response()', f'[INFO] fetching {htbMachinesUrl}')
    response = requests.get(htbMachinesUrl, headers={ 'Host': f'{htbHost}', 'User-Agent': UserAgent().random }).text
    # 404 (fake response is around 144 chars in response)
    # 404 (honest response for real not found is more than 5.5k chars in response)
    # 200 (good response is around 450k chars in response)
    if len(response) < 300e3 and verbose == True:
        my_p('get_HtB_machines_response()', '[WARN] response might be wrong as it\'s less than 300k, ignoring...')
    # TODO: check for the number of machines
    # my_p('get_HtB_machines_response()', f'[INFO] Number of machines: {response.find("<title>") + 7 : response.find("</title>")}')
    return response

def cache_HtB_machines_raw():
    try:
        content = get_HtB_machines_response()
        with open(htbMachinesRawCacheLocation, 'w') as myfile:
            myfile.write(content)
    except Exception as err:
        if verbose == True: my_p('cache_HtB_machines_raw()', f'[WARN] unable to write to cache file: {htbMachinesRawCacheLocation}')
        print(err)
    return content

def get_HtB_machines_raw():
    if cachingToFile == True:
        try:
            # check the last update time to update our cache regularily
            if check_timestamp_against_timedelta(os.path.getmtime(htbMachinesRawCacheLocation), dt.timedelta(days=3)):
                return cache_HtB_machines_raw()
        except Exception as err:
            if verbose == True: print('[WARN] failed cache resolution...', err)
            return cache_HtB_machines_raw()

        # load the cache file
        try:
            with open(htbMachinesRawCacheLocation, 'r') as myfile:
                return myfile.read()
            if len(htbMachinesRaw) == 0:
                return cache_HtB_machines_raw()
        except Exception as err:
            if verbose == True: my_p('get_HtB_machines_raw()', '[INFO] cache file is not there or empty')
            print(err)
            return cache_HtB_machines_raw()
    # No caching to file
    return get_HtB_machines_response()

def load_HtB_database():
    if verbose == True: my_p('load_HtB_database()', '[INFO] populating the database...')
    # try:
    #     if verbose == True: print('', '[INFO] fetching existing database...')
    #     # TODO: get videos from tinydb not youtube......
    #     # dbVideos = list(scrapetube.get_channel(ippsecChannelId))
    #     dbVideos = ytscrape(ippsecChannelUrl)
    # except:
    #     dbVideos = []
    #     if verbose == True: print('', '[WARN] unable to load existing the database')
    #     return
    query = Query()
    dbVideos = db.search(query._type == 'video')

    htbMachinesRaw = get_HtB_machines_raw()
    refreshIppsecDatabase(dbVideos)

    ############
    # SEARCH
    ############

    # TODO: find the magic regex that really works for matching html tags
    #           cf. https://regex101.com/r/gY1nI4/1 -> not good enough but is working right now
    e = 'a' # base tag element
    # find the slug corresponding to the machine name and url (nice and simple design from htb)
    slug = '([^"]+)"'
    ee = f'(?:<(?!{e})[^>]*)*[^<]*(?:<(?!/{e}[^>]*>)[^<]*)*'
    htbMachineRegex = f'(<{e} href="https://{htbHost}/machines/{slug}[^>]*>{ee}</{e}>)'
    # parse the cache file
    machinesFromResponse = re.findall(htbMachineRegex, htbMachinesRaw)
    for matchin in machinesFromResponse:
        if len(matchin) == 0 or len(matchin[1]) == 0 or matchin[1] == None:            
            if verbose == True: my_p('load_HtB_database()', f'[WARN] failed to match a machine, skipping...')
            continue

        try:
            name = matchin[1].lower()
            flags = re.IGNORECASE
            difficulty = re.search(f'({_difficulty["s"]})<\\/', matchin[0], flags=flags)
            avatar = re.search(r'(https://[a-z\.\/]+avatars/[a-z0-9]+\.[a-z0-9]+)', matchin[0], flags=flags)
            platform = re.search(f'({_platform["s"]})', matchin[0], flags=flags)
            blob = {
                '_type': 'machine',
                '_added': str(datetime.now()),
                'name': name,
                'difficulty': difficulty[1].lower(),
                'difficultyLevel': _difficulty['name'].index(difficulty[1].lower()),
                'avatar': avatar[1],
                'platform': platform[1].lower(),
                'doneDate': ""
            }
        except Exception as err:
            if verbose == True:
                my_p('load_HtB_database()', f'[WARN] failed to add new machine named {matchin[1]}')
                if difficulty == None:
                    print('difficulty match failed')
                if avatar == None:
                    print('avatar match failed')
                if platform == None:
                    print('platform match failed')
                print(matchin)
                print(err)
            continue

        # TODO: implement a hash compare strategy
        query = Query()
        if len(db.search(query._type == 'machine' and query.name == matchin[1])) == 0:
            if verbose == True: my_p('load_HtB_database()', f'[INFO] adding new machine named {matchin[1]}')
            db.insert(blob)
        # except:
        #     if verbose == True: my_p('load_HtB_database()', f'[WARN] failed to parse infos for machine: {machine[1]}, continuing...')
        #     print(blob)
            # continue
    return htbMachinesRaw, machinesFromResponse

def processingDatabase():
    if verbose == True: my_p('processingDatabase()', '[INFO] Processing database...')
    if verbose == True: print('-', 'Processing videos')
    query = Query()
    videos = db.search(query._type == 'video')
    # # Sort videos in the ascending order
    # for i in range(len(videos)):
    #     curr_video = videos[i]
    #     j = i - 1
    #     while j >= 0 and curr_video['score'] < videos[j]['score'] :
    #         videos[j + 1] = videos[j]
    #         j -= 1
    #     videos[j + 1] = curr_video

    if verbose == True: print('-', 'Processing machines against videos')
    query = Query()
    machines = db.search(query._type == 'machine')
    propositions = []
    unresolvedMachines = []
    # TODO: invert the logic here..... videos are already sorted so it needs to be done by video and not by machine
    for m in machines:
        m['vids'] = []
        for v in videos:
            try:
                # htbTagMatch = re.search(v['htb-tag'], m['name'], re.IGNORECASE)
                # if htbTagMatch != None:
                    # m['vids'].append(v)
                if v['htb-tag'] != None and v['htb-tag'].lower() == m['name']:
                    # print(v['htb-tag'].lower(), m['name'])
                    m['vids'].append(v)
                    v['marked'] = True # TODO: invert logic here also
            except: continue

        if m['vids'] != None and len(m['vids']) > 0:
            propositions.append(m)
            # if len(m['vids']) > 1:
            #     print(m['name'], m['vids'])
            #     print('-'*30)
            #     print('-'*30)
        else:
            unresolvedMachines.append(m)
    return propositions, unresolvedMachines, machines, videos


# TODO: really sort propositions
def sortingPropositions(propositions, regexDifficultyChosen):
    if verbose == True: my_p('sortingPropositions()', '[INFO] Processing propositions...')
    if verbose == True: print('-', 'Sorting propositions')
    # TODO: continue building logic....
    i = 0
    classedProps = [[], [], []]
    if filterOutAlreadyDone == True:
        for p in propositions:
            if p['doneDate'] != '':
                propositions.remove(p)
    limit = len(propositions) / 3
    j = 0
    for p in propositions:
        if i >= limit:
            limit += limit
            j += 1
        i += 1

        try:
            # TODO: setup difficulty
            difficultyOk = re.search(regexDifficultyChosen, p['difficulty'], flags=re.IGNORECASE)
            platformOk = re.search(chosenPlatformRegex, p['platform'], flags=re.IGNORECASE)
        except:
            continue # skip

        if difficultyOk != None and platformOk != None:
            classedProps[j].append(p)

    if verbose == True: print('-', 'Building final propositions tuple list')
    finalProps = []
    # TODO: change this algo to have increasing difficulty option
    while len(classedProps[0]) and len(classedProps[1]) and len(classedProps[2]):
        # TODO: a nice and clean for loop for this please
        c1 = random.choice(classedProps[0])
        classedProps[0].remove(c1)
        c2 = random.choice(classedProps[1])
        classedProps[1].remove(c2)
        c3 = random.choice(classedProps[2])
        classedProps[2].remove(c3)
        # TODO: make this tuple more "customisable"
        finalProps.append((c1, c2, c3))
    return finalProps


# ###
# Calls and objects creation
# ###
def run(skip=False, doVerbose=False):
    verbose = doVerbose
    # simply check and make the db
    if skip:
        load_HtB_database()
        propositions, unresolvedMachines, machines, videos = processingDatabase()
        return propositions

    if not processingOnly:
        if not verbose: print('Refreshing database...')
        htbMachinesRaw, results = load_HtB_database()
    else:
        if verbose == True: my_p('', '[INFO] processingOnly is on, HARD SKIPPING refreshing the database...')

    if not verbose: print('Processing database...')
    # TODO: externalize that
    propositions, unresolvedMachines, machines, videos = processingDatabase()
    finalProps = sortingPropositions(propositions, chosenDiffRegex)

    # ###
    # Stats
    # ###
    numberOfPropositions = len(propositions)
    numberOfUnresolvedMachines = len(unresolvedMachines)
    numberOfMachinesInDB = len(machines)
    numberOfVideos = len(videos)
    try:
        numberOfMachinesRecheckFromRaw = int((re.search(f'<title>([0-9]+)', htbMachinesRaw, re.IGNORECASE))[1])
    except:
        numberOfMachinesRecheckFromRaw = numberOfMachinesInDB
    try:
        numberOfResults = len(results)
    except:
        numberOfResults = numberOfMachinesInDB
    try:
        htbMachinesRawResponseSizeInK = round(len(htbMachinesRaw) / 1e3) # value rounded to K (10^3) for clarity
    except:
        htbMachinesRawResponseSizeInK = 300
    # try:
    #     numberOfFinalprops = len(finalProps) * len(finalProps[0]) # total len multiplied by size of tuples
    # except:
    #     numberOfFinalprops = -1

    # ###
    # Static summary
    # ###
    if showSummary == True:
        my_p('Quick summary', '')
        label = ' - '
        print('--Ippsec videos stats--')
        print(label, f'number of Ippsec\'s parsed videos          = {numberOfVideos}')
        # print(label, f'estimated number of Ippsec\'s videos       = {ippsecEstimatedTotalVideoNumber}')
        print('--Machines stats--')
        print(label, f'size of htb machines page response        = {htbMachinesRawResponseSizeInK}K')
        print(label, f'number of htb machines from page response = {numberOfMachinesRecheckFromRaw}')
        print(label, f'number of parsed htb machines             = {numberOfResults}')
        print(label, f'number of machines                        = {numberOfMachinesInDB}')
        print('--Propositions stats--')
        print(label, f'number of unresolved machines             = {numberOfUnresolvedMachines}')
        print(label, f'number of propositions                    = {numberOfPropositions}')
        # print(label, f'number of final propositions              = {numberOfFinalprops}')


    # TODO: maybe add https://ippsec.rocks/?# integration once we have a frontend

    if not noOutput:

        # stopCount = 5
        # full length
        stopCount = outputDepthLimit
        if stopCount < 1:
            stopCount = len(finalProps)
        propsRebuilt = []
        if jsonOutput:
            print(json.dumps(propositions, sort_keys=True).encode('utf-8'))
        else:
            for prop in finalProps:
                if stopCount == 0: break
                stopCount -= 1
                print(
                    (prop[0]['name'], prop[0]['difficulty']),
                    (prop[1]['name'], prop[1]['difficulty']),
                    (prop[2]['name'], prop[2]['difficulty'])
                )

    numberOfFinalprops = len(finalProps)
    return {
            "propositions": propositions,
            "finalProps": finalProps,
            "numberOfFinalprops": numberOfFinalprops,
            "numberOfVideos": numberOfVideos,
            # "ippsecEstimatedTotalVideoNumber": ippsecEstimatedTotalVideoNumber,
            "htbMachinesRawResponseSizeInK": htbMachinesRawResponseSizeInK,
            "numberOfMachinesRecheckFromRaw": numberOfMachinesRecheckFromRaw,
            "numberOfResults": numberOfResults,
            "numberOfMachinesInDB": numberOfMachinesInDB,
            "numberOfUnresolvedMachines": numberOfUnresolvedMachines,
            "numberOfPropositions": numberOfPropositions
            }

# f = open('.\\tttt.json', 'w')
# f.write(json.dumps(finalProps[0][0], sort_keys=True))

# my_p('', '[DEBUG] shitty debug...')
# # TODO: lel
# print(finalProps[0][0])
# print('-'*30)
# print('-'*30)
# print(finalProps[1][0])
# print('-'*30)
# print('-'*30)
# print(finalProps[2][0])


# EXPERIMENT 2
#################
# NOTE: yt-dlp is not suited for the job
# with yt_dlp.YoutubeDL({
#         # "player_skip": "all",
#         # "player_skip": [ "all" ],
#         # "player_skip": [ "configs", "webpage", "js" ],
#         # "skip": "webpage",
#         # "quiet":    True,
#         # "extractor_args": {'player': {'skip': ['all']}},
#         # "webpage_request": False,
#         # "simulate": True,
#         "forceurl": True,
#         "forcetitle": True,
#         # "noplaylist":True
#     }) as ydl:

#     # TODO: regular fast update sub channel info
#     # info = ydl.extract_info(ippsecVideosUrl, download=False, process=False)
#     # recursively download every
#     info = ydl.extract_info(ippsecVideosUrl, download=False)
#     print("********")
#     print("********")
#     print("********")
#     print("********")
#     print("********")
#     print(info["playlist_count"])
#     print("********")
#     print("********")
#     print("********")
#     print("********")
#     print("********")

#     # ℹ️ ydl.sanitize_info makes the info json-serializable
#     # print(info.keys())
#     dump = json.dumps(ydl.sanitize_info(info))
#     print(dump[:500])
#     # with open("tmp-dump.json", "w") as myfile:
#     #     myfile.write(dump)

#     # fff = open(loc+'dump0.json', 'a')
#     # fff.write(dump)

# REFERENCE IDEA
# print("NAME:", data[0]["name"])
# print("RANK:", data[0]["rank"])
# print("DIFF:", data[0]["difficulty"])
# print("URL:", data[0]["url"])

