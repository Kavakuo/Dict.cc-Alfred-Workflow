
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


# This script uses alfred-workflow by Dean Jackson
# https://github.com/deanishe/alfred-workflow


import workflow, sys
import parseDictsData, ujson, subprocess, os, re


__version__ = '1.1'

def createSettingsFile():
    workflowDataPath = os.getenv("alfred_workflow_data")
    settingsPath = os.path.join(workflowDataPath, "dictccSettings.json")
    if os.path.exists(settingsPath) is False:
        f = open(settingsPath, "w")
        f.write("You need to configure this file.\nLook here https://github.com/Kavakuo/Dict.cc-Alfred-Workflow#dictcc-alfred-workflow for a sample configuration!\nBefore you start delete these lines of text.")
        f.close()

    return settingsPath

def main(wsf):
    continuing = True

    if wf.update_available:
        # Download new version and tell Alfred to install it
        wf.add_item(u'New version available', u'Action this item to install the update', autocomplete=u' wf:update', icon=workflow.ICON_INFO)

    if os.getenv("alfred_workflow_data", None) is None:
        wf.add_item(u'Error occured!', icon=workflow.ICON_ERROR)
        wf.send_feedback()
        return

    workflowDataPath = os.getenv("alfred_workflow_data")
    settingsPath = createSettingsFile()

    query = None
    try:
        settings = ujson.loads(open(settingsPath).read())
    except:
        wf.add_item(u"You need to configure this workflow.", u"Action this item to start the configuration.", autocomplete=u" wf:openSettings", icon=workflow.ICON_WARNING)
        wf.send_feedback()
        continuing = False
        #return

    if len(wf.args):
        query = wf.args[0]
        if len(query) > 0 and query[0] == u" ":
            query = query[1:]
        if query == u'':
            query = None

    langModeId = query
    wantsToSearch = False
    if query and query.find(u" ") != -1:
        langModeId = query[:query.find(u" ")]
        query = query[query.find(u" ")+1:]
        wantsToSearch = True
        if query == u'':
            query = None
            wantsToSearch = False

    if re.search("^\s?wf", str(langModeId)):
        continuing = False
        wf.add_item(u"Open dictccSettings.json", autocomplete=u" wf:openSettings", icon=settingsPath, icontype=u"fileicon", arg=settingsPath, type=u'file')
        wf.add_item(u"Open settings folder", autocomplete=u" wf:folderSettings", icontype=u"filetype", icon=u"public.folder")
        wf.add_item(u"Run parseDictsData.py", autocomplete=u" wf:executeParsing", icon=workflow.ICON_SETTINGS)
        wf.add_item(u"See the documentation", icon=workflow.ICON_INFO, valid=True, arg=u"test")
        wf.add_item(u"Search for updates", icon=workflow.ICON_SYNC, autocomplete=u" wf:update")
        wf.send_feedback()


    items = []
    shouldSearch = False
    currentMode = None

    if continuing:
        for a in settings:
            langOrder = a["languageOrderInDictionaryFile"]
            identifiers = [langOrder[0]["identifier"], langOrder[1]["identifier"]]
            identifiersUnique = [identifiers[0] + u"-" + identifiers[1], identifiers[1] + u"-" + identifiers[0]]
            langOrder[0]["uniqueIdentifier"] = identifiersUnique[0]
            langOrder[1]["uniqueIdentifier"] = identifiersUnique[1]

            langOrder[0]["translationName"] = langOrder[0]["completeName"] + u" -> " + langOrder[1]["completeName"]
            langOrder[1]["translationName"] = langOrder[1]["completeName"] + u" -> " + langOrder[0]["completeName"]

            direction = a["supportedDirection"]

            validModeIdentifier = False
            if direction == u"both":
                if langModeId and langModeId in identifiersUnique:
                    validModeIdentifier = True
            else:
                index = identifiers.index(direction)
                identifiersUnique.pop((index+1)%2)

                if langModeId and langModeId in identifiersUnique:
                    validModeIdentifier = True

            if validModeIdentifier:
                shouldSearch = True
                items = []
                currentMode = langOrder[identifiersUnique.index(langModeId)]
                if os.path.exists(os.path.join(workflowDataPath, "Dictionaries/"+currentMode["uniqueIdentifier"]+".json")) is False:
                    shouldSearch = False
                    items.append(currentMode)
                break
            else:
                if direction == u"both":
                    items += langOrder
                else:
                    items.append(langOrder[identifiers.index(direction)])


        if wantsToSearch and shouldSearch is False:
            wf.add_item(u"Unknown language abriviation", icon=workflow.ICON_WARNING)
            wf.send_feedback()
            return

        elif shouldSearch is False:
            if langModeId:
                def filterKeys(d):
                    return d["uniqueIdentifier"]

                items = wf.filter(langModeId, items, filterKeys, match_on=workflow.MATCH_SUBSTRING ^ workflow.MATCH_STARTSWITH)

            presentHelp = False
            helpIdentifiers = []
            for a in items:
                title = a["translationName"]
                identifier = a["uniqueIdentifier"]
                path = os.path.join(workflowDataPath, "Dictionaries/"+identifier+".json")
                if os.path.exists(path) is False:
                    helpIdentifiers.append(identifier)
                    presentHelp = True
                else:
                    wf.add_item(title, identifier, autocomplete=u" " + identifier + u" ",icon=a["icon"])

            if presentHelp:
                for identifier in helpIdentifiers:
                    wf.add_item(u"Dictionary file for " + identifier + u" is missing", u"You need to run parseDictsData.py", icon=workflow.ICON_WARNING)
                wf.add_item(u"Execute parseDictsData.py to generate the files", autocomplete=u" wf:executeParsing", icon=workflow.ICON_SETTINGS)
                wf.add_item(u"See the documentation", icon=workflow.ICON_INFO, valid=True, arg=u"test")

            if len(items) == 0:
                wf.add_item(u"Unknown language abriviation", icon=workflow.ICON_WARNING)

            wf.send_feedback()


        elif shouldSearch:
            if wantsToSearch is False:
                wf.add_item(u"Search term is missing", icon=workflow.ICON_WARNING)
                wf.send_feedback()
                return

            jsonPath = os.path.join(workflowDataPath, "Dictionaries/"+currentMode["uniqueIdentifier"] + ".json")
            results = parseDictsData.searchParsedJson(query, jsonPath)
            if len(results) > 1:
                firstResult = [results[0]]
                results = firstResult + wf.filter(query, results[1:], lambda x:x["original"])

            for a in results:
                wf.add_item(a["original"], a["translation"],icon=currentMode["icon"])
            wf.send_feedback()
            return


def openSettings():
    subprocess.call(['open', createSettingsFile()])
    return 'Opening workflow settings...'

def openFolder():
    subprocess.call(['open', os.path.dirname(createSettingsFile())])
    return "Open settings Folder..."

def openTerminalAndStartParsing():
    scriptDir = os.path.abspath(os.path.dirname(__file__))
    script = os.path.join(scriptDir, "openTerminal.scpt")

    settingsFolder = "\"%s\"" % os.path.dirname(createSettingsFile())
    cmd = "python \"%s\" %s" % (os.path.join(scriptDir, "parseDictsData.py"), settingsFolder)

    subprocess.call(['osascript', script, cmd])

    return "Open terminal..."



if __name__ == '__main__':
    wf = workflow.Workflow(update_settings={'github_slug': "Kavakuo/Dict.cc-Alfred-Workflow", 'version':__version__})
    wf.magic_prefix = ' wf:'
    wf.magic_arguments['openSettings'] = openSettings
    wf.magic_arguments['folderSettings'] = openFolder
    wf.magic_arguments['executeParsing'] = openTerminalAndStartParsing
    sys.exit(wf.run(main))