# Sidebar Enhancements

### In other languages

Japanese - <http://taamemo.blogspot.jp/2012/10/sublime-text-2-sidebarenhancements.html?m=1>
Russian - <https://www.youtube.com/watch?v=8I0dJTd58kI&feature=youtu.be&a>

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

<https://github.com/titoBouzout/SideBarEnhancements>

## Forum Thread

<http://www.sublimetext.com/forum/viewtopic.php?f=5&t=3331>

# Contributors:

(Thank you so much!)
-   bofm
-   Dalibor Simacek
-   Devin Rhode
-   Eric Eldredge
-   Hewei Liu
-   Jeremy Gailor
-   Joao Antunes
-   Leif Ringstad
-   Nick Zaccardi
-   Patrik Göthe
-   Randy Lai
-   Raphael DDL Oliveira
-   robwala
-   Stephen Horne
-   Sven Axelsson
-   Till Theis
-   Todd Wolfson
-   Tyler Thrailkill
-   Yaroslav Admin
-   Aleksandar Urosevic
-   MauriceZ

## TODO

<https://github.com/titoBouzout/SideBarEnhancements/issues/223>

## Change Log

Update 2.151010

-   add option "statusbar_modified_time_locale" to avoid broken locales on Windows

Update 2.010905

-   "Open in browser", "mass rename" and "empty" runs now in own thread
-   Always initialize to default settings (in case users hack the package and remove some preference)

Update 2.010405

-   rename and move runs now threaded
-   "progress indicators" or "doing something" for deleting, duplicate, pasting,  moving, renaming
-   do not "edit" open in a ST view/tab binary files (example when duplicating, etc)
-   "Find File Named" fix for OSX
-   Rename-/Move-dialog initial selection does not includes part of file-extension for files with multiple extensions
-   Fix bug with "open with applications" method signature changed

Update 2.122104

-   Somewhat refactor to file "SideBarAPI.py" with the classes SideBarItem, SideBarSelection, SideBarProject
-   moved statusbar functionality to main py file
-   remove "changelog" file, in favor of this readme
-   remove "license" file, in favor of this readme
-   removed conflicting keys!

Update 2.0.4

-   paste now runs threaded.
-   on windows delete files with big file names.

Update 2.0.3

-   copy image cant' copy image sizes
-   fix canary <https://github.com/titoBouzout/SideBarEnhancements/commit/0d23f3e10650ec8e3792cd7a7f0ceaec2ae84fcb>
-   Apply patch for ubuntu encrypted folder bug. <https://github.com/hsoft/send2trash/issues/1#issuecomment-31734060>
-   open in default browser OSX
-   Relative vs absolute in project folders
-   Allow mass rename of folders and files <https://github.com/titoBouzout/SideBarEnhancements/commit/dbdaaffa4a53411b1d39337f7ceee6ecef9b73cb>
-   correctly open folders in a new window on mac os x

Update 2.0.2

-   fix instant search (begin edit, end edit mess)..
-   rename of "dirty" view, does not carry changes.
-   rename of view, does not carry undo/redo history.
-   reveal on windows on a folder, will open the folder, not reveal the folder.
-   fix.. reveal does not work with "," in path names
-   fix.. a project folder can't be removed via context menu if the project was not saved.
-   browser preview supports relative urls, and multiple configuration files a la ".htaccess"

Update 2.0.1

-   remove some obsolete code
-   refactor some functions
-   solve encoding mess
-   Fix for when packages\_path is a link
-   fix open with..
-   copy url command
-   exclude from project
-   promote as project folder
-   no value on browser will use default browser
-   statusbar functions fixes
-   fix open/run command windows
-   hide default menus
-   for each window, locate the focused tab in sidebar at startup
-   Lazy load sendtotrash, desktop.
-   2nd fix \#92
-   improves open in new window command

Update from v1.2 to.. ST3:

-   An incredible amount of fixes, corrections and small tweaks, /documented/ via commit messages.

Update v1.2:

-   Improved: Feature "find advanced -\> in paths containing" or CTRL+ALT+F now provides instant search, contribution by @ryecroft, thanks a lot!
-   Fix: When only 1 tab is open and setting "close\_windows\_when\_empty" is true. If the user renames or delete the current file will cause the application to close by itself (it will be perceived as a crash but is not).
-   New: Add to the command palette useful commands as duplicate, reveal, move, open project file, open in browser, refresh, rename
-   New: added keybindings F12 to open in local server, ALT+F12 to open in production server.
-   New: Allows to copy the URL of the selected items.
-   Improved: When renaming/moving remember the tab position and syntax.
-   small fixes:
-   Correct display of commands that are available only for projects
-   Be sure to return None if there is no open project
-   only display a message when using the clipboard if something was copied.

Update v1.1:

-   New: Add boolean preference "confirm\_before\_deleting" which controls if a the package should ask the user to delete files and folders
-   New: When using copy, cut or paste the editor will ask for "replace items" when these items exists. Note: When a folder exists the package will merge the two as in the OS.

Update v1.0:

-   New: Add boolean preference "close\_affected\_buffers\_when\_deleting\_even\_if\_dirty" which controls if a buffer should be closed when affected by a deletion operation-

Update v0.9:

-   Minor tweaks and fixes.
-   Fix: Re-enable move to trash for OSX
-   New: Allow to display "file modified time" and "file size" on statusbar via preferences.
-   Fix: Disable of built-in function is now automatic.
-   On the way: exclude from project, promote as project folder. ( requires restart to apply changes, looks like there is no way to reload project files.)
-   Fix: Many appends of same directory to "sys.path"

Update v0.8:

-   Full review for when the user has selection of multiples items.
-   New: Added support for bookmarks and marks for when a view is moved.

Update v0.7:

-   New: After a rename of a file or folder, the affected views will update(reload) to reflect the new location keeping intact content, selections, folded regions and scroll position.
-   New: File path search

Update v0.6:

-   Fix: Paste was pasting on parent folder (Misinterpretation of boolean)
-   Fix: "Open with" works on Linux
-   Improved: Allow case change on Windows when renaming a file or folder
-   Improved: Update to "find commands" for version 2134

Update v0.5:

-   Change: Removed "files" prefix from commands.
-   New: Ability to copy a path relative to the current view
-   New: Ability to "paste in parent"
-   New: Ctrl+T will ask for a new file on same folder as current view
-   Improved: Context menu open faster

Update v0.4:

-   Fix: "Open / Run" fixed on Linux thanks to project [desktop][]
-   Improved: "Paste" command copy permission bits, last access time, last modification time, and flags
-   Improved: "Delete" command send files to trash thanks to [Send2Trash][] . NOTE: If "Delete" fails to send to trash it will ask for "Permanently Delete" On confirmation it delete the item forever.

Update v0.3:

-   Fixed: Open should run correctly with some strange characters on paths
-   New: "Open with.." is enabled and allows to set custom applications for different file extensions.
-   New: "Copy content as Data URI" ( handy for embedding images on CSS files )
-   Improved: Copy img tags now add attributes width and height thanks to project [bfg-pages][] and suggestion from @nobleach.

Update v0.2:

-   Copy paths and names in various formats.
-   Removed license to not conflict with sublime

Update v0.1:

-   Tweaks here, tweaks there.
-   Renamed repository
-   New: "edit" will open the file with sublime text.
-   New: "open" will call to the command line with the file path
-   New: a disabled "open with" for future use
-   Tweaks: ids to all context elements

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
  []: http://dl.dropbox.com/u/43596449/tito/sublime/SideBar/screenshot.png
  [desktop]: http://pypi.python.org/pypi/desktop
  [Send2Trash]: http://pypi.python.org/pypi/Send2Trash
  [bfg-pages]: http://code.google.com/p/bfg-pages/
  [tito.bouzout@gmail.com]: tito.bouzout@gmail.com
  [Donate to support this project.]: https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=DD4SL2AHYJGBW