import random
from htbTutor import *

ERR_UNKOWN = "ERROR: unrecognized command, please type help"

def parseCommand(e: str, cmd: str) -> [str]:
    if e[:len(cmd)] == cmd:
        return e.split(" ")
    return []

props = False
while True:
    print("######################################################################")
    entry = input("command >>>> ")

    if (e := parseCommand(entry, "help")):
        print("available commands: start; prop [list|first|last|X]; shuffle; list; set []")

    elif (e := parseCommand(entry, "list")):
        print("verbose", verbose)
        print("yt_dlp_verbose", yt_dlp_verbose)
        print("cachingToFile", cachingToFile)
        print("showSummary", showSummary)
        print("processingOnly", processingOnly)
        print("noOutput", noOutput)
        print("jsonOutput", jsonOutput)
        print("diffArray", diffArray)
        print("chosenDiffRegex", chosenDiffRegex)
        print("chosenPlatformRegex", chosenPlatformRegex)
        print("outputDepthLimit", outputDepthLimit)
        print("filterOutAlreadyDone", filterOutAlreadyDone)

    elif (e := parseCommand(entry, "set")):
        l = len(e)
        if l < 2:
            print("error: set has to have at least 2 arguments")
        c = e[2]
        i = 3
        while i < l:
            c += " "+e[i]
            i += 1
        e[2] = c

        # TODO: check type of entry before eval
        if (e[1] == "verbose"):
            verbose = eval(e[2])
        elif (e[1] == "yt_dlp_verbose"):
            yt_dlp_verbose = eval(e[2])
        elif (e[1] == "cachingToFile"):
            cachingToFile = eval(e[2])
        elif (e[1] == "showSummary"):
            showSummary = eval(e[2])
        elif (e[1] == "processingOnly"):
            processingOnly = eval(e[2])
        elif (e[1] == "noOutput"):
            noOutput = eval(e[2])
        elif (e[1] == "jsonOutput"):
            jsonOutput = eval(e[2])
        elif (e[1] == "diffArray"):
            diffArray = eval(e[2])
        elif (e[1] == "chosenDiffRegex"):
            chosenDiffRegex = eval(e[2])
        elif (e[1] == "chosenPlatformRegex"):
            chosenPlatformRegex = eval(e[2])
        elif (e[1] == "outputDepthLimit"):
            outputDepthLimit = eval(e[2])
        elif (e[1] == "filterOutAlreadyDone"):
            filterOutAlreadyDone = eval(e[2])
        else:
            print("error: unrecognized variable", e[1])


    elif (e := parseCommand(entry, "start")):
        props = run()

    elif (e := parseCommand(entry, "prop")):
        if (props == False):
            print("error: run start first")
        elif len(e) == 1 or e[1] == "list":
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

    elif (e := parseCommand(entry, "shuffle")):
        if (props == False):
            print("error: run start first")
        random.shuffle(props)
        print("Shuffling done!")
    # elif (e := parseCommand(entry, "sort")):
    #     if e == "" or e == " asc" or e == " ascend" or e == "ascending":

    else:
        print(ERR_UNKOWN)
