Dict.cc Alfred Workflow
===================

This Alfred workflow uses the offline translation databases provided by dict.cc. The configuration is a little bit work, but it is easy to manage.

####Features:

* Offline translation with dictionaries powered by dict.cc
* Highly flexible, integrate as many language packs as you want
* Easy to setup

####A little bit hidden features:

* Copy the translated word to the clipboard by actioning it
* Copy the word in the origin language to the clipboard by actioning it with `cmd` as modifier


![Screenshot](http://i.imgur.com/7kwcDCu.png)


#Installation

1. Install the workflow.
2. Download the language databases you want from
	http://www1.dict.cc/translation_file_request.php. Only download **"tab-delimited"** versions.
3. Open the workflow folder. Just type `dictcc wf:folderSettings` into Alfred to open this folder.
4. Move the downloaded language database file(s) into this folder.
5. Open the `dictccSettings.json` file (same folder) and configure it. See below for specifiactions. You can open this file by typing
`dictcc wf:openSettings` into Alfred.
6. Last but not least run the `parseDictsData.py` script. To do this type `dictcc wf:executeParsing` into Alfred. A new Terminal window opens and the necessary operations are performed.
7. That's it.

###The `dictccSettings.json` file

	[{
		"downloadedDictionaryFile": "[path to file]",
		"languageOrderInDictionaryFile": [{
			"identifier":"de",
			"completeName":"German",
			"icon":"icons/icon.png"
		},{
			"identifier":"en",
			"completeName":"English",
			"icon":"icons/icon.png"
		}],
		"supportedDirection":"both"
	},{
		** second translation configuration goes here (same keys as before) **
	}]

	
* `"downloadedDictionaryFile"` Key:
	* The file path to the downloaded file from dict.cc (absolute or relative path). If the file is in the same folder as the `dictccSettings.json` file, just assign the file name to this key.
* `"languageOrderInDictionaryFile"` Key:
	* The first entry refers to the language, which is on the left side inside the downloaded dictionary file.
		* `"identifier"` see below how this works.
		* `"completeName"` the name of the language. Used by Alfred to show the language modes.
		* `"icon"` An icon which is displayed by Alfred for the translation from this language to the other.
	* The second entry is the language on the right side.
		* Same keys as above.
* `"supportedDirection"` Key:
	* If you want to translate in both directions, `"both"` is the value you want. If you just want to translate from English to German, this value should be the identifier of the language you want to translate from. In this example it would be `"en"`.

###How the workflow works
`dictcc` activates the workflow in Alfred. The `settings.json` file is parsed to get the supported translations. To activate a translations the language identifiers are connected with `-`. 

With this command `dictcc en-de` (see the settings.json sample) you activate the English -> German translation for example. If the identifier for `English` would be `eng` and the `German` identifier would be `ger`, the command to activate the English -> German translation is `dictcc eng-ger`.
