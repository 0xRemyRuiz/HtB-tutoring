from htbTutor import run
from utils import *


obj = run()

# ###
# Consistancy tests
# ###
def curateTestList():
    tests = []
    tests.append((
        'Success from recheck of number of machines from raw',
        obj["numberOfFinalprops"] != -1,
        f'{obj["numberOfFinalprops"]} == -1'
    ))
    tests.append((
        'Success from getting the total number of final propositions',
        obj["numberOfMachinesRecheckFromRaw"] != -1,
        f'{obj["numberOfMachinesRecheckFromRaw"]} == -1'
    ))
    tests.append((
        'HackTheBox machine listing web response should be higher than 350K',
        obj["htbMachinesRawResponseSizeInK"] > 350,
        f'{obj["htbMachinesRawResponseSizeInK"]} < 350'
    ))
    # TODO: check why certain videos seem to be missed
    # this test below is, for now, always false
    # tests.append((
    #     'Total number of ippsec videos in DB should be equal to the estimatation',
    #     obj["numberOfVideos"] == obj["ippsecEstimatedTotalVideoNumber"],
    #     f'{obj["numberOfVideos"]} != {obj["ippsecEstimatedTotalVideoNumber"]}'
    # ))
    tests.append((
        'Equality for number of machines in db and scraped',
        obj["numberOfResults"] == obj["numberOfMachinesRecheckFromRaw"],
        f'{obj["numberOfResults"]} != {obj["numberOfMachinesRecheckFromRaw"]}'
    ))
    tests.append((
        'Superior to zero number of propositions',
        obj["numberOfPropositions"] > 0,
        f'{obj["numberOfPropositions"]} <= 0'
    ))
    tests.append((
        'Inferior number of unresolved machines than half total machines',
        obj["numberOfUnresolvedMachines"] < obj["numberOfMachinesInDB"] / 2,
        f'{obj["numberOfUnresolvedMachines"]} < {obj["numberOfMachinesInDB"]} / 2'
    ))
    # TODO: clarify this, as it seems I have a double
    tests.append((
        'Triple equality for number of machines in db and scraped (with rechecked value)',
        obj["numberOfResults"] == obj["numberOfMachinesRecheckFromRaw"] and obj["numberOfMachinesRecheckFromRaw"] == obj["numberOfMachinesInDB"],
        f'{obj["numberOfResults"]} != {obj["numberOfMachinesRecheckFromRaw"]} != {obj["numberOfMachinesInDB"]}'
    ))
    # # TODO: refactor and clean this maybe
    # tests.append((
    #     'Final propositions should be a list of size tuples',
    #     obj["numberOfFinalprops"] / 3 == len(obj["finalProps"]),
    #     f'{obj["numberOfFinalprops"]} / 3 != {len(obj["finalProps"])}'
    # ))
    return tests

def runTests(testList):
    # returns 1 if successful and 0 if not
    def evalTest(text, ev, err):
        okLabel = '[OK]'
        errLabel = '[FAIL]'
        if ev:
            print(okLabel, f'{text} passed')
            return 1
        else:
            print(errLabel, f'{text} FAILED -> {err}')
            return 0
    totalSuccess = 0
    totalTests = 0
    for text, ev, err in testList:
        # either +1 or +0
        totalSuccess += evalTest(text, ev, err)
        totalTests += 1
    return totalSuccess, totalTests

try:
    successNumber, testNumber = runTests(curateTestList())
    if testNumber == 0:
        print('no consistancy test has run')
    else:
        failNumber = testNumber - successNumber
        # failRatio should be of type .2f
        failRatio = ((failNumber * 100) // testNumber) / 100

        successReport = f'{successNumber} success{"es" if successNumber > 1 else ""}'
        failReport = f'{failNumber} fail{ "s" if failNumber > 1 else ""}'
        failRatioReport = f'fail ratio is about {failRatio}'
        print(f'{successReport} {failReport} and {failRatioReport}')

except Exception as err:
    print('consistancy tests failed for some reason')
    print(err)
