# Sidebar Enhancements

## Description

Provides enhancements to the operations on Sidebar of Files and Folders for Sublime Text. See: http://www.sublimetext.com/

Notably provides delete as "move to trash", open with.. and a clipboard. Close, move, open and restore buffers affected by a rename/move command.

Provides the basics: new file/folder, edit, open/run, reveal, find in selected/parent/project, cut, copy, paste, paste in parent, rename, move, delete, refresh....

The not so basic: copy paths as URIs, URLs, content as UTF8, content as data:uri base64 ( nice for embedding into CSS! ), copy as tags img/a/script/style, duplicate

Preference to control if a buffer should be closed when affected by a deletion operation.

Allows to display "file modified date" and "file size" on statusbar.

![Screenshot](http://dl.dropbox.com/u/43596449/tito/sublime/SideBar/screenshot.png)

## Installation

To install SideBarEnhancements, [download](https://github.com/titoBouzout/SideBarEnhancements/archive/st3.zip) or clone this repo into the SublimeText ```Packages``` directory and ```git checkout st3```.  A restart of SublimeText might be nessecary to complete the install.

```
cd Packages/
git clone -b st3 git://github.com/titoBouzout/SideBarEnhancements.git "SideBarEnhancements"
```



## F12 key

F12 key allows you to open the current file in browser.

```url_testing``` allows you to set the url of your local server, opened via F12

```url_production``` allows you to set the url of your production server, opened via ALT+F12

### With absolute paths

 * Right click any file on sidebar and select: "Project -> Edit Projects Preview URLs"
 * Edit this file, and add your paths and URLs with the following structure:

```
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
```

### With relative paths

Imagine we have a project with the following structure

```
Project/ < - root project folder
Project/libs/
Project/public/ < - the folder we want to load as "http://localhost/"
Project/private/
Project/experimental/ < - other folder we may run as experimental/test in another url "http://experimental/"
```

Then we create configuration file:

`Project/.sublime/SideBarEnhancements.json`

with content:

```
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
```
...

You can create config files ```some/folder/.sublime/SideBarEnhancements.json``` anywhere.

## Notes on configuring the `Open With` menu:

Definitions file:  `User/SideBarEnhancements/Open With/Side Bar.sublime-menu` (note the extra subfolder levels).
To open it, right-click on any file in an open project and select `Open With > Edit Applications...`

- On OSX, the 'application' property simply takes the *name* of an application, to which the file at hand's full path will be passed as if with `open ...`, e.g.: "application": "Google Chrome"
- On OSX, invoking *shell* commands is NOT supported.

## FAQ

Q: Why the menu is not shown on `Open Files`?

- It should be mentioned that the package's context menu is only available for files and folders **in a project (section `Folders` in the side bar)**, and _not_ on the open files listed at the top of the side bar, due to a limitation of ST.

## Using the External Libraries

 * "getImageInfo" to get width and height for images from "bfg-pages". See: http://code.google.com/p/bfg-pages/
 * "desktop" to be able to open files with system handlers. See: http://pypi.python.org/pypi/desktop
 * "send2trash" to be able to send to the trash instead of deleting for ever!. See: http://pypi.python.org/pypi/Send2Trash
 * "hurry.filesize" to be able to format file sizes. See: http://pypi.python.org/pypi/hurry.filesize/

## Source-code

https://github.com/titoBouzout/SideBarEnhancements

## Forum Thread

http://www.sublimetext.com/forum/viewtopic.php?f=5&t=3331

# Contributors:

	- Leif Ringstad
	- Sven Axelsson
	- Dalibor Simacek
	- Stephen Horne
	- Eric Eldredge
