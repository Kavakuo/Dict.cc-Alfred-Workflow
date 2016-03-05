Dict.cc Alfred Workflow
===================

This Alfred workflow uses the offline translation databases provided by dict.cc. The configuration is a little bit work, but it is easy to manage.

![Screenshot](http://i.imgur.com/gPe3zAz.jpg)


#Installation


1. Install the workflow.
2. Download the language databases you want from
	http://www1.dict.cc/translation_file_request.php. Only download **"tab-delimited"** versions.
3. Open the workflow folder. Just type `dictcc wf:openworkflow` into Alfred to open this folder or perform a right-click on the workflow in the Alfred settings and select `Reveal in Finder`.
4. Move the downloaded language database file into this folder.
5. Open the `settings.json` file and configure it. See below for Specifiactions. You can open this file by typing  
`dictcc wf:settings` into Alfred.
6. Open the Terminal.app and run the `ParseDictsData.py` script (Don't move the script outside the folder!)  
	`python /path/to/ParseDictsData.py`
7. That's it.

###The `settings.json` file

	[{
		"downloadedDictionaryFile": "[path to file]",
		"languageOrderInDictionaryFile": [{
			"identifier":"de",
			"completeName":"German"
			"icon":"icons/icon.png"
		},{
			"identifier":"en",
			"completeName":"English"
			"icon":"icons/icon.png"
		}],
		"supportedDirection":"both"
	},{
		** second translation configuration goes here (same keys as before) **
	}]

	
* `"downloadedDictionaryFile"`  Key:
	* The file path to the downloaded file from dict.cc (absolute or relative path). If the file is in the same folder, just assign the file name to this key.
* `"languageOrderInDictionaryFile"` Key:
	* The first entry refers to the language, which is on the left side inside the downloaded dictionary file.
		* `"identifier"` see below how this works.
		* `"completeName"` the name of the language. Used by Alfred to show the language modes.
		* `"icon"` An icon which is displayed by Alfred for the translation from this language to the next one. 
	* The second entry is the language on the right side.
		* Same keys as above.
* `"supportedDirection"` Key:
	* If you want to translate in both directions, `"both"` is the value you want. If you just want to translate from English to German, this value should be the identifier of the language you want to translate from. In this example it would be `"en"`.

###How the workflow works
`dictcc` activates the workflow in Alfred. The `settings.json` file is parsed to get the supported translations. To activate a translations the language identifiers are connected with `-`. 

With this command `dictcc en-de` (see the settings.json sample) you activate the English -> German translation for example. If the identifier for `English` would be `eng` and the `German` identifier would be `ger`, the command to activate the English -> German translation is `dictcc eng-ger`.
