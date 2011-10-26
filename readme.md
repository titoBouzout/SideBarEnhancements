Description
------------------

Provides enhancements to the operations on Side Bar of Files and Folders for Sublime Text 2. See: http://www.sublimetext.com/

Notably provides delete as "move to trash", open with and clipboard.

Provides the basics: new file/folder, edit, open/run, reveal, find in selected/parent/project, cut, copy, paste, paste in parent, rename, move, delete, refresh....

The not so basic: copy paths as URIs, URLs, content as UTF8, content as data:uri base64 ( nice for embedding into CSS! ), copy as tags img/a/script/style, duplicate, open with...

All commands available for files and folders(when applicable) .

[img]http://dl.dropbox.com/u/43596449/tito/sublime/SideBar/screenshot.png[/img]

<img src="http://dl.dropbox.com/u/43596449/tito/sublime/SideBar/screenshot.png" border="0"/>

Todo
------------------

 * Use a real clipboard integrated with the OS
 * Move should ask for the folder with a real OS prompt
 * Allow to quickly "hide from sidebar" folders and files using built-in settings for projects.
 * Lock and Unlock files.
 * Compress items

Bugs
------------------

 * "Open with.." may not work on Mac

Installation
------------------

 * Sublime already provides some file operations. This plugin provides enhanced versions of the same operations. Then, there is at least two "New File.." menus. In order to remove the built-in menus: Open the file "Sublime Text 2/Packages/Default/Side Bar.sublime-menu" and comment everything using a comment block like this: /* here file contents */
 * Install this repository via "Package Control" http://wbond.net/sublime_packages/package_control
 * Test !
 * Consider make a contribution <3

Using the External Libraries
------------------

 * "getImageInfo" to get width and height for images from "bfg-pages". See: http://code.google.com/p/bfg-pages/
 * "desktop" to be able to open files with system handlers. See: http://pypi.python.org/pypi/desktop
 * "send2trash" to be able to send to the trash instead of deleting for ever!. See: http://pypi.python.org/pypi/Send2Trash

Source-code
------------------

https://github.com/titoBouzout/SideBarEnhancements

Forum Thread
------------------

http://www.sublimetext.com/forum/viewtopic.php?f=5&t=3331

Update v0.8:
------------------

* Full review for when the user has selection of multiples items.
* New: Added support for bookmarks and marks for when a view is moved.

Update v0.7:
------------------

* New: After a rename of a file or folder, the affected views will update(reload) to reflect the new location keeping intact content, selections, folded regions and scroll position.
* New: File path search

Update v0.6:
------------------

* Fix: Paste was pasting on parent folder (Misinterpretation of boolean)
* Fix: "Open with" works on Linux
* Improved: Allow case change on Windows when renaming a file or folder
* Improved: Update to "find commands" for version 2134

Update v0.5:
------------------

* Change: Removed "files" prefix from commands.
* New: Ability to copy a path relative to the current view
* New: Ability to "paste in parent"
* New: Ctrl+T will ask for a new file on same folder as current view
* Improved: Context menu open faster

Update v0.4:
------------------

* Fix: "Open / Run" fixed on Linux thanks to project [desktop](http://pypi.python.org/pypi/desktop )
* Improved: "Paste" command copy permission bits, last access time, last modification time, and flags
* Improved: "Delete" command send files to trash thanks to [Send2Trash](http://pypi.python.org/pypi/Send2Trash ) . NOTE: If "Delete" fails to send to trash it will ask for "Permanently Delete" On confirmation it delete the item forever.

Update v0.3:
------------------

* Fixed: Open should run correctly with some strange characters on paths
* New: "Open with.." is enabled and allows to set custom applications for different file extensions.
* New:  "Copy content as Data URI" ( handy for embedding images on CSS files )
* Improved: Copy img tags now add attributes width and height thanks to project [bfg-pages](http://code.google.com/p/bfg-pages/ ) and suggestion from nobleach.

Update v0.2:
------------------

 * Copy paths and names in various formats.
 * Removed license to not conflict with sublime

Update v0.1:
------------------

 * Tweaks here, tweaks there.
 * Renamed repository
 * New: "edit" will open the file with sublime text.
 * New: "open" will call to the command line with the file path
 * New: a disabled "open with" for future use
 * Tweaks: ids to all context elements

Contribute
------------------

[Consider make a contribution](https://www.paypal.com/cgi-bin/webscr?cmd=_donations&business=extensiondevelopment%40gmail%2ecom&lc=UY&item_name=Tito&item_number=sublime%2dtext%2dside%2dbar%2dplugin&currency_code=USD&bn=PP%2dDonationsBF%3abtn_donateCC_LG%2egif%3aNonHosted )