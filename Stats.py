# This code sends basic, anonymous statistics.  We use this to understand the popularity
# of different operating systems, builds of Sublime, Package Control plugin popularity,
# and programming language popularity.  We use these statistics to target and prioritize
# various features.  If you would like to opt out of these statistics, create a file in
# your home directory called `.SideBarEnhancements.optout`.  You can do this by running
# the following command:   touch ~/.SideBarEnhancements.optout


import json
import os
import sublime
import sublime_plugin
import sys
import time
import threading
import uuid
import platform
import re
import hashlib


try:
    from urllib.request import urlopen
except ImportError:
    from urllib2 import urlopen

class SideBarEnhancementsStats(sublime_plugin.EventListener, threading.Thread):
    def __init__(self):
        super(AdamTestPlugin, self).__init__()

        self.activity = False
        self.py_activity = False
        self.num_mins = 0
        self.num_activity_mins = 0
        self.num_py_activity_mins = 0
        self.should_stop = False
        self.state_lock = threading.Lock()

        if not os.path.isfile(os.path.join(os.path.expanduser('~'), '.SideBarEnhancements.optout')):
            sublime.set_timeout(self.start, 0)

    def every_minute(self):
        self.state_lock.acquire()
        try:
            self.num_mins += 1
            if self.activity:
                self.num_activity_mins += 1
            if self.py_activity:
                self.num_py_activity_mins += 1
            self.activity = self.py_activity = False
        finally:
            self.state_lock.release()

    def every_hour(self):
        address = []
        if uuid.getnode() and uuid.getnode() & 0x010000000000 == 0:
            address = [hashlib.sha1(bytes(hex(uuid.getnode())[2:].lower(), "utf-8")).hexdigest().lower()]

        active_editor_file_ext = None
        if sublime.active_window() and sublime.active_window().active_view():
            file_name = sublime.active_window().active_view().file_name()
            if file_name:
                active_editor_file_ext = os.path.splitext(file_name)[1] or None
        if active_editor_file_ext:
            active_editor_file_ext = active_editor_file_ext[1:].lower() or None
        if not active_editor_file_ext in "go,js,cpp,java,py,php,m,h,scala,c,cs,pl,rb,sh,html,less,css,md,asp,aspx,cfm,yaws,swf,htm,xhtml,jsp,jspx,do,action,php4,php3,xml,svg,coffee,_coffee,rhtml,jsx".split(","):
            active_editor_file_ext = None

        self.state_lock.acquire()
        data = None
        try:
            data = {
                "protocolVersion": 0,
                "addresses": address,
                "os": platform.system(),
                "osVersion": platform.release(),
                "editor": "sublime",
                "editorVersion": sublime.version(),
                "editorUUID": address[0] if len(address) > 0 else None,
                "activeNonBundledPackageNames": sorted(sublime.load_settings('Package Control.sublime-settings').get('installed_packages'), key=lambda s: s.lower()),
                "name": "SideBarEnhancements",
                "activeEditorFileExtension": active_editor_file_ext,
                "numMinutes": self.num_mins,
                "numMinutesCoding": self.num_activity_mins,
                "numMinutesCodingPython": self.num_py_activity_mins
            }
        finally:
            self.state_lock.release()

        # if sending fails (e.g. no internet connection), accumulate to send in a future "hour"
        # note, technically speaking it's cleaner to keep the lock while we call _send(), but we don't want
        #   a long HTTP request to block on_modified or on_selection_modified.
        if data and self._send(data):
            self.state_lock.acquire()
            try:
                self.num_mins = self.num_activity_mins = self.num_py_activity_mins = 0
            finally:
                self.state_lock.release()

    def on_modified(self, view):
        self.on_selection_modified(view)

    def on_selection_modified(self, view):
        self.state_lock.acquire()
        try:
            self.activity = True
            if (view.file_name() or "").endswith(".py") or 'Python' in view.settings().get('syntax'):
                self.py_activity = True
        finally:
            self.state_lock.release()

    def plugin_unloaded(self):
        self.state_lock.acquire()
        try:
            self.should_stop = True
        finally:
            self.state_lock.release()

        self.every_hour()

    def run(self):
        # Implements run from threading.Thread.
        min_counter = 0
        while True:
            time.sleep(60)
            self.state_lock.acquire()
            try:
                if self.should_stop:
                    return
            finally:
                self.state_lock.release()
            self.every_minute()

            min_counter += 1
            if min_counter == 60:
                min_counter = 0
                self.every_hour()

    def _send(self, data):
        json_body = json.dumps(data)
        if sys.version_info[0] >= 3:
            json_body = bytes(json_body, "utf-8")
        try:
            # strictly speaking we should use url-encoding, or set the content encoding header, but for
            #   simplicity (e.g. python 2 & 3 compatibility), not doing either.
            urlopen('http://52.52.168.91/status', json_body)
            return True
        except:
            return False