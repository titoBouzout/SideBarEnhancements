Update 2.151010

* add option "statusbar_modified_time_locale" to avoid broken locales on Windows

Update 2.010905

* "Open in browser", "mass rename" and "empty" runs now in own thread
* Always initialize to default settings (in case users hack the package and remove some preference)

Update 2.010405

* rename and move runs now threaded
* "progress indicators" or "doing something" for deleting, duplicate, pasting,  moving, renaming
* do not "edit" open in a ST view/tab binary files (example when duplicating, etc)
* "Find File Named" fix for OSX
* Rename-/Move-dialog initial selection does not includes part of file-extension for files with multiple extensions
* Fix bug with "open with applications" method signature changed

Update 2.122104

* Somewhat refactor to file "SideBarAPI.py" with the classes SideBarItem, SideBarSelection, SideBarProject
* moved statusbar functionality to main py file
* remove "changelog" file, in favor of this readme
* remove "license" file, in favor of this readme
* removed conflicting keys!

Update 2.0.4

* paste now runs threaded.
* on windows delete files with big file names.

Update 2.0.3

* copy image cant' copy image sizes
* fix canary <https://github.com/titoBouzout/SideBarEnhancements/commit/0d23f3e10650ec8e3792cd7a7f0ceaec2ae84fcb>
* Apply patch for ubuntu encrypted folder bug. <https://github.com/hsoft/send2trash/issues/1#issuecomment-31734060>
* open in default browser OSX
* Relative vs absolute in project folders
* Allow mass rename of folders and files <https://github.com/titoBouzout/SideBarEnhancements/commit/dbdaaffa4a53411b1d39337f7ceee6ecef9b73cb>
* correctly open folders in a new window on mac os x

Update 2.0.2

* fix instant search (begin edit, end edit mess)..
* rename of "dirty" view, does not carry changes.
* rename of view, does not carry undo/redo history.
* reveal on windows on a folder, will open the folder, not reveal the folder.
* fix.. reveal does not work with "," in path names
* fix.. a project folder can't be removed via context menu if the project was not saved.
* browser preview supports relative urls, and multiple configuration files a la ".htaccess"

Update 2.0.1

* remove some obsolete code
* refactor some functions
* solve encoding mess
* Fix for when packages\_path is a link
* fix open with..
* copy url command
* exclude from project
* promote as project folder
* no value on browser will use default browser
* statusbar functions fixes
* fix open/run command windows
* hide default menus
* for each window, locate the focused tab in sidebar at startup
* Lazy load sendtotrash, desktop.
* 2nd fix \#92
* improves open in new window command

Update from v1.2 to.. ST3:

* An incredible amount of fixes, corrections and small tweaks, /documented/ via commit messages.

Update v1.2:

* Improved: Feature "find advanced -\> in paths containing" or CTRL+ALT+F now provides instant search, contribution by @ryecroft, thanks a lot!
* Fix: When only 1 tab is open and setting "close\_windows\_when\_empty" is true. If the user renames or delete the current file will cause the application to close by itself (it will be perceived as a crash but is not).
* New: Add to the command palette useful commands as duplicate, reveal, move, open project file, open in browser, refresh, rename
* New: added keybindings F12 to open in local server, ALT+F12 to open in production server.
* New: Allows to copy the URL of the selected items.
* Improved: When renaming/moving remember the tab position and syntax.
* small fixes:
* Correct display of commands that are available only for projects
* Be sure to return None if there is no open project
* only display a message when using the clipboard if something was copied.

Update v1.1:

* New: Add boolean preference "confirm\_before\_deleting" which controls if a the package should ask the user to delete files and folders
* New: When using copy, cut or paste the editor will ask for "replace items" when these items exists. Note: When a folder exists the package will merge the two as in the OS.

Update v1.0:

* New: Add boolean preference "close\_affected\_buffers\_when\_deleting\_even\_if\_dirty" which controls if a buffer should be closed when affected by a deletion operation-

Update v0.9:

* Minor tweaks and fixes.
* Fix: Re-enable move to trash for OSX
* New: Allow to display "file modified time" and "file size" on statusbar via preferences.
* Fix: Disable of built-in function is now automatic.
* On the way: exclude from project, promote as project folder. ( requires restart to apply changes, looks like there is no way to reload project files.)
* Fix: Many appends of same directory to "sys.path"

Update v0.8:

* Full review for when the user has selection of multiples items.
* New: Added support for bookmarks and marks for when a view is moved.

Update v0.7:

* New: After a rename of a file or folder, the affected views will update(reload) to reflect the new location keeping intact content, selections, folded regions and scroll position.
* New: File path search

Update v0.6:

* Fix: Paste was pasting on parent folder (Misinterpretation of boolean)
* Fix: "Open with" works on Linux
* Improved: Allow case change on Windows when renaming a file or folder
* Improved: Update to "find commands" for version 2134

Update v0.5:

* Change: Removed "files" prefix from commands.
* New: Ability to copy a path relative to the current view
* New: Ability to "paste in parent"
* New: Ctrl+T will ask for a new file on same folder as current view
* Improved: Context menu open faster

Update v0.4:

* Fix: "Open / Run" fixed on Linux thanks to project [desktop](http://pypi.python.org/pypi/desktop)
* Improved: "Paste" command copy permission bits, last access time, last modification time, and flags
* Improved: "Delete" command send files to trash thanks to [Send2Trash](http://pypi.python.org/pypi/Send2Trash) . NOTE: If "Delete" fails to send to trash it will ask for "Permanently Delete" On confirmation it delete the item forever.

Update v0.3:

* Fixed: Open should run correctly with some strange characters on paths
* New: "Open with.." is enabled and allows to set custom applications for different file extensions.
* New: "Copy content as Data URI" ( handy for embedding images on CSS files )
* Improved: Copy img tags now add attributes width and height thanks to project [bfg-pages](http://code.google.com/p/bfg-pages) and suggestion from @nobleach.

Update v0.2:

* Copy paths and names in various formats.
* Removed license to not conflict with sublime

Update v0.1:

* Tweaks here, tweaks there.
* Renamed repository
* New: "edit" will open the file with sublime text.
* New: "open" will call to the command line with the file path
* New: a disabled "open with" for future use
* Tweaks: ids to all context elements
