
# Sidebar Enhancements

### In other languages

Japanese - <http://taamemo.blogspot.jp/2012/10/sublime-text-2-sidebarenhancements.html?m=1>

Russian - <https://www.youtube.com/watch?v=8I0dJTd58kI&feature=youtu.be&a>

Chinese - <https://github.com/52fisher/SideBarEnhancements>

## Description

### [Sublime Text 3+][] Package, It does NOT WORK with ST2, DOES NOT; Use Sublime Text 3 Please.

Provides enhancements to the operations on Sidebar of Files and Folders for Sublime Text. <http://www.sublimetext.com/>

Notably provides delete as "move to trash", open with.. and a clipboard.

Close, move, open and restore buffers affected by a rename/move command. (even on folders)

Provides the basics: new file/folder, edit, open/run, reveal, find in selected/parent/project, cut, copy, paste, paste in parent, rename, move, delete, refresh....

The not so basic: copy paths as URIs, URLs, content as UTF8, content as <data:uri> base64 ( nice for embedding into CSS! ), copy as tags img/a/script/style, duplicate

Preference to control if a buffer should be closed when affected by a deletion operation.

Allows to display "file modified date" and "file size" on statusbar.

![][]

## Installation

Download or clone the contents of this repository to a folder named exactly as the package name into the Packages/ folder of ST.

Troubleshooting Installation:

If you have problems with the installation, do this:

-   First please note this package only adds a context menu to the "Folders" section and not to the "Open Files" section.
-   Open the package folder. Main menu -\> Preferences -\> Browse Packages.
-   Close Sublime Text.
-   Remove the folder "Packages/SideBarEnhancements"
-   Remove the folder "User/SideBarEnhancements"
-   Navigate one folder up, to "Installed Packages/", check for any instance of SideBarEnhancements and remove it.
-   Open ST, with Package Control go to : Remove Package, check for any instance of SideBarEnhancements and remove it.
-   Restart ST
-   Open ST, check if there is any entry about SideBarEnhancements in Package Control(in sections: "Remove Package" and just in case in "Enable Package")
-   Repeat until you find there no entry about SideBarEnhancements
-   Restart ST
-   Install it.
-   It works

## F12 key

(Please note that from version 2.122104 this package no longer provides the key, you need to manually add it to your sublime-keymap file (see next section))

F12 key allows you to open the current file in browser.

`url_testing` allows you to set the url of your local server, opened via F12

`url_production` allows you to set the url of your production server, opened via ALT+F12

### With absolute paths
-   Right click any file on sidebar and select: "Project -\> Edit Projects Preview URLs"
-   Edit this file, and add your paths and URLs with the following structure:

<!-- -->

	{
		"S:/www/domain.tld":{
			"url_testing":"http://testing",
			"url_production":"http://domain.tld"
		},
		"C:/Users/luna/some/domain2.tld":{
			"url_testing":"http://testing1",
			"url_production":"http://productiontld2"
		}
	}

### With relative paths

Imagine we have a project with the following structure

	Project/ < - root project folder
	Project/libs/
	Project/public/ < - the folder we want to load as "http://localhost/"
	Project/private/
	Project/experimental/ < - other folder we may run as experimental/test in another url "http://experimental/"

Then we create configuration file:

`Project/.sublime/SideBarEnhancements.json`

with content:

	{
		"public/":{
			"url_testing":"http://localhost/",
			"url_production":"http://domain.tld/"
		},
		"experimental/":{
			"url_testing":"http://experimental/",
			"url_production":"http://domain.tld/"
		},
		"":{
			"url_testing":"http://the_url_for_the_project_root/",
			"url_production":"http://the_url_for_the_project_root/"
		}
	}

...

You can create config files `some/folder/.sublime/SideBarEnhancements.json` anywhere.

#### F12 key conflict

On Sublime Text 3 `F12` key is bound to `"goto_definition"` command by default. This package was conflicting with that key, this no longers happens. You need to manually add the keys now: Go to `Preferences -> Package Settings -> Side Bar -> Key Bindings - User` and add any of the following:

		[
			{ "keys": ["f12"],
				"command": "side_bar_open_in_browser" ,
				"args":{"paths":[], "type":"testing", "browser":""}
			},
			{ "keys": ["alt+f12"],
				"command": "side_bar_open_in_browser",
				"args":{"paths":[], "type":"production", "browser":""}
			},
			{
				"keys": ["ctrl+t"],
				"command": "side_bar_new_file2"
			},
			{
				"keys": ["f2"],
				"command": "side_bar_rename"
			},
		]

## Keybinding for Find in paths:

You may wish to add a key for opening "find in paths.."

	[
		{
			"keys": ["f10"],
			"id": "side-bar-find-files",
			"command": "side_bar_find_files_path_containing",
			"args": {
				"paths": []
			}
		}
	]


## Notes on configuring the `Open With` menu:


Definitions file: `User/SideBarEnhancements/Open With/Side Bar.sublime-menu` (note the extra subfolder levels). To open it, right-click on any file in an open project and select `Open With > Edit Applications...`

-   On OSX, the 'application' property simply takes the *name* of an application, to which the file at hand's full path will be passed as if with `open ...`, e.g.: "application": "Google Chrome"
-   On OSX, invoking *shell* commands is NOT supported.

<!-- -->

	//application 1
	{
		"caption": "Photoshop",
		"id": "side-bar-files-open-with-photoshop",
		"command": "side_bar_files_open_with",
		"args": {
			"paths": [],
			"application": "Adobe Photoshop CS5.app", // OSX
			"extensions":"psd|png|jpg|jpeg",  //any file with these extensions
			"args":[]
		}
		"open_automatically" : true // will close the view/tab and launch the application
	},

### Vars on "args" param

- $PATH - The full path to the current file, e. g., C:\Files\Chapter1.txt.
- $PROJECT - The root directory of the current project.
- $DIRNAME - The directory of the current file, e. g., C:\Files.
- $NAME - The name portion of the current file, e. g., Chapter1.txt.
- $EXTENSION - The extension portion of the current file, e. g., txt.

## FAQ

Q: Why the menu is not shown on `Open Files`?

-   It should be mentioned that the package's context menu is only available for files and folders **in a project (section** `Folders` **in the side bar)**, and *not* on the open files listed at the top of the side bar, due to a limitation of ST.

Q: Can the package stop "show preview in a **right** click to a file".

-   No, ​I'm sorry, can't figure out how to prevent it.

## Using the External Libraries

(check each license in project pages)

-   "getImageInfo" to get width and height for images from "bfg-pages". See: <http://code.google.com/p/bfg-pages/>
-   "desktop" to be able to open files with system handlers. See: <http://pypi.python.org/pypi/desktop>
-   "send2trash" to be able to send to the trash instead of deleting for ever!. See: <http://pypi.python.org/pypi/Send2Trash>
-   "hurry.filesize" to be able to format file sizes. See: <http://pypi.python.org/pypi/hurry.filesize/>
-   "Edit.py" ST2/3 Edit Abstraction. See: <http://www.sublimetext.com/forum/viewtopic.php?f=6&t=12551>

## Source-code

<https://github.com/SideBarEnhancements-org/SideBarEnhancements>

## Forum Thread

<http://www.sublimetext.com/forum/viewtopic.php?f=5&t=3331>

# Contributors:

(Thank you so much!)
-   Aleksandar Urosevic
-   bofm
-   Dalibor Simacek
-   Devin Rhode
-   Eric Eldredge
-   Hewei Liu
-   Jeremy Gailor
-   Joao Antunes
-   Leif Ringstad
-   MauriceZ
-   Nick Zaccardi
-   Patrik Göthe
-   Peder Langdal
-   Randy Lai
-   Raphael DDL Oliveira
-   robwala
-   Stephen Horne
-   Sven Axelsson
-   Till Theis
-   Todd Wolfson
-   Tyler Thrailkill
-   Yaroslav Admin

## TODO

<https://github.com/SideBarEnhancements-org/SideBarEnhancements/issues/223>

## License

"None are so hopelessly enslaved as those who falsely believe they are free." Johann Wolfgang von Goethe

Copyright (C) 2014 Tito Bouzout [tito.bouzout@gmail.com][]

This license apply to all the files inside this program unless noted different for some files or portions of code inside these files.

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation. <http://www.gnu.org/licenses/gpl.html>

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see <http://www.gnu.org/licenses/gpl.html>

## Helpful!? Support, Many thanks ^_^


[Donate to support this project.][]

  [Sublime Text 3+]: http://www.sublimetext.com/
  []: https://www.dropbox.com/s/ckz5n2ncn2pxkii/sidebar.png?dl=1
  [desktop]: http://pypi.python.org/pypi/desktop
  [Send2Trash]: http://pypi.python.org/pypi/Send2Trash
  [bfg-pages]: http://code.google.com/p/bfg-pages/
  [tito.bouzout@gmail.com]: tito.bouzout@gmail.com
  [Donate to support this project.]: https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=DD4SL2AHYJGBW
