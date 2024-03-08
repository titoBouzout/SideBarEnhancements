# coding=utf8

import sublime
import sublime_plugin

import os
import shutil
import threading
import time
import re
import subprocess
import platform

from .edit.Edit import Edit
from .hurry.filesize import size as hurry_size

try:
    from urllib import unquote as urlunquote
except ImportError:
    from urllib.parse import unquote as urlunquote

from .SideBarAPI import SideBarItem, SideBarSelection, SideBarProject

Pref = {}
s = {}
Cache = {}


def cli(command):
    info = subprocess.STARTUPINFO()
    info.dwFlags = subprocess.STARTF_USESHOWWINDOW
    info.wShowWindow = 0
    p = subprocess.Popen(
        command,
        startupinfo=info,
        stdin=subprocess.PIPE,
        stderr=subprocess.PIPE,
        stdout=subprocess.PIPE,
        shell=platform.system() == "Windows" or os.name == "nt",
    )
    stdout, stderr = p.communicate()
    try:
        p.kill()
    except:
        pass

    p = {"stderr": stderr, "stdout": stdout, "returncode": p.returncode}
    return p


def CACHED_SELECTION(paths=[]):
    if Cache.cached:
        return Cache.cached
    else:
        return SideBarSelection(paths)


def escapeCMDWindows(string):
    return string.replace("^", "^^")


class Pref:
    def load(self):
        pass


def plugin_loaded():
    global Pref, s
    s = sublime.load_settings("Side Bar.sublime-settings")
    Pref = Pref()
    Pref.load()
    s.clear_on_change("reload")
    s.add_on_change("reload", lambda: Pref.load())


def Window(window=None):
    return window if window else sublime.active_window()


def expandVars(path):
    for k, v in list(os.environ.items()):
        path = path.replace("%" + k + "%", v).replace("%" + k.lower() + "%", v)
    return path


def window_set_status(key, name=""):
    for window in sublime.windows():
        for view in window.views():
            view.set_status("SideBar-" + key, name)


class Object:
    pass


class Cache:
    pass


Cache = Cache()
Cache.cached = False


class aaaaaSideBarCommand(sublime_plugin.WindowCommand):
    def run(self, paths=[]):
        pass

    def is_visible(self, paths=[]):  # <- WORKS AS AN ONPOPUPSHOWN
        Cache.cached = SideBarSelection(paths)
        return False


class SideBarNewFileCommand(sublime_plugin.WindowCommand):
    def run(self, paths=[], name=""):
        import functools

        Window().run_command("hide_panel")
        view = Window().show_input_panel(
            "File Name:",
            name,
            functools.partial(self.on_done, paths, False),
            None,
            None,
        )
        Window().focus_view(view)

    def on_done(self, paths, relative_to_project, name):
        _paths = paths
        _paths = SideBarSelection(_paths).getSelectedDirectoriesOrDirnames()
        if not _paths:
            _paths = SideBarProject().getDirectories()
            if _paths:
                _paths = [SideBarItem(_paths[0], False)]
        if not _paths:
            Window().new_file()
        else:
            for item in _paths:
                item = SideBarItem(item.join(name), False)
                if item.exists():
                    sublime.error_message(
                        "Unable to create file, file or folder exists."
                    )
                    self.run(paths, name)
                    return
                else:
                    try:
                        item.create()
                        item.edit()
                    except:
                        sublime.error_message(
                            "Unable to create file:\n\n" + item.path()
                        )
                        self.run(paths, name)
                        return
            SideBarProject().refresh()


class SideBarNewFile2Command(sublime_plugin.WindowCommand):
    def run(self, paths=[], name=""):
        import functools

        Window().run_command("hide_panel")
        view = Window().show_input_panel(
            "File Name:",
            name,
            functools.partial(SideBarNewFileCommand(Window()).on_done, paths, True),
            None,
            None,
        )
        Window().focus_view(view)


class SideBarNewDirectory2Command(sublime_plugin.WindowCommand):
    def run(self, paths=[], name=""):
        import functools

        Window().run_command("hide_panel")
        view = Window().show_input_panel(
            "Folder Name:",
            name,
            functools.partial(
                SideBarNewDirectoryCommand(Window()).on_done, paths, True
            ),
            None,
            None,
        )
        Window().focus_view(view)


class SideBarNewDirectoryCommand(sublime_plugin.WindowCommand):
    def run(self, paths=[], name=""):
        import functools

        Window().run_command("hide_panel")
        view = Window().show_input_panel(
            "Folder Name:",
            name,
            functools.partial(self.on_done, paths, False),
            None,
            None,
        )
        Window().focus_view(view)

    def on_done(self, paths, relative_to_project, name):
        _paths = paths
        _paths = SideBarSelection(_paths).getSelectedDirectoriesOrDirnames()

        for item in _paths:
            item = SideBarItem(item.join(name), True)
            if item.exists():
                sublime.error_message("Unable to create folder, folder or file exists.")
                self.run(paths, name)
                return
            else:
                item.create()
                if not item.exists():
                    sublime.error_message("Unable to create folder:\n\n" + item.path())
                    self.run(paths, name)
                    return
        SideBarProject().refresh()

    def is_enabled(self, paths=[]):
        return CACHED_SELECTION(paths).len() > 0


class SideBarEditCommand(sublime_plugin.WindowCommand):
    def run(self, paths=[]):
        for item in SideBarSelection(paths).getSelectedFiles():
            item.edit()

    def is_enabled(self, paths=[]):
        return CACHED_SELECTION(paths).hasFiles()


class SideBarEditToRightCommand(sublime_plugin.WindowCommand):
    def run(self, paths=[]):
        window = Window()
        window.run_command(
            "set_layout",
            {
                "cols": [0.0, 0.5, 1.0],
                "rows": [0.0, 1.0],
                "cells": [[0, 0, 1, 1], [1, 0, 2, 1]],
            },
        )
        window.focus_group(1)
        for item in SideBarSelection(paths).getSelectedFiles():
            view = item.edit()
            window.set_view_index(view, 1, 0)

    def is_enabled(self, paths=[]):
        return CACHED_SELECTION(paths).hasFiles()


class SideBarOpenCommand(sublime_plugin.WindowCommand):
    def run(self, paths=[]):
        for item in SideBarSelection(paths).getSelectedItems():
            item.open(s.get("use_powershell", True), s.get("use_command", ""))

    def is_enabled(self, paths=[]):
        return CACHED_SELECTION(paths).len() > 0


class SideBarFindInSelectedCommand(sublime_plugin.WindowCommand):
    def run(self, paths=[]):
        window = Window()
        views = []
        for view in window.views():
            if view.name() == "Find Results":
                views.append(view)
        for view in views:
            view.close()

        window = Window()
        views = []
        for view in window.views():
            if view.name() == "Find Results":
                Window().focus_view(view)

                content = view.substr(sublime.Region(0, view.size()))
                _view = Window().new_file()

                _view.settings().set("auto_indent", False)
                _view.run_command("insert", {"characters": content})
                _view.settings().erase("auto_indent")

                # the space at the end of the name prevents it from being reused by Sublime Text
                # it looks like instead of keeping an internal refrence they just look at the view name -__-
                _view.set_name("Find Results ")
                _view.set_syntax_file("Packages/Default/Find Results.hidden-tmLanguage")
                _view.sel().clear()
                for sel in view.sel():
                    _view.sel().add(sel)
                _view.set_scratch(True)
                views.append(view)

        for view in views:
            view.close()

        # fill form
        items = []
        for item in SideBarSelection(paths).getSelectedItemsWithoutChildItems():
            items.append(item.path())
        Window().run_command("hide_panel")
        Window().run_command(
            "show_panel", {"panel": "find_in_files", "where": ",".join(items)}
        )

    def is_enabled(self, paths=[]):
        return CACHED_SELECTION(paths).len() > 0


Object.sidebar_instant_search_id = 0


class SideBarFindFilesPathContainingCommand(sublime_plugin.WindowCommand):
    def run(self, paths=[]):
        if paths == [] and SideBarProject().getDirectories():
            paths = SideBarProject().getDirectories()
        else:
            paths = [
                item.path()
                for item in SideBarSelection(paths).getSelectedDirectoriesOrDirnames()
            ]
        if paths == []:
            return
        view = Window().new_file()
        view.settings().set("word_wrap", False)
        view.set_name("Instant File Search")
        view.set_syntax_file(
            "Packages/SideBarEnhancements/SideBar Results.sublime-syntax"
        )
        view.set_scratch(True)
        view.run_command("insert", {"characters": "Type to search: "})
        view.sel().clear()
        view.sel().add(sublime.Region(16, 16))
        view.settings().set("sidebar_instant_search_paths", paths)


class SideBarFindFilesPathContainingViewListener(sublime_plugin.EventListener):
    def on_modified(self, view):
        view.settings().has(
            "sidebar_instant_search_paths"
        )  # for some reason the first call in some conditions returns true
        # but not the next one WTH xD
        if view.settings().has("sidebar_instant_search_paths"):
            searchTerm = (
                view.substr(view.line(0)).replace("Type to search:", "").strip()
            )
            if searchTerm and Object.sidebar_instant_search_id != searchTerm:
                SideBarFindFilesPathContainingSearchThread(view, searchTerm).start()
            elif not searchTerm:
                view.set_name("Instant File Search")


class SideBarFindFilesPathContainingSearchThread(threading.Thread):
    def __init__(self, view, searchTerm):
        self.view = view
        self.searchTerm = searchTerm
        threading.Thread.__init__(self)

    def run(self):
        if Object.sidebar_instant_search_id == self.searchTerm:
            return
        searchTerm = self.searchTerm
        Object.sidebar_instant_search_id = searchTerm
        view = self.view

        paths = view.settings().get("sidebar_instant_search_paths")
        self.ignore_paths = view.settings().get("file_exclude_patterns", [])
        try:
            self.searchTermRegExp = re.compile(searchTerm, re.I | re.U)
            self.match_function = self.match_regexp
            search_type = "REGEXP"
        except:
            self.match_function = self.match_string
            search_type = "LITERAL"

        if Object.sidebar_instant_search_id == searchTerm:
            total = 0
            highlight_from = 0
            match_result = ""
            match_result += "Type to search: " + searchTerm + "\n"
            find = self.find
            for item in SideBarSelection(paths).getSelectedDirectoriesOrDirnames():
                self.files = []
                self.num_files = 0
                find(item.path())
                match_result += "\n"
                length = len(self.files)
                if length > 1:
                    match_result += str(length) + " matches"
                elif length > 0:
                    match_result += "1 match"
                else:
                    match_result += "No match"
                match_result += (
                    " in "
                    + str(self.num_files)
                    + ' files for term "'
                    + searchTerm
                    + '" using '
                    + search_type
                    + ' under \n"'
                    + item.path()
                    + '"\n\n'
                )
                if highlight_from == 0:
                    highlight_from = len(match_result)
                match_result += "\n".join(self.files)
                total += length
            match_result += "\n"

            if Object.sidebar_instant_search_id == searchTerm:
                sel = view.sel()
                position = sel[0].begin()
                if position > 16 + len(searchTerm):
                    position = 16 + len(searchTerm)

                view.run_command(
                    "side_bar_enhancements_write_to_view",
                    {
                        "content": match_result,
                        "position": position,
                        "searchTerm": searchTerm,
                    },
                )

                view.set_name(searchTerm + " - IFS")
                if Object.sidebar_instant_search_id == searchTerm:
                    view.erase_regions("sidebar_search_instant_highlight")
                    if total < 5000 and len(searchTerm) > 1:
                        if search_type == "REGEXP":
                            regions = [
                                item
                                for item in view.find_all(
                                    searchTerm, sublime.IGNORECASE
                                )
                                if item.begin() >= highlight_from
                            ]
                        else:
                            regions = [
                                item
                                for item in view.find_all(
                                    searchTerm, sublime.LITERAL | sublime.IGNORECASE
                                )
                                if item.begin() >= highlight_from
                            ]
                        if Object.sidebar_instant_search_id == searchTerm:
                            view.add_regions(
                                "sidebar_search_instant_highlight",
                                regions,
                                "entity.name.function",
                                "",
                                sublime.PERSISTENT
                                | sublime.DRAW_SQUIGGLY_UNDERLINE
                                | sublime.DRAW_NO_FILL
                                | sublime.DRAW_NO_OUTLINE
                                | sublime.DRAW_EMPTY_AS_OVERWRITE,
                            )

    def find(self, path):
        if os.path.isfile(path) or os.path.islink(path):
            self.num_files = self.num_files + 1
            if self.match_function(path):
                self.files.append(path)
        elif os.path.isdir(path):
            for content in os.listdir(path):
                file = os.path.join(path, content)
                if os.path.isfile(file) or os.path.islink(file):
                    self.num_files = self.num_files + 1
                    if self.match_function(file):
                        self.files.append(file)
                else:
                    self.find(file)

    def match_regexp(self, path):
        return self.searchTermRegExp.search(path) and not [
            1 for s in self.ignore_paths if s in path
        ]

    def match_string(self, path):
        return self.searchTerm in path and not [
            1 for s in self.ignore_paths if s in path
        ]


class SideBarEnhancementsWriteToViewCommand(sublime_plugin.TextCommand):
    def run(self, edit, content, position, searchTerm):
        if Object.sidebar_instant_search_id == searchTerm:
            view = self.view
            view.replace(edit, sublime.Region(0, view.size()), content)
            view.sel().clear()
            view.sel().add(sublime.Region(position, position))
            view.end_edit(edit)


class SideBarCutCommand(sublime_plugin.WindowCommand):
    def run(self, paths=[]):
        s = sublime.load_settings("SideBarEnhancements/Clipboard.sublime-settings")
        items = []
        for item in SideBarSelection(paths).getSelectedItemsWithoutChildItems():
            items.append(item.path())

        if len(items) > 0:
            s.set("cut", "\n".join(items))
            s.set("copy", "")
            if len(items) > 1:
                sublime.status_message("Items cut")
            else:
                sublime.status_message("Item cut")

    def is_enabled(self, paths=[]):
        return (
            CACHED_SELECTION(paths).len() > 0
            and CACHED_SELECTION(paths).hasProjectDirectories() is False
        )


class SideBarCopyCommand(sublime_plugin.WindowCommand):
    def run(self, paths=[]):
        s = sublime.load_settings("SideBarEnhancements/Clipboard.sublime-settings")
        items = []
        for item in SideBarSelection(paths).getSelectedItemsWithoutChildItems():
            items.append(item.path())

        if len(items) > 0:
            s.set("cut", "")
            s.set("copy", "\n".join(items))
            if len(items) > 1:
                sublime.status_message("Items copied")
            else:
                sublime.status_message("Item copied")

    def is_enabled(self, paths=[]):
        return CACHED_SELECTION(paths).len() > 0


class SideBarPasteCommand(sublime_plugin.WindowCommand):
    def run(self, paths=[], test="True", replace="False"):
        key = "paste-" + str(time.time())
        SideBarPasteThread(paths, test, replace, key).start()

    def is_enabled(self, paths=[]):
        s = sublime.load_settings("SideBarEnhancements/Clipboard.sublime-settings")
        return (s.get("cut", "") + s.get("copy", "")) != "" and len(
            CACHED_SELECTION(paths).getSelectedDirectoriesOrDirnames()
        ) == 1


class SideBarPasteThread(threading.Thread):
    def __init__(self, paths=[], test="True", replace="False", key=""):
        self.paths = paths
        self.test = test
        self.replace = replace
        self.key = key
        threading.Thread.__init__(self)

    def run(self):
        SideBarPasteCommand2(Window()).run(
            self.paths, self.test, self.replace, self.key
        )


class SideBarPasteCommand2(sublime_plugin.WindowCommand):
    def run(self, paths=[], test="True", replace="False", key=""):
        window_set_status(key, "Pasting…")

        s = sublime.load_settings("SideBarEnhancements/Clipboard.sublime-settings")

        cut = s.get("cut", "")
        copy = s.get("copy", "")

        already_exists_paths = []

        if SideBarSelection(paths).len() > 0:
            location = SideBarSelection(paths).getSelectedItems()[0].path()

            if os.path.isdir(location) is False:
                location = SideBarItem(os.path.dirname(location), True)
            else:
                location = SideBarItem(location, True)

            if cut != "":
                cut = cut.split("\n")
                for path in cut:
                    path = SideBarItem(path, os.path.isdir(path))
                    new = os.path.join(location.path(), path.name())
                    if test == "True" and os.path.exists(new):
                        already_exists_paths.append(new)
                    elif test == "False":
                        if os.path.exists(new) and replace == "False":
                            pass
                        else:
                            try:
                                if not path.move(new, replace == "True"):
                                    window_set_status(key, "")
                                    sublime.error_message(
                                        "Unable to cut and paste, destination exists."
                                    )
                                    return
                            except:
                                window_set_status(key, "")
                                sublime.error_message(
                                    "Unable to move:\n\n"
                                    + path.path()
                                    + "\n\nto\n\n"
                                    + new
                                )
                                return

            if copy != "":
                copy = copy.split("\n")
                for path in copy:
                    path = SideBarItem(path, os.path.isdir(path))
                    new = os.path.join(location.path(), path.name())
                    if test == "True" and os.path.exists(new):
                        already_exists_paths.append(new)
                    elif test == "False":
                        if os.path.exists(new) and replace == "False":
                            pass
                        else:
                            try:
                                if not path.copy(new, replace == "True"):
                                    window_set_status(key, "")
                                    sublime.error_message(
                                        "Unable to copy and paste, destination exists."
                                    )
                                    return
                            except:
                                window_set_status(key, "")
                                sublime.error_message(
                                    "Unable to copy:\n\n"
                                    + path.path()
                                    + "\n\nto\n\n"
                                    + new
                                )
                                return

            if test == "True" and len(already_exists_paths):
                self.confirm(paths, already_exists_paths, key)
            elif test == "True" and not len(already_exists_paths):
                SideBarPasteThread(paths, "False", "False", key).start()
            elif test == "False":
                cut = s.set("cut", "")
                SideBarProject().refresh()
                window_set_status(key, "")
        else:
            window_set_status(key, "")

    def confirm(self, paths, data, key):
        import functools

        window = Window()
        window.show_input_panel("BUG! xD", "", "", None, None)
        window.run_command("hide_panel")

        yes = []
        yes.append("Yes, Replace the following items:")
        for item in data:
            yes.append(SideBarItem(item, os.path.isdir(item)).pathWithoutProject())

        no = []
        no.append("No")
        no.append("Continue without replacing")

        while len(no) != len(yes):
            no.append("ST3 BUG xD")

        window.show_quick_panel([yes, no], functools.partial(self.on_done, paths, key))

    def on_done(self, paths, key, result):
        window_set_status(key, "")
        if result != -1:
            if result == 0:
                SideBarPasteThread(paths, "False", "True", key).start()
            else:
                SideBarPasteThread(paths, "False", "False", key).start()


class SideBarCopyNameCommand(sublime_plugin.WindowCommand):
    def run(self, paths=[]):
        items = []
        for item in SideBarSelection(paths).getSelectedItems():
            items.append(item.name())

        if len(items) > 0:
            sublime.set_clipboard("\n".join(items))
            if len(items) > 1:
                sublime.status_message("Items copied")
            else:
                sublime.status_message("Item copied")

    def is_enabled(self, paths=[]):
        return CACHED_SELECTION(paths).len() > 0


class SideBarCopyNameEncodedCommand(sublime_plugin.WindowCommand):
    def run(self, paths=[]):
        items = []
        for item in SideBarSelection(paths).getSelectedItems():
            items.append(item.nameEncoded())

        if len(items) > 0:
            sublime.set_clipboard("\n".join(items))
            if len(items) > 1:
                sublime.status_message("Items copied")
            else:
                sublime.status_message("Item copied")

    def is_enabled(self, paths=[]):
        return CACHED_SELECTION(paths).len() > 0


class SideBarCopyPathRelativeFromProjectEncodedCommand(sublime_plugin.WindowCommand):
    def run(self, paths=[]):
        items = []
        for item in SideBarSelection(paths).getSelectedItems():
            items.append(item.pathRelativeFromProjectEncoded())

        if len(items) > 0:
            sublime.set_clipboard("\n".join(items))
            if len(items) > 1:
                sublime.status_message("Items copied")
            else:
                sublime.status_message("Item copied")

    def is_enabled(self, paths=[]):
        return (
            CACHED_SELECTION(paths).len() > 0
            and CACHED_SELECTION(paths).hasItemsUnderProject()
        )


class SideBarCopyContentBase64Command(sublime_plugin.WindowCommand):
    def run(self, paths=[]):
        items = []
        for item in SideBarSelection(paths).getSelectedFiles():
            items.append(item.contentBase64())

        if len(items) > 0:
            sublime.set_clipboard("\n".join(items))
            if len(items) > 1:
                sublime.status_message("Items content copied")
            else:
                sublime.status_message("Item content copied")

    def is_enabled(self, paths=[]):
        return CACHED_SELECTION(paths).hasFiles()


class SideBarDuplicateCommand(sublime_plugin.WindowCommand):
    def run(self, paths=[], new=False):
        import functools

        Window().run_command("hide_panel")
        view = Window().show_input_panel(
            "Duplicate As:",
            new or SideBarSelection(paths).getSelectedItems()[0].path(),
            functools.partial(
                self.on_done, SideBarSelection(paths).getSelectedItems()[0].path()
            ),
            None,
            None,
        )
        Window().focus_view(view)

        view.sel().clear()
        view.sel().add(
            sublime.Region(
                view.size() - len(SideBarSelection(paths).getSelectedItems()[0].name()),
                view.size()
                - len(SideBarSelection(paths).getSelectedItems()[0].extension()),
            )
        )

    def on_done(self, old, new):
        key = "duplicate-" + str(time.time())
        SideBarDuplicateThread(old, new, key).start()

    def is_enabled(self, paths=[]):
        return (
            CACHED_SELECTION(paths).len() == 1
            and CACHED_SELECTION(paths).hasProjectDirectories() is False
        )


class SideBarDuplicateThread(threading.Thread):
    def __init__(self, old, new, key):
        self.old = old
        self.new = new
        self.key = key
        threading.Thread.__init__(self)

    def run(self):
        old = self.old
        new = self.new
        key = self.key
        window_set_status(key, "Duplicating…")

        item = SideBarItem(old, os.path.isdir(old))
        try:
            if not item.copy(new):
                window_set_status(key, "")
                if SideBarItem(new, os.path.isdir(new)).overwrite():
                    self.run()
                else:
                    SideBarDuplicateCommand(Window()).run([old], new)
                return
        except:
            window_set_status(key, "")
            sublime.error_message("Unable to copy:\n\n" + old + "\n\nto\n\n" + new)
            SideBarDuplicateCommand(Window()).run([old], new)
            return
        item = SideBarItem(new, os.path.isdir(new))
        if item.isFile():
            item.edit()
        SideBarProject().refresh()
        window_set_status(key, "")


class SideBarRenameCommand(sublime_plugin.WindowCommand):
    def run(self, paths=[], newLeaf=False):
        import functools

        branch, leaf = os.path.split(
            SideBarSelection(paths).getSelectedItems()[0].path()
        )
        Window().run_command("hide_panel")
        view = Window().show_input_panel(
            "New Name:",
            newLeaf or leaf,
            functools.partial(
                self.on_done,
                SideBarSelection(paths).getSelectedItems()[0].path(),
                branch,
            ),
            None,
            None,
        )
        Window().focus_view(view)

        view.sel().clear()
        view.sel().add(
            sublime.Region(
                view.size() - len(SideBarSelection(paths).getSelectedItems()[0].name()),
                view.size()
                - len(SideBarSelection(paths).getSelectedItems()[0].extension()),
            )
        )

    def on_done(self, old, branch, leaf):
        key = "rename-" + str(time.time())
        SideBarRenameThread(old, branch, leaf, key).start()

    def is_enabled(self, paths=[]):
        return (
            CACHED_SELECTION(paths).len() == 1
            and CACHED_SELECTION(paths).hasProjectDirectories() is False
        )


class SideBarRenameThread(threading.Thread):
    def __init__(self, old, branch, leaf, key):
        self.old = old
        self.branch = branch
        self.leaf = leaf
        self.key = key
        threading.Thread.__init__(self)

    def run(self):
        old = self.old
        branch = self.branch
        leaf = self.leaf
        key = self.key
        window_set_status(key, "Renaming…")

        Window().run_command("hide_panel")
        leaf = leaf.strip()
        new = os.path.join(branch, leaf)
        item = SideBarItem(old, os.path.isdir(old))
        try:
            if not item.move(new):
                if SideBarItem(new, os.path.isdir(new)).overwrite():
                    self.run()
                else:
                    window_set_status(key, "")
                    SideBarRenameCommand(Window()).run([old], leaf)
        except:
            window_set_status(key, "")
            sublime.error_message("Unable to rename:\n\n" + old + "\n\nto\n\n" + new)
            SideBarRenameCommand(Window()).run([old], leaf)
            raise
            return
        SideBarProject().refresh()
        window_set_status(key, "")


class SideBarMassRenameCommand(sublime_plugin.WindowCommand):
    def run(self, paths=[]):
        import functools

        Window().run_command("hide_panel")
        view = Window().show_input_panel(
            "Find:", "", functools.partial(self.on_find, paths), None, None
        )
        Window().focus_view(view)

    def on_find(self, paths, find):
        if not find:
            return
        import functools

        Window().run_command("hide_panel")
        view = Window().show_input_panel(
            "Replace:", "", functools.partial(self.on_replace, paths, find), None, None
        )
        Window().focus_view(view)

    def on_replace(self, paths, find, replace):
        key = "mass-renaming-" + str(time.time())
        SideBarMassRenameThread(paths, find, replace, key).start()

    def is_enabled(self, paths=[]):
        return CACHED_SELECTION(paths).len() > 0


class SideBarMassRenameThread(threading.Thread):
    def __init__(self, paths, find, replace, key):
        self.paths = paths
        self.find = find
        self.replace = replace
        self.key = key
        threading.Thread.__init__(self)

    def run(self):
        paths = self.paths
        find = self.find
        replace = self.replace
        key = self.key

        if find == "":
            return None
        else:
            window_set_status(key, "Mass renaming…")

            to_rename_or_move = []
            for item in SideBarSelection(paths).getSelectedItemsWithoutChildItems():
                self.recurse(item.path(), to_rename_or_move)
            to_rename_or_move.sort()
            to_rename_or_move.reverse()
            for item in to_rename_or_move:
                if find in item:
                    origin = SideBarItem(item, os.path.isdir(item))
                    destination = SideBarItem(
                        origin.pathProject()
                        + ""
                        + (origin.pathWithoutProject().replace(find, replace)),
                        os.path.isdir(item),
                    )
                    origin.move(destination.path())

            SideBarProject().refresh()
            window_set_status(key, "")

    def recurse(self, path, paths):
        if os.path.isfile(path) or os.path.islink(path):
            paths.append(path)
        else:
            for content in os.listdir(path):
                file = os.path.join(path, content)
                if os.path.isfile(file) or os.path.islink(file):
                    paths.append(file)
                else:
                    self.recurse(file, paths)
            paths.append(path)


class SideBarMoveCommand(sublime_plugin.WindowCommand):
    def run(self, paths=[], new=False):
        import functools

        Window().run_command("hide_panel")
        view = Window().show_input_panel(
            "New Location:",
            new or SideBarSelection(paths).getSelectedItems()[0].path(),
            functools.partial(
                self.on_done, SideBarSelection(paths).getSelectedItems()[0].path()
            ),
            None,
            None,
        )
        Window().focus_view(view)

        view.sel().clear()
        view.sel().add(
            sublime.Region(
                view.size() - len(SideBarSelection(paths).getSelectedItems()[0].name()),
                view.size()
                - len(SideBarSelection(paths).getSelectedItems()[0].extension()),
            )
        )

    def on_done(self, old, new):
        key = "move-" + str(time.time())
        SideBarMoveThread(old, new, key).start()

    def is_enabled(self, paths=[]):
        return (
            CACHED_SELECTION(paths).len() == 1
            and CACHED_SELECTION(paths).hasProjectDirectories() is False
        )


class SideBarMoveThread(threading.Thread):
    def __init__(self, old, new, key):
        self.old = old
        self.new = new
        self.key = key
        threading.Thread.__init__(self)

    def run(self):
        old = self.old
        new = self.new
        key = self.key
        window_set_status(key, "Moving…")

        item = SideBarItem(old, os.path.isdir(old))
        try:
            if not item.move(new):
                if SideBarItem(new, os.path.isdir(new)).overwrite():
                    self.run()
                else:
                    window_set_status(key, "")
                    SideBarMoveCommand(Window()).run([old], new)
                return
        except:
            window_set_status(key, "")
            sublime.error_message("Unable to move:\n\n" + old + "\n\nto\n\n" + new)
            SideBarMoveCommand(Window()).run([old], new)
            raise
            return
        SideBarProject().refresh()
        window_set_status(key, "")


class SideBarDeleteThread(threading.Thread):
    def __init__(self, paths):
        self.paths = paths
        threading.Thread.__init__(self)

    def run(self):
        SideBarDeleteCommand(Window())._delete_threaded(self.paths)


class SideBarDeleteCommand(sublime_plugin.WindowCommand):
    def run(self, paths=[], confirmed="False"):
        if confirmed == "False":
            if sublime.platform() == "osx":
                if sublime.ok_cancel_dialog("Delete the selected items?"):
                    self.run(paths, "True")
            else:
                self.confirm(
                    [
                        item.path()
                        for item in SideBarSelection(paths).getSelectedItems()
                    ],
                    [
                        item.pathWithoutProject()
                        for item in SideBarSelection(paths).getSelectedItems()
                    ],
                )
        else:
            SideBarDeleteThread(paths).start()

    def _delete_threaded(self, paths):
        key = "delete-" + str(time.time())
        window_set_status(key, "Deleting…")
        try:
            from .send2trash import send2trash

            for item in SideBarSelection(paths).getSelectedItemsWithoutChildItems():
                item.closeViews()
                send2trash(item.path())
            SideBarProject().refresh()
        except:
            if sublime.ok_cancel_dialog(
                "There is no trash bin, permanently delete?", "Yes, Permanent Deletion"
            ):
                for item in SideBarSelection(paths).getSelectedItemsWithoutChildItems():
                    item.closeViews()
                    if sublime.platform() == "windows":
                        try:
                            # this is for deleting "large path names"
                            self.remove("\\\\?\\" + item.path())
                        except:
                            # this is for deleting network paths
                            self.remove(item.path())

                    else:
                        self.remove(item.path())
                SideBarProject().refresh()
        window_set_status(key, "")

    def confirm(self, paths, display_paths):
        import functools

        window = Window()
        window.show_input_panel("BUG!", "", "", None, None)
        window.run_command("hide_panel")

        yes = []
        yes.append("Yes, delete the selected items.")
        for item in display_paths:
            yes.append(item)

        no = []
        no.append("No")
        no.append("Cancel the operation.")

        while len(no) != len(yes):
            no.append("")

        if sublime.platform() == "osx":
            sublime.set_timeout(
                lambda: window.show_quick_panel(
                    [yes, no], functools.partial(self.on_confirm, paths)
                ),
                200,
            )
        else:
            window.show_quick_panel(
                [yes, no], functools.partial(self.on_confirm, paths)
            )

    def on_confirm(self, paths, result):
        if result != -1:
            if result == 0:
                self.run(paths, "True")

    def on_done(self, old, new):
        item = SideBarItem(new, os.path.isdir(new))
        item.closeViews()
        if sublime.platform() == "windows":
            self.remove("\\\\?\\" + new)
        else:
            self.remove(new)
        SideBarProject().refresh()

    def remove(self, path):
        if os.path.isfile(path) or os.path.islink(path):
            self.remove_safe_file(path)
        else:
            for content in os.listdir(path):
                file = os.path.join(path, content)
                if os.path.isfile(file) or os.path.islink(file):
                    self.remove_safe_file(file)
                else:
                    self.remove(file)
            self.remove_safe_dir(path)

    def remove_safe_file(self, path):
        if not SideBarSelection().isNone(path):
            try:
                os.remove(path)
            except:
                try:
                    if not os.access(path, os.W_OK):
                        import stat

                        os.chmod(path, stat.S_IWUSR)
                    os.remove(path)
                except:
                    # raise error in case we were unable to delete.
                    if os.path.exists(path):
                        print("Unable to remove file:\n" + path)
                        os.remove(path)
        else:
            print("path is none")
            print(path)

    def remove_safe_dir(self, path):
        if not SideBarSelection().isNone(path):
            try:
                shutil.rmtree(path)
            except:
                try:
                    if not os.access(path, os.W_OK):
                        import stat

                        os.chmod(path, stat.S_IWUSR)
                    shutil.rmtree(path)
                except:
                    # raise error in case we were unable to delete.
                    if os.path.exists(path):
                        print("Unable to remove folder:\n" + path)
                        shutil.rmtree(path)

    def is_enabled(self, paths=[]):
        return (
            CACHED_SELECTION(paths).len() > 0
            and CACHED_SELECTION(paths).hasProjectDirectories() is False
        )


class SideBarRevealCommand(sublime_plugin.WindowCommand):
    def run(self, paths=[]):
        if len(paths) > 1:
            paths = SideBarSelection(paths).getSelectedDirectoriesOrDirnames()
        else:
            paths = SideBarSelection(paths).getSelectedItems()
        for item in paths:
            item.reveal()

    def is_enabled(self, paths=[]):
        return CACHED_SELECTION(paths).len() > 0


class SideBarProjectItemRemoveFolderCommand(sublime_plugin.WindowCommand):
    def run(self, paths=[]):
        Window().run_command("remove_folder", {"dirs": paths})

    def is_visible(self, paths=[]):
        selection = CACHED_SELECTION(paths)
        project = SideBarProject()
        return project.hasDirectories() and all(
            [
                item.path() in project.getDirectories() or not item.exists()
                for item in selection.getSelectedItems()
            ]
        )


class SideBarOpenInNewWindowCommand(sublime_plugin.WindowCommand):
    def run(self, paths=[]):
        import subprocess

        items = []

        executable_path = sublime.executable_path()

        if sublime.platform() == "osx":
            app_path = executable_path[: executable_path.rfind(".app/") + 5]
            executable_path = app_path + "Contents/SharedSupport/bin/subl"

        items.append(executable_path)
        items.append("-n")

        for item in SideBarSelection(paths).getSelectedItems():
            items.append(item.forCwdSystemPath())
            items.append(item.path())
        subprocess.Popen(items, cwd=items[2])


class SideBarOpenWithFinderCommand(sublime_plugin.WindowCommand):
    def run(self, paths=[]):
        import subprocess

        for item in SideBarSelection(paths).getSelectedDirectoriesOrDirnames():
            subprocess.Popen(["open", item.name()], cwd=item.dirname())

    def is_visible(self, paths=[]):
        return sublime.platform() == "osx"


class SideBarStatusBarFileSize(sublime_plugin.EventListener):
    def on_activated(self, v):
        if v.file_name():
            try:
                self.show(v, hurry_size(os.path.getsize(v.file_name())))
            except:
                pass

    def on_post_save(self, v):
        if v.file_name():
            try:
                self.show(v, hurry_size(os.path.getsize(v.file_name())))
            except:
                pass


class SideBarSaveAsAdminCommand(sublime_plugin.WindowCommand):
    def run(self):
        import tempfile

        view = sublime.active_window().active_view()
        path = os.path.dirname(__file__) + "/"
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(bytes(view.substr(sublime.Region(0, view.size())), "UTF-8"))
            cli(
                [
                    escapeCMDWindows(path + "bin/elevate.exe"),
                    escapeCMDWindows(path + "bin/elevate.bat"),
                    escapeCMDWindows(f.name),
                    escapeCMDWindows(view.file_name()),
                ]
            )
            f.close()
        view.set_scratch(True)
        view.run_command("revert")
        view.set_scratch(False)

    def is_visible(self):
        return platform.system() == "Windows" or os.name == "nt"


class DefaultDirectory:
    pass


DefaultDirectory = DefaultDirectory()
DefaultDirectory.path = False


class SideBarDefaultNewFolder(sublime_plugin.EventListener):
    def on_new(self, view):
        path = None
        if not DefaultDirectory.path:
            paths = SideBarProject().getDirectories()
            if paths:
                path = paths[0]
        else:
            path = DefaultDirectory.path

        if path:
            view.settings().set("default_dir", path)

    def on_activated(self, view):
        if view and view.file_name():
            path = SideBarItem(view.file_name(), False).dirname()
            if path:
                DefaultDirectory.path = path


class zzzzzSideBarCommand(sublime_plugin.WindowCommand):
    def run(self, paths=[]):
        pass

    def is_visible(self, paths=[]):  # <- WORKS AS AN ONPOPUPSHOWN
        Cache.cached = False
        return False


class SideBarDonateCommand(sublime_plugin.WindowCommand):
    def run(self, paths=[]):
        import webbrowser

        webbrowser.open(
            "https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=DD4SL2AHYJGBW",
        )


class zzzzzcacheSideBarCommand(sublime_plugin.EventListener):
    def on_activated(self, view):
        if view and view.file_name():
            Cache.cached = SideBarSelection([view.file_name()])
