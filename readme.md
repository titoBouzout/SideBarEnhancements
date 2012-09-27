# Description


Provides enhancements to the operations on Side Bar of Files and Folders for Sublime Text 2. See: http://www.sublimetext.com/

Notably provides delete as "move to trash", open with.. a and clipboard. Close, move, open and restore buffers affected by a rename/move command.

Provides the basics: new file/folder, edit, open/run, reveal, find in selected/parent/project, cut, copy, paste, paste in parent, rename, move, delete, refresh....

The not so basic: copy paths as URIs, URLs, content as UTF8, content as data:uri base64 ( nice for embedding into CSS! ), copy as tags img/a/script/style, duplicate


Preference to control if a buffer should be closed when affected by a deletion operation.

Allows to display "file modified date" and "file size" on statusbar.

All commands available for files and folders(when applicable) .

[img]http://dl.dropbox.com/u/43596449/tito/sublime/SideBar/screenshot.png[/img]

<img src="http://dl.dropbox.com/u/43596449/tito/sublime/SideBar/screenshot.png" border="0"/>

# F12 key

F12 key allows you to open the current file in browser.
If you want to add a url to that feature:

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

```url_testing``` allows you to set the url of your local server, opened via F12

```url_production``` allows you to set the url of your production server, opened via ALT+F12

# Notes on configuring the `Open With` menu:

Definitions file:  `User/SidebarEnhancements/Open With/Side Bar.sublime-menu` (note the extra subfolder levels).
To open it, right-click on any file in an open project and select `Open With > Edit Applications...`

- On OSX, the 'application' property simply takes the *name* of an application, to which the file at hand's full path will be passed as if with `open ...`, e.g.: "application": "Google Chrome"
- On OSX, invoking *shell* commands is NOT supported.

# Todo

 * Use a real clipboard integrated with the OS

# Installation

Install this repository via "Package Control" http://wbond.net/sublime_packages/package_control

# FAQ

Q: Uninstall?

 * Follow the instructions here: https://github.com/titoBouzout/SideBarEnhancements/issues/18

Q: Why the menu is not shown on `Open Files`?

- It should be mentioned that the package's context menu is only available for files and folders **in a project (section `Folders` in the side bar)**, and _not_ on the open files listed at the top of the side bar, due to a limitation of ST2.

# Using the External Libraries


 * "getImageInfo" to get width and height for images from "bfg-pages". See: http://code.google.com/p/bfg-pages/
 * "desktop" to be able to open files with system handlers. See: http://pypi.python.org/pypi/desktop
 * "send2trash" to be able to send to the trash instead of deleting for ever!. See: http://pypi.python.org/pypi/Send2Trash
 * "hurry.filesize" to be able to format file sizes. See: http://pypi.python.org/pypi/hurry.filesize/

# Source-code


https://github.com/titoBouzout/SideBarEnhancements

# Forum Thread


http://www.sublimetext.com/forum/viewtopic.php?f=5&t=3331

# Update v1.2:

* Improved: Feature "find advanced -> in paths containing" or CTRL+ALT+F now provides instant search, contribution by @ryecroft, thanks a lot!
* Fix: When only 1 tab is open and setting "close_windows_when_empty" is true. If the user renames or delete the current file will cause the application to close by itself (it will be perceived as a crash but is not).
* New: Add to the command palette useful commands as duplicate, reveal, move, open project file, open in browser, refresh, rename
* New: added keybindings F12 to open in local server, ALT+F12 to open in production server.
* New: Allows to copy the URL of the selected items.
* Improved: When renaming/moving remember the tab position and syntax.
* small fixes:
- Correct display of commands that are available only for projects
- Be sure to return None if there is no open project
- only display a message when using the clipboard if something was copied.

# Update v1.1:

* New: Add boolean preference "confirm_before_deleting" which controls if a the package should ask the user to delete files and folders
* New: When using copy, cut or paste the editor will ask for "replace items" when these items exists. Note: When a folder exists the package will merge the two as in the OS.

# Update v1.0:

* New: Add boolean preference "close_affected_buffers_when_deleting_even_if_dirty" which controls if a buffer should be closed when affected by a deletion operation-

# Update v0.9:


* Minor tweaks and fixes.
* Fix: Re-enable move to trash for OSX
* New: Allow to display "file modified time" and "file size" on statusbar via preferences.
* Fix: Disable of built-in function is now automatic.
* On the way: exclude from project, promote as project folder. ( requires restart to apply changes, looks like there is no way to reload project files.)
* Fix: Many appends of same directory to "sys.path"

# Update v0.8:


* Full review for when the user has selection of multiples items.
* New: Added support for bookmarks and marks for when a view is moved.

# Update v0.7:


* New: After a rename of a file or folder, the affected views will update(reload) to reflect the new location keeping intact content, selections, folded regions and scroll position.
* New: File path search

# Update v0.6:


* Fix: Paste was pasting on parent folder (Misinterpretation of boolean)
* Fix: "Open with" works on Linux
* Improved: Allow case change on Windows when renaming a file or folder
* Improved: Update to "find commands" for version 2134

# Update v0.5:


* Change: Removed "files" prefix from commands.
* New: Ability to copy a path relative to the current view
* New: Ability to "paste in parent"
* New: Ctrl+T will ask for a new file on same folder as current view
* Improved: Context menu open faster

# Update v0.4:


* Fix: "Open / Run" fixed on Linux thanks to project [desktop](http://pypi.python.org/pypi/desktop )
* Improved: "Paste" command copy permission bits, last access time, last modification time, and flags
* Improved: "Delete" command send files to trash thanks to [Send2Trash](http://pypi.python.org/pypi/Send2Trash ) . NOTE: If "Delete" fails to send to trash it will ask for "Permanently Delete" On confirmation it delete the item forever.

# Update v0.3:


* Fixed: Open should run correctly with some strange characters on paths
* New: "Open with.." is enabled and allows to set custom applications for different file extensions.
* New:  "Copy content as Data URI" ( handy for embedding images on CSS files )
* Improved: Copy img tags now add attributes width and height thanks to project [bfg-pages](http://code.google.com/p/bfg-pages/ ) and suggestion from nobleach.

# Update v0.2:


 * Copy paths and names in various formats.
 * Removed license to not conflict with sublime

# Update v0.1:


 * Tweaks here, tweaks there.
 * Renamed repository
 * New: "edit" will open the file with sublime text.
 * New: "open" will call to the command line with the file path
 * New: a disabled "open with" for future use
 * Tweaks: ids to all context elements