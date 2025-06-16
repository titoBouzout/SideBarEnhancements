# Side Bar Enhancements

## Description

Sidebar menu for Sublime Text. This Package notably provides

- delete as "move to trash",
- a clipboard, and
- files affected by a rename/move command are closed, renamed/moved, and re-opened again.

## Default Menu Items

SideBarEnhancements' `Side Bar.sublime-menu` context menu resource file is designed to
fully replace both the `Side Bar.sublime-menu` and `Side Bar Mount Point.sublime-menu` context menus from the `Default` Package.  When you are ready to do so, you can suppress
the appearance of the menu items from these two `Default` context menus by creating
these two empty files in your `<data_path>/Packages/Default/` directory.  If the
`<data_path>/Packages/Default/` directory does not already exist, you can create it
with the help of "Preferences -> Browse Packages".

- `<data_path>/Packages/Default/Side Bar Mount Point.sublime-menu`
- `<data_path>/Packages/Default/Side Bar.sublime-menu`

Note:  "Unpromote" replaces the "Remove Folder from Project" menu item from the
`Side Bar Mount Point.sublime-menu` context menu, and accomplishes the same thing
without deleting the folder.

"Promote" (its "opposite") takes any folder visible in the FOLDERS trees and ALSO
makes it a Mount Point (i.e. top-level folder), in addition to the top-level folders
that were already in the project.

## Pre Simplification

After 13-Jul-2023, this Package was simplified.  If you wish to use (or go back to)
the Package before this simplification, do so with the following steps:

1. Uninstall/Remove SideBarEnhancements
2. open
   https://github.com/titoBouzout/SideBarEnhancements/tree/289fa49d005352c47cfb9ba36656794dade7ced3
3. Code(green button) -> Download Zip
4. Sublime Text -> Main menu bar -> Preferences -> Browse Packages
5. Unzip to "Packages/SideBarEnhancements/" (make sure is NOT double as
   "Packages/SideBarEnhancements/SideBarEnhancements")
6. Restart

## External Libraries Used

- "desktop" for opening files with system handlers. See:
  <http://pypi.python.org/pypi/desktop>
- "send2trash" for sending to trash instead of deleting forever!.
  See: <http://pypi.python.org/pypi/Send2Trash>
- "hurry.filesize" for formatting file sizes. See:
  <http://pypi.python.org/pypi/hurry.filesize/>
- "Edit.py" ST2/3 Edit Abstraction. See:
  <http://www.sublimetext.com/forum/viewtopic.php?f=6&t=12551>

## Source-code

<https://github.com/titoBouzout/SideBarEnhancements>

## License

"None are so hopelessly enslaved as those who falsely believe they are free."<br>
—Johann Wolfgang von Goethe

Copyright (C) 2011-2024 Tito Bouzout

This license applies to all the files inside this Package unless noted differently
for some files or portions of code inside these files.

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation. <http://www.gnu.org/licenses/gpl.html>

This program is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with
this program. If not, see <http://www.gnu.org/licenses/gpl.html>
