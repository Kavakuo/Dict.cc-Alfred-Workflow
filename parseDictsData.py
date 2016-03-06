# Just run this script with Alfred.
# Enter dictcc wf:executeParsing in Alfred
#
# Be sure that the dictccSettings.json file is configured correctly!



# The MIT License (MIT)
#
# Copyright (c) [2016] [Philipp Nieting]
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.



import ujson
import re, os, sys, time
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker, clear_mappers, mapper

metadata = None
currentTablename = ""
readyForFirstCommit = False
tableExists = False

SQL_ENGINE = None
session = None

DEBUG = False


class x:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class Dictionary(object):

    def __init__(self, sf, ss, of, os):
        self.searchFirstLang = sf
        self.searchSecondLang = ss
        self.orgFirstLang = of
        self.orgSecondLang = os

    def __repr__(self):
        return "<Dict searches=[%s, %s] orgs=[%s, %s]" %(self.searchFirstLang, self.searchSecondLang, self.orgFirstLang, self.orgSecondLang)


def get_table_object(tablename):
    global metadata, currentTablename, readyForFirstCommit, tableExists
    metadata = MetaData()
    currentTablename = tablename
    table_object = Table(tablename, metadata,
                         Column('id', Integer, primary_key=True),
                         Column('searchFirstLang', String, index=True),
                         Column('searchSecondLang', String, index=True),
                         Column('orgFirstLang', String),
                         Column('orgSecondLang', String)
                         )
    clear_mappers()
    mapper(Dictionary, table_object)
    readyForFirstCommit = True
    tableExists = table_object.exists(SQL_ENGINE)
    return Dictionary

def newDict(tablename, searchFirstLang, searchSecondLang, orgFirstLang, orgSecondLang):
    if tablename != currentTablename:
        if readyForFirstCommit:
            sessionCommit()
        get_table_object(tablename)

    session.add(Dictionary(searchFirstLang.decode('utf-8'), searchSecondLang.decode('utf-8'), orgFirstLang.decode('utf-8'), orgSecondLang.decode('utf-8')))

def sessionCommit():
    metadata.create_all(SQL_ENGINE)
    session.commit()


def connectToDatabase(path):
    global SQL_ENGINE, session
    SQL_ENGINE = create_engine("sqlite:///"+path)
    session = sessionmaker()(bind=SQL_ENGINE)


def cli_progress_test(percent, bar_length=20):
    hashes = '#' * int(round(percent * bar_length))
    spaces = ' ' * (bar_length - len(hashes))
    sys.stdout.write("\r[{0}] {1}%".format(hashes + spaces, int(round(percent * 100))))
    sys.stdout.flush()


def main():
    if len(sys.argv) == 1:
        print x.FAIL + "Workflow settings path is missing as argument. Run this script with Alfred with"
        print x.OKBLUE + "dictcc wf:executeParsing" + x.ENDC
        sys.exit()

    dirName = sys.argv[1]

    connectToDatabase(os.path.join(dirName, "Dictionaries.sqlite"))

    settings = ujson.loads(open(os.path.join(dirName, "dictccSettings.json")).read())

    printRemoveInfo = False
    for setting in settings:
        langOrder = setting["languageOrderInDictionaryFile"]
        identifiers = [langOrder[0]["identifier"], langOrder[1]["identifier"]]
        tableName = identifiers[0] + "-" + identifiers[1]
        get_table_object(tableName)
        identifiersUnique = [identifiers[0] + "-" + identifiers[1], identifiers[1] + "-" + identifiers[0]]
        direction = setting["supportedDirection"]
        both = True
        firstLangOnly = False
        if direction != u"both":
            both = False
            firstLangOnly = bool((identifiers.index(direction)+1)%2)

        path = setting["downloadedDictionaryFile"]
        if os.path.exists(path) is False:
            path = os.path.join(dirName, path)
            if os.path.exists(path) is False:
                print x.FAIL + "Downloaded dictionary file for %s doesn't exist. Configure dictccSettings.json correctly." % " ".join(identifiersUnique)
                print "Download dictionary files from " + x.ENDC + "http://www1.dict.cc/translation_file_request.php"
                print x.FAIL + "Get help here " + x.ENDC + "https://github.com/Kavakuo/Dict.cc-Alfred-Workflow#dictcc-alfred-workflow"
                continue

        if both:
            modeName = " ".join(identifiersUnique)
        elif firstLangOnly:
            modeName = identifiersUnique[0]
        else:
            modeName = identifiersUnique[1]

        if tableExists:
            print x.OKBLUE + "Dictionary for %s already exists." % modeName + x.ENDC
            continue

        raw = open(path).read()
        raw = raw.splitlines()
        firstLine = raw[0]

        while firstLine == '' or firstLine[0] == "#":
            raw.pop(0)
            firstLine = raw[0]

        raw = '\n'.join(raw)

        results = re.finditer("(.+?)\t",raw)
        totalCount = len(re.findall(".+?\t",raw))

        count = 0
        print x.HEADER + "Start parsing " + modeName + x.ENDC

        searchFirst = ""
        searchSecond = ""
        orgFirst = ""
        orgSecond = ""
        cli_progress_test(0)
        for a in results:
            if count % 2 == 0:
                searchString = a.group(1)
                replace = [re.finditer("\{.+?\}", a.group(1), flags=re.UNICODE), re.finditer("\[.+?\]", a.group(1), flags=re.UNICODE)]
                for r in replace:
                    for match in r:
                        searchString = searchString.replace(match.group(0), "")
                searchString = searchString.strip()

                searchFirst = searchString
                orgFirst = a.group(1) #german

            else:
                searchString = a.group(1)
                replace = [re.finditer("\{.+?\}", a.group(1), flags=re.UNICODE), re.finditer("\[.+?\]", a.group(1), flags=re.UNICODE)]
                for r in replace:
                    for match in r:
                        searchString = searchString.replace(match.group(0), "")
                searchString = searchString.strip()
                searchSecond = searchString
                orgSecond = a.group(1)
                newDict(tableName,searchFirst, searchSecond, orgFirst, orgSecond)

            count += 1
            if count % 200 == 0:
                cli_progress_test(float(count)/totalCount)

        cli_progress_test(1)
        print " "

        print x.OKBLUE + "Writing to database. This may take a while! The operation won't fail silently. So just be patient, please." + x.ENDC
        sessionCommit()

        if both:
            print x.OKGREEN + "Dictionary tables for %s were generated successfully" % modeName
        if firstLangOnly:
            print x.OKGREEN + "Dictionary tables for %s was generated successfully" % modeName

        printRemoveInfo = True

    if printRemoveInfo:
        print x.OKGREEN + "You can remove the downloaded dictionary files now to save diskspace." + x.ENDC



def getNResultsOfQuery(N, query):
    result = []
    for a in range(N):
        r = query.offset(a).first()
        if r is not None:
            result.append(r)
        else:
            break
    return result

def searchParsedJson(query, firstLangIdentifier, tablename):
    get_table_object(tablename)
    identifiers = tablename.split("-")
    secondLang = bool(identifiers.index(firstLangIdentifier))

    search = query.lower()

    results = []

    if secondLang:
        results += getNResultsOfQuery(30, session.query(Dictionary).filter(Dictionary.searchSecondLang.like(search)))
        n = 30
        if len(results) > 0:
            n = 10
        results += getNResultsOfQuery(n, session.query(Dictionary).filter(Dictionary.searchSecondLang.like("%" + search + "%")))

    else:
        results += getNResultsOfQuery(30, session.query(Dictionary).filter(Dictionary.searchFirstLang.like(search)))
        n = 30
        if len(results) > 0:
            n = 10
        results += getNResultsOfQuery(n, session.query(Dictionary).filter(Dictionary.searchFirstLang.like("%" + search + "%")))


    ids = []

    realResults = []
    for a in results:
        if a.id in ids:
            continue

        ids.append(a.id)

        if secondLang:
            realResults.append({"original":a.orgSecondLang, "translation":a.orgFirstLang})
        else:
            realResults.append({"original": a.orgFirstLang, "translation": a.orgSecondLang})

    return realResults


def sqlTest():
    import time
    connectToDatabase("/Users/Philipp/Desktop/Scripts/AlfredDict/Dictionaries.sqlite")

    get_table_object("de-en")
    print tableExists
    now = time.time()
    result = getNResultsOfQuery(30, session.query(Dictionary).filter(Dictionary.searchSecondLang.like("hallo")))
    print "finished after %s " % str(time.time() - now)
    now = time.time()


    result = getNResultsOfQuery(10, session.query(Dictionary).filter(Dictionary.searchSecondLang.like("%hallo%")))
    print "finished after %s " % str(time.time()-now)
    print len(result)
    #now = time.time()
    #result = session.query(Dictionary).filter(Dictionary.searchFirstLang.like("%a%")).all()
    #print "finished after %s " % str(time.time() - now)


if __name__ == '__main__':
    DEBUG = True
    main()

