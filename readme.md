\*[Sublime Text 3+][] **Package. Install via an updated version of**
[Package Control 2+][]**. Just** DON'T\*\* install manually.

# Sidebar Enhancements

### Translations

Japanese -
http://taamemo.blogspot.jp/2012/10/sublime-text-2-sidebarenhancements.html?m=1

## Description

Provides enhancements to the operations on Sidebar of Files and Folders
for Sublime Text. See: http://www.sublimetext.com/

Notably provides delete as "move to trash", open with.. and a clipboard.
Close, move, open and restore buffers affected by a rename/move command.

Provides the basics: new file/folder, edit, open/run, reveal, find in
selected/parent/project, cut, copy, paste, paste in parent, rename,
move, delete, refresh....

The not so basic: copy paths as URIs, URLs, content as UTF8, content as
data:uri base64 ( nice for embedding into CSS! ), copy as tags
img/a/script/style, duplicate

Preference to control if a buffer should be closed when affected by a
deletion operation.

Allows to display "file modified date" and "file size" on statusbar.

![][]

## Installation

To install SideBarEnhancements, Install Package Control 2 First. See:
https://sublime.wbond.net/installation

Then after restarting, with package control Install this Package.

WARNING: Manual installation:

-   We don't have time to workaround, provide support and follow threads
    of all the possible problems that installing manually can cause.

-   Most users will clone this repo, with sublime opened, which will
    Install the version of the package for ST2 on ST3, if you do this
    with ST3 and opened, the installition is likely screwed up.

-   Install with package control please.

Troubleshooting Installtion:

If you have problems with the installtion, do this:

-   First please note this package only adss a context menu to the "Folders" section and not to the "Open Files" section.

-   Open the package folder. Main menu -\> Preferences -\> Browse
    Packages.

-   Close Sublime Text.

-   Remove the folder "Packages/SideBarEnhancements"

-   Remove the folder "User/SideBarEnhancements"

-   Navigate one folder up, to "Installed Packages/", check for any
    instance of SideBarEnhancements and remove it.

-   Open ST, with Package Control go to : Remove Package, check for any
    instance of SideBarEnhancements and remove it.

-   Restart ST

-   Open ST, check if there is any entry about SideBarEnhancements in
    Package Control(in sections: "Remove Package" and just in case in
    "Enable Package")

-   Repeat until you find there no entry about SideBarEnhancements

-   Restart ST

-   Install it via Package Control.

-   It works

## F12 key

F12 key allows you to open the current file in browser.

`url_testing` allows you to set the url of your local server, opened via
F12

`url_production` allows you to set the url of your production server,
opened via ALT+F12

### With absolute paths

-   Right click any file on sidebar and select: "Project -\> Edit
    Projects Preview URLs"

-   Edit this file, and add your paths and URLs with the following
    structure:

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

ost"\>

		\<skos:prefLabel\>The concepts I like the most\</skos:prefLabel\>

		\<skos:member rdf:resource="\#top\_category1"/\>

		\<skos:member rdf:resource="\#subcategory\_3"/\>


            "url_testing":"http://experimental/",
            "url_production":"http://domain.tld/"
        },
        "":{
            "url_testing":"http://the_url_for_the_project_root/",
            "url_production":"http://the_url_for_the_project_root/"
        }
    }

...

You can create config files
`some/folder/.sublime/SideBarEnhancements.json` anywhere.

#### F12 key conflict

On Sublime Text 3 `F12` key is bound to `"goto_definition"` command by
default. To restore the default behaviour use this workaround.

Go to
`Preferences -> Package Settings -> Side Bar -> Key Bindings - User` and
add the following:

    [
        { "keys": ["f12"],
            "command": "goto_definition"
        },
    ]

## Notes on configuring the `Open With` menu:

Definitions file:
`User/SideBarEnhancements/Open With/Side Bar.sublime-menu` (note the
extra subfolder levels). To open it, right-click on any file in an open
project and select `Open With > Edit Applications...`

-   On OSX, the 'application' property simply takes the *name* of an
    application, to which the file at hand's full path will be passed as
    if with `open ...`, e.g.: "application": "Google Chrome"

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
            "extensions":"psd|png|jpg|jpeg"  //any file with these extensions
        }
        "open_automatically" : true // will close the view/tab and launch the application
    },

## FAQ

Q: Why the menu is not shown on `Open Files`?

-   It should be mentioned that the package's context menu is only
    available for files and folders **in a project (section** `Folders`
    **in the side bar)**, and *not* on the open files listed at the top
    of the side bar, due to a limitation of ST.

Q: Can the package stop "show preview in a **right** click to a file".

-   No, ​I'm sorry, can't figure out how to prevent it.

## Using the External Libraries

-   "getImageInfo" to get width and height for images from "bfg-pages".
    See: http://code.google.com/p/bfg-pages/

-   "desktop" to be able to open files with system handlers. See:
    http://pypi.python.org/pypi/desktop

-   "send2trash" to be able to send to the trash instead of deleting for
    ever!. See: http://pypi.python.org/pypi/Send2Trash

-   "hurry.filesize" to be able to format file sizes. See:
    http://pypi.python.org/pypi/hurry.filesize/

-   "Edit.py" ST2/3 Edit Abstraction. See:
    http://www.sublimetext.com/forum/viewtopic.php?f=6&t=12551

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
    - Till Theis
    - Jeremy Gailor

# Like it? Support

    - https://www.paypal.com/cgi-bin/webscr?cmd=_donations&business=YNNRSS2UJ8P88&lc=UY&item_name=Support%20%20SideBarEnhancements%20Developer&amount=12%2e00&currency_code=USD&bn=PP%2dDonationsBF%3abtn_donateCC_LG%2egif%3aNonHosted

  [Sublime Text 3+]: http://www.sublimetext.com/
  [Package Control 2+]: https://sublime.wbond.net/installation
  []: http://dl.dropbox.com/u/43596449/tito/sublime/SideBar/screenshot.png
