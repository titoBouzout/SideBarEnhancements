Sublime Text
------------------

This repository holds a Sublime Text 2 Plugin. See: http://www.sublimetext.com/

Description
------------------

Provides enhancements to the operations on Side Bar of Files and Folders.

Currently provides: new file/folder, edit, open/run, open with, reveal, find in selected/parent/project, cut, copy, paste, duplicate, rename, move, delete, refresh.... and many copy as text, binary and tags formats. All commands available for files and folders.

<img src="http://dl.dropbox.com/u/43596449/tito/sublime/SideBar/screenshot.png" border="0"/>

Todo
------------------
 
 * Use a real clipboard integrated with the OS
 * Move should ask for the folder with a real OS prompt
 * Allow to quickly "hide" folders and files using built-in settings for projects.

Bugs
------------------
 * "Open with.." may not work on Linux

Limitations
------------------

* Only operates with one item at the same time ( ex: you can't deleted multiple selected files at the same time )

Installation
------------------

* Sublime already provides some file operations. This plugin provides enhanced versions of the same operations. Then, there is at least two "New File.." menus. In order to remove the built-in menus: Open the file "Sublime Text 2/Packages/Default/Side Bar.sublime-menu" and comment everything using a comment block like this: /* here file contents */
* Install this repository via "Package Control" http://wbond.net/sublime_packages/package_control
* Test !
* Consider make a donation <3

Using the External Libraries
------------------
 * "getImageInfo" to get width and height for images from "bfg-pages". See: http://code.google.com/p/bfg-pages/
 * "desktop" to be able to open files with system handlers. See: http://code.google.com/p/bfg-pages/
 * "send2trash" to be able to send to the trash instead of deleting for ever!. See: http://pypi.python.org/pypi/Send2Trash

Source-code
------------------

https://github.com/titoBouzout/SideBarEnhancements

Forum Thread
------------------

http://www.sublimetext.com/forum/viewtopic.php?f=5&t=3331

Contribute
------------------

https://www.paypal.com/cgi-bin/webscr?cmd=_donations&business=extensiondevelopment%40gmail%2ecom&lc=UY&item_name=Tito&item_number=sublime%2dtext%2dside%2dbar%2dplugin&currency_code=USD&bn=PP%2dDonationsBF%3abtn_donateCC_LG%2egif%3aNonHosted
