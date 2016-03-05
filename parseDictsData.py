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
import re, os, sys

DEBUG = False

def cli_progress_test(percent, bar_length=20):
    hashes = '#' * int(round(percent * bar_length))
    spaces = ' ' * (bar_length - len(hashes))
    sys.stdout.write("\r[{0}] {1}%".format(hashes + spaces, int(round(percent * 100))))
    sys.stdout.flush()


def main():
    if len(sys.argv) == 1:
        print "Workflow Settings path is missing. Run this script with Alfred with"
        print "dictcc wf:executeParsing"
        sys.exit()

    dirName = sys.argv[1]
    dictionaryDir = os.path.join(dirName, "Dictionaries")
    if os.path.exists(dictionaryDir) is False:
        os.mkdir(dictionaryDir)

    settings = ujson.loads(open(os.path.join(dirName, "dictccSettings.json")).read())

    for setting in settings:
        langOrder = setting["languageOrderInDictionaryFile"]
        identifiers = [langOrder[0]["identifier"], langOrder[1]["identifier"]]
        identifiersUnique = [identifiers[0] + "-" + identifiers[1], identifiers[1] + "-" + identifiers[0]]
        direction = setting["supportedDirection"]
        both = True
        firstLangOnly = False
        if direction != u"both":
            both = False
            firstLangOnly = bool((identifiers.index(direction)+1)%2)


        firstLangFile = os.path.join(dictionaryDir, identifiersUnique[0]+".json")
        seconLangFile = os.path.join(dictionaryDir, identifiersUnique[1]+".json")

        if both:
            if os.path.exists(firstLangFile) and os.path.exists(seconLangFile):
                print "Parsed files for %s already exist" % " ".join(identifiersUnique)
                continue
        elif firstLangOnly:
            if os.path.exists(firstLangFile):
                print "Parsed file for %s already exist" % identifiersUnique[0]
                continue
        elif firstLangOnly is False:
            if os.path.exists(firstLangFile):
                print "Parsed file for %s already exist" % identifiersUnique[1]
                continue

        path = setting["downloadedDictionaryFile"]
        if os.path.exists(path) is False:
            path = os.path.join(dirName, path)
            if os.path.exists(path) is False:
                print "Downloaded dictionary file for %s doesn't exist. Configure dictccSettings.json correctly." % " ".join(identifiersUnique)
                print "Download dictionary files from http://www1.dict.cc/translation_file_request.php"
                print "Get help here https://github.com/Kavakuo/Dict.cc-Alfred-Workflow#dictcc-alfred-workflow"
                continue

        if both:
            modeName = " ".join(identifiersUnique)
        elif firstLangOnly:
            modeName = identifiersUnique[0]
        else:
            modeName = identifiersUnique[1]

        raw = open(path).read()
        raw = raw.splitlines()
        firstLine = raw[0]

        while firstLine == '' or firstLine[0] == "#":
            raw.pop(0)
            firstLine = raw[0]

        raw = '\n'.join(raw)

        results = re.finditer("(.+?)\t",raw)
        totalCount = len(re.findall(".+?\t",raw))
        de_en = {}
        en_de = {}
        # generated JSON structure:
        # {
        #   "[search without gender and additional info]": {
        #       "org":         "[search with gender]",
        #       "translation": "[translation]"
        #   }
        #
        # }

        count = 0
        temp = ""
        tempSearch = ""
        print "Start parsing " + modeName

        cli_progress_test(0)
        for a in results:
            if count % 2 == 0:
                searchString = a.group(1)
                replace = [re.finditer("\{.+?\}", a.group(1), flags=re.UNICODE), re.finditer("\[.+?\]", a.group(1), flags=re.UNICODE)]
                for r in replace:
                    for match in r:
                        searchString = searchString.replace(match.group(0), "")
                searchString = searchString.strip()

                temp = a.group(1) #german
                tempSearch = searchString
                de_en[searchString] = {"original":a.group(1), "translation":""}
            else:
                searchString = a.group(1)
                replace = [re.finditer("\{.+?\}", a.group(1), flags=re.UNICODE), re.finditer("\[.+?\]", a.group(1), flags=re.UNICODE)]
                for r in replace:
                    for match in r:
                        searchString = searchString.replace(match.group(0), "")
                searchString = searchString.strip()

                de_en[tempSearch]["translation"] = a.group(1)
                en_de[searchString] = {"original":a.group(1), "translation":temp}

            count += 1
            if count % 200 == 0:
                cli_progress_test(float(count)/totalCount)

        cli_progress_test(1)
        print " "

        string = ujson.dumps(de_en)
        f = open(firstLangFile, "w")
        f.write(string)
        f.close()

        string = ujson.dumps(en_de)
        f = open(seconLangFile, "w")
        f.write(string)
        f.close()

        if both:
            print "Dictionary files for %s were generated" % modeName
        if firstLangOnly:
            print "Dictionary file for %s was generated" % modeName

        print "Removing downloaded dictionary file to save diskspace..."
        os.remove(path)



def searchParsedJson(query, jsonDictionary):
    raw = open(jsonDictionary).read()
    raw = ujson.loads(raw)
    search = query.lower()
    search2 = search[0].upper() + search[1:]
    results = []

    if raw.get(search):
        results.append({"original":raw[search]["original"], "translation":raw[search]["translation"]})
        raw.pop(search, None)
    elif raw.get(search2):
        results.append({"original": raw[search2]["original"], "translation": raw[search2]["translation"]})
        raw.pop(search2, None)

    if len(results) > 0 and DEBUG:
        print results[-1]

    if DEBUG:
        print "search"


    count = 0
    for key in raw:
        if count > 30:
            break
        if search in key.lower():
            results.append({"original": raw[key]["original"], "translation": raw[key]["translation"]})
            count += 1
            if DEBUG:
                print results[-1]

    return results


if __name__ == '__main__':
    DEBUG = True
    main()
