import random
from htbTutor import *

ERR_UNKOWN = "ERROR: unrecognized command"

def parseCommand(cmd: str) -> [str]:
    if entry[:len(cmd)] == cmd:
        return " ".split(entry)
    return []


props = run(True)
while True:
    print("######################################################################")
    entry = input("command >>>> ")

    if (e := parseCommand("prop")):
        if len(e) == 1 or e[1] == "list":
            print(props)
            # print([n for n in ])
        elif e[1] == "first":
            prop = props[0]
            print(prop)
            # print(
            #     (prop[0]['name'], prop[0]['difficulty']),
            #     (prop[1]['name'], prop[1]['difficulty']),
            #     (prop[2]['name'], prop[2]['difficulty'])
            # )
        elif e[1] == "last":
            prop = props[-1]
            print(prop)
            # print(
            #     (prop[0]['name'], prop[0]['difficulty']),
            #     (prop[1]['name'], prop[1]['difficulty']),
            #     (prop[2]['name'], prop[2]['difficulty'])
            # )
        else:
            try:
                index = int(e[1])
                print(prop[index])
            except:
                print(ERR_UNKOWN)
    elif (e := parseCommand("shuffle")):
        random.shuffle(props)
        print("Shuffling done!")
    # elif (e := parseCommand("sort")):
    #     if e == "" or e == " asc" or e == " ascend" or e == "ascending":
    elif (e := parseCommand("rerun")):
        props = run()
    else:
        print(ERR_UNKOWN)
