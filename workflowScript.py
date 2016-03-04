
import workflow, sys
import parseDictsData, ujson, subprocess


__version__ = '1.0'

def main(wsf):

    if wf.update_available:
        # Download new version and tell Alfred to install it
        wf.add_item(u'New version available',
                    u'Action this item to install the update',
                    autocomplete=u' wf:update',
                    icon=workflow.ICON_INFO)

    query = None
    settings = ujson.loads(open("settings.json").read())
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


    items = []
    shouldSearch = False
    currentMode = None
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

        for a in items:
            title = a["translationName"]
            identifier = a["uniqueIdentifier"]
            wf.add_item(title, identifier, autocomplete=u" " + identifier + u" ",icon=a["icon"])

        if len(items) == 0:
            wf.add_item(u"Unknown language abriviation", icon=workflow.ICON_WARNING)

        wf.send_feedback()
        return

    elif shouldSearch:
        if wantsToSearch is False:
            wf.add_item(u"Search term is missing", icon=workflow.ICON_WARNING)
            wf.send_feedback()
            return

        results = parseDictsData.searchParsedJson(query, "Dictionaries/"+currentMode["uniqueIdentifier"] + ".json")
        if len(results) > 1:
            firstResult = [results[0]]
            results = firstResult + wf.filter(query, results[1:], lambda x:x["original"])

        for a in results:
            wf.add_item(a["original"], a["translation"],icon=currentMode["icon"])
        wf.send_feedback()
        return


def opensettings():
    subprocess.call(['open', "settings.json"])
    return 'Opening workflow settings...'



if __name__ == '__main__':
    wf = workflow.Workflow(update_settings={'github_slug': "Kavakuo/Dict.cc-Alfred-Workflow", 'version':__version__})
    wf.magic_prefix = ' wf:'
    wf.magic_arguments['settings'] = opensettings
    sys.exit(wf.run(main))