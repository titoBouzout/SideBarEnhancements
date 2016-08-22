# coding=utf8
import sublime, sublime_plugin

import os, shutil
import threading, time
import re

from .edit.Edit import Edit as Edit
from .hurry.filesize import size as hurry_size

try:
	from urllib import unquote as urlunquote
except ImportError:
	from urllib.parse import unquote as urlunquote

from .SideBarAPI import SideBarItem, SideBarSelection, SideBarProject

global Pref, s, Cache
Pref = {}
s = {}
Cache = {}

def CACHED_SELECTION(paths = []):
	if Cache.cached:
		return Cache.cached
	else:
		return SideBarSelection(paths)

def escapeCMDWindows(string):
	return string.replace('^', '^^')

class Pref():
	def load(self):
		pass

def plugin_loaded():
	global Pref, s
	s = sublime.load_settings('Side Bar.sublime-settings')
	Pref = Pref()
	Pref.load()
	s.clear_on_change('reload')
	s.add_on_change('reload', lambda:Pref.load())

def Window():
	return sublime.active_window()

def expandVars(path):
	for k, v in list(os.environ.items()):
		path = path.replace('%'+k+'%', v).replace('%'+k.lower()+'%', v)
	return path

def window_set_status(key, name =''):
	for window in sublime.windows():
		for view in window.views():
			view.set_status('SideBar-'+key, name)

class Object():
	pass

class Cache():
	pass
Cache = Cache()
Cache.cached = False

class OpenWithListener(sublime_plugin.EventListener):
	def on_load_async(self, view):
		if view and view.file_name() and not view.settings().get('open_with_edit'):
			item = SideBarItem(os.path.join(sublime.packages_path(), 'User', 'SideBarEnhancements', 'Open With', 'Side Bar.sublime-menu'), False)
			if item.exists():
				settings = sublime.decode_value(item.contentUTF8())
				selection = SideBarSelection([view.file_name()])
				for item in settings[0]['children']:
					try:
						if item['open_automatically'] and selection.hasFilesWithExtension(item['args']['extensions']):
							SideBarFilesOpenWithCommand(sublime_plugin.WindowCommand).run([view.file_name()], item['args']['application'], item['args']['extensions'])
							view.window().run_command('close')
							break
					except:
						pass

class aaaaaSideBarCommand(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		pass

	def is_visible(self, paths = []): # <- WORKS AS AN ONPOPUPSHOWING
		Cache.cached = SideBarSelection(paths)
		return False

class SideBarNewFileCommand(sublime_plugin.WindowCommand):
	def run(self, paths = [], name = ""):
		import functools
		Window().run_command('hide_panel');
		Window().show_input_panel("File Name:", name, functools.partial(self.on_done, paths, False), None, None)

	def on_done(self, paths, relative_to_project, name):
		if relative_to_project or s.get('new_files_relative_to_project_root', False):
			paths = SideBarProject().getDirectories()
			if paths:
				paths = [SideBarItem(paths[0], False)]
			if not paths:
				paths = SideBarSelection(paths).getSelectedDirectoriesOrDirnames()
		else:
			paths = SideBarSelection(paths).getSelectedDirectoriesOrDirnames()
		if not paths:
			paths = SideBarProject().getDirectories()
			if paths:
				paths = [SideBarItem(paths[0], False)]
		if not paths:
			sublime.active_window().new_file()
		else:
			for item in paths:
				item = SideBarItem(item.join(name), False)
				if item.exists():
					sublime.error_message("Unable to create file, file or folder exists.")
					self.run(paths, name)
					return
				else:
					try:
						item.create()
						item.edit()
					except:
						sublime.error_message("Unable to create file:\n\n"+item.path())
						self.run(paths, name)
						return
			SideBarProject().refresh();

class SideBarNewFile2Command(sublime_plugin.WindowCommand):
	def run(self, paths = [], name = ""):
		import functools
		Window().run_command('hide_panel');
		Window().show_input_panel("File Name:", name, functools.partial(SideBarNewFileCommand(sublime_plugin.WindowCommand).on_done, paths, True), None, None)

class SideBarNewDirectory2Command(sublime_plugin.WindowCommand):
	def run(self, paths = [], name = ""):
		import functools
		Window().run_command('hide_panel');
		Window().show_input_panel("Folder Name:", name, functools.partial(SideBarNewDirectoryCommand(sublime_plugin.WindowCommand).on_done, paths, True), None, None)

class SideBarNewDirectoryCommand(sublime_plugin.WindowCommand):
	def run(self, paths = [], name = ""):
		import functools
		Window().run_command('hide_panel');
		Window().show_input_panel("Folder Name:", name, functools.partial(self.on_done, paths, False), None, None)

	def on_done(self, paths, relative_to_project, name):
		if relative_to_project or s.get('new_folders_relative_to_project_root', False):
			paths = SideBarProject().getDirectories()
			if paths:
				paths = [SideBarItem(paths[0], True)]
			if not paths:
				paths = SideBarSelection(paths).getSelectedDirectoriesOrDirnames()
		else:
			paths = SideBarSelection(paths).getSelectedDirectoriesOrDirnames()

		for item in paths:
			item = SideBarItem(item.join(name), True)
			if item.exists():
				sublime.error_message("Unable to create folder, folder or file exists.")
				self.run(paths, name)
				return
			else:
				item.create()
				if not item.exists():
					sublime.error_message("Unable to create folder:\n\n"+item.path())
					self.run(paths, name)
					return
		SideBarProject().refresh();

	def is_enabled(self, paths = []):
		return CACHED_SELECTION(paths).len() > 0

class SideBarEditCommand(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		for item in SideBarSelection(paths).getSelectedFiles():
			item.edit()

	def is_enabled(self, paths = []):
		return CACHED_SELECTION(paths).hasFiles()

	def is_visible(self, paths =[]):
		return not s.get('disabled_menuitem_edit', False)

class SideBarEditToRightCommand(sublime_plugin.WindowCommand):
	def run(self, paths = []):

		window = Window()
		window.run_command('set_layout', {"cols": [0.0, 0.5, 1.0], "rows": [0.0, 1.0], "cells": [[0, 0, 1, 1], [1, 0, 2, 1]]})
		window.focus_group(1)
		for item in SideBarSelection(paths).getSelectedFiles():
			view = item.edit()
			window.set_view_index(view, 1, 0)

	def is_enabled(self, paths = []):
		return CACHED_SELECTION(paths).hasFiles()

	def is_visible(self, paths =[]):
		return not s.get('disabled_menuitem_edit', False) and not s.get('disabled_menuitem_edit_to_right', False)

class SideBarOpenCommand(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		for item in SideBarSelection(paths).getSelectedItems():
			item.open(s.get('use_powershell', True))

	def is_enabled(self, paths = []):
		return CACHED_SELECTION(paths).len() > 0

	def is_visible(self, paths =[]):
		return not s.get('disabled_menuitem_open_run', False)

class SideBarFilesOpenWithEditApplicationsCommand(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		platform = '';
		if sublime.platform() == 'osx':
			platform = 'OSX'
		elif sublime.platform() == 'windows':
			platform = 'Windows'
		else:
			platform = 'Linux'

		item = SideBarItem(os.path.join(sublime.packages_path(), 'User', 'SideBarEnhancements', 'Open With', 'Side Bar.sublime-menu'), False)
		if not item.exists() and False:
			item = SideBarItem(os.path.join(sublime.packages_path(), 'User', 'SideBarEnhancements', 'Open With', 'Side Bar ('+platform+').sublime-menu'), False)

		if not item.exists():
			item.create()
			item.write("""[
	{"id": "side-bar-files-open-with",
		"children":
		[

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
								},
				"open_automatically" : false // will close the view/tab and launch the application
			},

			//separator
			{"caption":"-"},

			//application 2
			{
				"caption": "SeaMonkey",
				"id": "side-bar-files-open-with-seamonkey",

				"command": "side_bar_files_open_with",
				"args": {
									"paths": [],
									"application": "C:\\\\Archivos de programa\\\\SeaMonkey\\\\seamonkey.exe", // WINNT
									"extensions":"", //open all even folders
									"args":[]
								},
				"open_automatically" : false // will close the view/tab and launch the application
			},
			//application n
			{
				"caption": "Chrome",
				"id": "side-bar-files-open-with-chrome",

				"command": "side_bar_files_open_with",
				"args": {
									"paths": [],
									"application": "C:\\\\Documents and Settings\\\\tito\\\\local\\\\Datos de programa\\\\Google\\\\Chrome\\\\Application\\\\chrome.exe",
									"extensions":".*", //any file with extension
									"args":[]
						},
				"open_automatically" : false // will close the view/tab and launch the application
			},

			{"caption":"-"}
		]
	}
]""");
		item.edit()

	def is_enabled(self, paths = []):
		return True

class SideBarFilesOpenWithCommand(sublime_plugin.WindowCommand):
	def run(self, paths = [], application = "", extensions = ""):
		self.run(self, paths = [], application = "", extensions = "", args=[])
	def run(self, paths = [], application = "", extensions = "", args=[]):
		application_dir, application_name = os.path.split(application)

		if extensions == '*':
			extensions = '.*'
		if extensions == '':
			items = SideBarSelection(paths).getSelectedItems()
		else:
			items = SideBarSelection(paths).getSelectedFilesWithExtension(extensions)
		import subprocess
		try:
			for item in items:
				if sublime.platform() == 'osx':
					subprocess.Popen(['open', '-a', application] + args + [item.name()], cwd=item.dirname())
				elif sublime.platform() == 'windows':
					subprocess.Popen([application_name] + args + [escapeCMDWindows(item.path())], cwd=expandVars(application_dir), shell=True)
				else:
					subprocess.Popen([application_name] + args + [escapeCMDWindows(item.name())], cwd=item.dirname())
		except:
			sublime.error_message('Unable to "Open With..", probably incorrect path to application.')

	def is_enabled(self, paths = [], application = "", extensions = ""):
		self.is_enabled(self, paths = [], application = "", extensions = "", args=[])
	def is_enabled(self, paths = [], application = "", extensions = "", args=[]):
		if extensions == '*':
			extensions = '.*'
		if extensions == '':
			return CACHED_SELECTION(paths).len() > 0
		else:
			return CACHED_SELECTION(paths).hasFilesWithExtension(extensions)

	def is_visible(self, paths = [], application = "", extensions = ""):
		self.is_visible(self, paths = [], application = "", extensions = "", args=[])
	def is_visible(self, paths = [], application = "", extensions = "", args=[]):
		if extensions == '*':
			extensions = '.*'
		if extensions == '':
			return CACHED_SELECTION(paths).len() > 0
		else:
			has = CACHED_SELECTION(paths).hasFilesWithExtension(extensions)
			return has or (not has and not s.get("hide_open_with_entries_when_there_are_no_applicable", False))

class SideBarFindInSelectedCommand(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		window = sublime.active_window()
		views = []
		for view in window.views():
			if view.name() == 'Find Results':
				views.append(view);
		for view in views:
			view.close();
		items = []
		for item in SideBarSelection(paths).getSelectedItemsWithoutChildItems():
			items.append(item.path())
		Window().run_command('hide_panel');
		Window().run_command("show_panel", {"panel": "find_in_files", "where":",".join(items) })

	def is_enabled(self, paths = []):
		return CACHED_SELECTION(paths).len() > 0

class SideBarFindInParentCommand(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		items = []
		for item in SideBarSelection(paths).getSelectedItems():
			items.append(item.dirname())
		items = list(set(items))
		Window().run_command('hide_panel');
		Window().run_command("show_panel", {"panel": "find_in_files", "where":",".join(items) })

	def is_enabled(self, paths = []):
		return CACHED_SELECTION(paths).len() > 0

class SideBarFindInProjectFoldersCommand(sublime_plugin.WindowCommand):
	def run(self):
		Window().run_command('hide_panel');
		Window().run_command("show_panel", {"panel": "find_in_files", "where":"<project>"})

class SideBarFindInProjectCommand(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		Window().run_command('hide_panel');
		Window().run_command("show_panel", {"panel": "find_in_files", "where":"<project>"})

	def is_visible(self, paths = []):
		return not s.get('disabled_menuitem_find_in_project', False)

class SideBarFindInProjectFolderCommand(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		items = []
		for item in SideBarSelection(paths).getSelectedItemsWithoutChildItems():
			items.append(SideBarProject().getDirectoryFromPath(item.path()))
		items = list(set(items))
		if items:
			Window().run_command('hide_panel');
			Window().run_command("show_panel", {"panel": "find_in_files", "where":",".join(items)})

class SideBarFindInFilesWithExtensionCommand(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		items = []
		for item in SideBarSelection(paths).getSelectedItems():
			items.append('*'+item.extension())
		items = list(set(items))
		Window().run_command('hide_panel');
		Window().run_command("show_panel", {"panel": "find_in_files", "where":",".join(items) })

	def is_enabled(self, paths = []):
		return CACHED_SELECTION(paths).hasFiles()

	def description(self, paths = []):
		items = []
		for item in CACHED_SELECTION(paths).getSelectedFiles():
			items.append('*'+item.extension())
		items = list(set(items))
		if len(items) > 1:
			return 'In Files With Extensions '+(",".join(items))+'…'
		elif len(items) > 0:
			return 'In Files With Extension '+(",".join(items))+'…'
		else:
			return 'In Files With Extension…'

Object.sidebar_instant_search_id = 0
class SideBarFindFilesPathContainingCommand(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		if paths == [] and SideBarProject().getDirectories():
			paths = SideBarProject().getDirectories()
		else:
			paths = [item.path() for item in SideBarSelection(paths).getSelectedDirectoriesOrDirnames()]
		if paths == []:
			return
		view = Window().new_file()
		view.settings().set('word_wrap', False)
		view.set_name('Instant File Search')
		view.set_syntax_file('Packages/SideBarEnhancements/SideBar Results.hidden-tmLanguage')
		view.set_scratch(True)
		view.run_command('insert', {"characters": "Type to search: "})
		view.sel().clear()
		view.sel().add(sublime.Region(16,16))
		view.settings().set('sidebar_instant_search_paths', paths)
	def is_enabled(self, paths=[]):
		return True

class SideBarFindFilesPathContainingViewListener(sublime_plugin.EventListener):
	def on_modified(self, view):
		view.settings().has('sidebar_instant_search_paths') # for some reason the first call in some conditions returns true, but not the next one WTH
		if view.settings().has('sidebar_instant_search_paths'):
			searchTerm = view.substr(view.line(0)).replace("Type to search:", "").strip()
			if searchTerm and Object.sidebar_instant_search_id != searchTerm:
				SideBarFindFilesPathContainingSearchThread(view, searchTerm).start()
			elif not searchTerm:
				view.set_name('Instant File Search')

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

		paths = view.settings().get('sidebar_instant_search_paths')
		self.ignore_paths = view.settings().get('file_exclude_patterns', [])
		try:
			self.searchTermRegExp = re.compile(searchTerm, re.I | re.U)
			self.match_function = self.match_regexp
			search_type = 'REGEXP'
		except:
			self.match_function = self.match_string
			search_type = 'LITERAL'

		if Object.sidebar_instant_search_id == searchTerm:
			total = 0
			highlight_from = 0
			match_result = ''
			match_result += 'Type to search: '+searchTerm+'\n'
			find = self.find
			for item in SideBarSelection(paths).getSelectedDirectoriesOrDirnames():
				self.files = []
				self.num_files = 0
				find(item.path())
				match_result += '\n'
				length = len(self.files)
				if length > 1:
					match_result += str(length)+' matches'
				elif length > 0:
					match_result += '1 match'
				else:
					match_result += 'No match'
				match_result += ' in '+str(self.num_files)+' files for term "'+searchTerm+'" using '+search_type+' under \n"'+item.path()+'"\n\n'
				if highlight_from == 0:
					highlight_from = len(match_result)
				match_result += ('\n'.join(self.files))
				total += length
			match_result += '\n'

			if Object.sidebar_instant_search_id == searchTerm:
				sel = view.sel()
				position = sel[0].begin()
				if position > 16+len(searchTerm):
					position = 16+len(searchTerm)
				if sublime.platform() == 'osx':
					view.run_command('side_bar_enhancements_write_to_view', {'content' :match_result, 'position': position, 'searchTerm': searchTerm})
				else:
					with Edit(view) as edit:
						edit.replace(sublime.Region(0, view.size()), match_result);
					sel.clear()
					sel.add(sublime.Region(position, position))
				view.set_name(searchTerm+' - IFS')
				if Object.sidebar_instant_search_id == searchTerm:
					view.erase_regions("sidebar_search_instant_highlight")
					if total < 5000 and len(searchTerm) > 1:
						if search_type == 'REGEXP':
							regions = [item for item in view.find_all(searchTerm, sublime.IGNORECASE) if item.begin() >= highlight_from]
						else:
							regions = [item for item in view.find_all(searchTerm, sublime.LITERAL|sublime.IGNORECASE) if item.begin() >= highlight_from]
						if Object.sidebar_instant_search_id == searchTerm:
							view.add_regions("sidebar_search_instant_highlight", regions, 'entity.name.function', '', sublime.PERSISTENT | sublime.DRAW_SQUIGGLY_UNDERLINE | sublime.DRAW_NO_FILL | sublime.DRAW_NO_OUTLINE | sublime.DRAW_EMPTY_AS_OVERWRITE)

	def find(self, path):
		if os.path.isfile(path) or os.path.islink(path):
			self.num_files = self.num_files+1
			if self.match_function(path):
				self.files.append(path)
		elif os.path.isdir(path):
			for content in os.listdir(path):
				file = os.path.join(path, content)
				if os.path.isfile(file) or os.path.islink(file):
					self.num_files = self.num_files+1
					if self.match_function(file):
						self.files.append(file)
				else:
					self.find(file)

	def match_regexp(self, path):
		return self.searchTermRegExp.search(path) and not [1 for s in self.ignore_paths if s in path]

	def match_string(self, path):
		return self.searchTerm in path and not [1 for s in self.ignore_paths if s in path]

class SideBarEnhancementsWriteToViewCommand(sublime_plugin.TextCommand):
	def run(self, edit, content, position, searchTerm):
		if Object.sidebar_instant_search_id == searchTerm:
			view = self.view
			view.replace(edit, sublime.Region(0, view.size()), content);
			view.sel().clear()
			view.sel().add(sublime.Region(position,position))
			view.end_edit(edit)

class SideBarCutCommand(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		s = sublime.load_settings("SideBarEnhancements/Clipboard.sublime-settings")
		items = []
		for item in SideBarSelection(paths).getSelectedItemsWithoutChildItems():
			items.append(item.path())

		if len(items) > 0:
			s.set('cut', "\n".join(items))
			s.set('copy', '')
			if len(items) > 1 :
				sublime.status_message("Items cut")
			else :
				sublime.status_message("Item cut")

	def is_enabled(self, paths = []):
		return CACHED_SELECTION(paths).len() > 0 and CACHED_SELECTION(paths).hasProjectDirectories() == False

class SideBarCopyCommand(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		s = sublime.load_settings("SideBarEnhancements/Clipboard.sublime-settings")
		items = []
		for item in SideBarSelection(paths).getSelectedItemsWithoutChildItems():
			items.append(item.path())

		if len(items) > 0:
			s.set('cut', '')
			s.set('copy', "\n".join(items))
			if len(items) > 1 :
				sublime.status_message("Items copied")
			else :
				sublime.status_message("Item copied")

	def is_enabled(self, paths = []):
		return CACHED_SELECTION(paths).len() > 0

class SideBarPasteCommand(sublime_plugin.WindowCommand):
	def run(self, paths = [], in_parent = 'False', test = 'True', replace = 'False'):
		key = 'paste-'+str(time.time())
		SideBarPasteThread(paths, in_parent, test, replace, key).start()

	def is_enabled(self, paths = [], in_parent = False):
		s = sublime.load_settings("SideBarEnhancements/Clipboard.sublime-settings")
		return (s.get('cut', '') + s.get('copy', '')) != '' and len(CACHED_SELECTION(paths).getSelectedDirectoriesOrDirnames()) == 1

	def is_visible(self, paths = [], in_parent = False):
		if in_parent == 'True':
			return not s.get('disabled_menuitem_paste_in_parent', False)
		else:
			return True

class SideBarPasteThread(threading.Thread):
	def __init__(self, paths = [], in_parent = 'False', test = 'True', replace = 'False', key = ''):
		self.paths = paths
		self.in_parent = in_parent
		self.test = test
		self.replace = replace
		self.key = key
		threading.Thread.__init__(self)

	def run(self):
		SideBarPasteCommand2(sublime_plugin.WindowCommand).run(self.paths, self.in_parent, self.test, self.replace, self.key)

class SideBarPasteCommand2(sublime_plugin.WindowCommand):
	def run(self, paths = [], in_parent = 'False', test = 'True', replace = 'False', key = ''):
		window_set_status(key, 'Pasting…')

		s = sublime.load_settings("SideBarEnhancements/Clipboard.sublime-settings")

		cut = s.get('cut', '')
		copy = s.get('copy', '')

		already_exists_paths = []

		if SideBarSelection(paths).len() > 0:
			if in_parent == 'False':
				location = SideBarSelection(paths).getSelectedItems()[0].path()
			else:
				location = SideBarSelection(paths).getSelectedDirectoriesOrDirnames()[0].dirname()

			if os.path.isdir(location) == False:
				location = SideBarItem(os.path.dirname(location), True)
			else:
				location = SideBarItem(location, True)

			if cut != '':
				cut = cut.split("\n")
				for path in cut:
					path = SideBarItem(path, os.path.isdir(path))
					new  = os.path.join(location.path(), path.name())
					if test == 'True' and os.path.exists(new):
						already_exists_paths.append(new)
					elif test == 'False':
						if os.path.exists(new) and replace == 'False':
							pass
						else:
							try:
								if not path.move(new, replace == 'True'):
									window_set_status(key, '')
									sublime.error_message("Unable to cut and paste, destination exists.")
									return
							except:
								window_set_status(key, '')
								sublime.error_message("Unable to move:\n\n"+path.path()+"\n\nto\n\n"+new)
								return

			if copy != '':
				copy = copy.split("\n")
				for path in copy:
					path = SideBarItem(path, os.path.isdir(path))
					new  = os.path.join(location.path(), path.name())
					if test == 'True' and os.path.exists(new):
						already_exists_paths.append(new)
					elif test == 'False':
						if os.path.exists(new) and replace == 'False':
							pass
						else:
							try:
								if not path.copy(new, replace == 'True'):
									window_set_status(key, '')
									sublime.error_message("Unable to copy and paste, destination exists.")
									return
							except:
								window_set_status(key, '')
								sublime.error_message("Unable to copy:\n\n"+path.path()+"\n\nto\n\n"+new)
								return

			if test == 'True' and len(already_exists_paths):
				self.confirm(paths, in_parent, already_exists_paths, key)
			elif test == 'True' and not len(already_exists_paths):
				SideBarPasteThread(paths, in_parent, 'False', 'False', key).start();
			elif test == 'False':
				cut = s.set('cut', '')
				SideBarProject().refresh();
				window_set_status(key, '')
		else:
			window_set_status(key, '')

	def confirm(self, paths, in_parent, data, key):
		import functools
		window = sublime.active_window()
		window.show_input_panel("BUG!", '', '', None, None)
		window.run_command('hide_panel');

		yes = []
		yes.append('Yes, Replace the following items:');
		for item in data:
			yes.append(SideBarItem(item, os.path.isdir(item)).pathWithoutProject())

		no = []
		no.append('No');
		no.append('Continue without replacing');

		while len(no) != len(yes):
			no.append('ST3 BUG');

		window.show_quick_panel([yes, no], functools.partial(self.on_done, paths, in_parent, key))

	def on_done(self, paths, in_parent, key, result):
		window_set_status(key, '')
		if result != -1:
			if result == 0:
				SideBarPasteThread(paths, in_parent, 'False', 'True', key).start()
			else:
				SideBarPasteThread(paths, in_parent, 'False', 'False', key).start()

class SideBarCopyNameCommand(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		items = []
		for item in SideBarSelection(paths).getSelectedItems():
			items.append(item.name())

		if len(items) > 0:
			sublime.set_clipboard("\n".join(items));
			if len(items) > 1 :
				sublime.status_message("Items copied")
			else :
				sublime.status_message("Item copied")

	def is_enabled(self, paths = []):
		return CACHED_SELECTION(paths).len() > 0

	def is_visible(self, paths =[]):
		return not s.get('disabled_menuitem_copy_name', False)

class SideBarCopyNameEncodedCommand(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		items = []
		for item in SideBarSelection(paths).getSelectedItems():
			items.append(item.nameEncoded())

		if len(items) > 0:
			sublime.set_clipboard("\n".join(items));
			if len(items) > 1 :
				sublime.status_message("Items copied")
			else :
				sublime.status_message("Item copied")

	def is_enabled(self, paths = []):
		return CACHED_SELECTION(paths).len() > 0

class SideBarCopyPathCommand(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		items = []
		for item in SideBarSelection(paths).getSelectedItems():
			items.append(item.path())

		if len(items) > 0:
			sublime.set_clipboard("\n".join(items));
			if len(items) > 1 :
				sublime.status_message("Items copied")
			else :
				sublime.status_message("Item copied")

	def is_enabled(self, paths = []):
		return CACHED_SELECTION(paths).len() > 0

class SideBarCopyDirPathCommand(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		items = []
		for item in SideBarSelection(paths).getSelectedDirectoriesOrDirnames():
			items.append(item.path())

		if len(items) > 0:
			sublime.set_clipboard("\n".join(items));
			if len(items) > 1 :
				sublime.status_message("Items copied")
			else :
				sublime.status_message("Item copied")

	def is_enabled(self, paths = []):
		return CACHED_SELECTION(paths).len() > 0

	def is_visible(self, paths =[]):
		return not s.get('disabled_menuitem_copy_dir_path', False)

class SideBarCopyPathEncodedCommand(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		items = []
		for item in SideBarSelection(paths).getSelectedItems():
			items.append(item.uri())

		if len(items) > 0:
			sublime.set_clipboard("\n".join(items));
			if len(items) > 1 :
				sublime.status_message("Items copied")
			else :
				sublime.status_message("Item copied")

	def is_enabled(self, paths = []):
		return CACHED_SELECTION(paths).len() > 0

class SideBarCopyPathRelativeFromProjectCommand(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		items = []
		for item in SideBarSelection(paths).getSelectedItems():
			items.append(item.pathRelativeFromProject())

		if len(items) > 0:
			sublime.set_clipboard("\n".join(items));
			if len(items) > 1 :
				sublime.status_message("Items copied")
			else :
				sublime.status_message("Item copied")

	def is_enabled(self, paths = []):
		return CACHED_SELECTION(paths).len() > 0 and CACHED_SELECTION(paths).hasItemsUnderProject()

class SideBarCopyPathRelativeFromProjectEncodedCommand(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		items = []
		for item in SideBarSelection(paths).getSelectedItems():
			items.append(item.pathRelativeFromProjectEncoded())

		if len(items) > 0:
			sublime.set_clipboard("\n".join(items));
			if len(items) > 1 :
				sublime.status_message("Items copied")
			else :
				sublime.status_message("Item copied")

	def is_enabled(self, paths = []):
		return CACHED_SELECTION(paths).len() > 0 and CACHED_SELECTION(paths).hasItemsUnderProject()

class SideBarCopyPathRelativeFromViewCommand(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		items = []
		for item in SideBarSelection(paths).getSelectedItems():
			items.append(item.pathRelativeFromView())

		if len(items) > 0:
			sublime.set_clipboard("\n".join(items));
			if len(items) > 1 :
				sublime.status_message("Items copied")
			else :
				sublime.status_message("Item copied")

	def is_enabled(self, paths = []):
		return CACHED_SELECTION(paths).len() > 0

class SideBarCopyPathRelativeFromViewEncodedCommand(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		items = []
		for item in SideBarSelection(paths).getSelectedItems():
			items.append(item.pathRelativeFromViewEncoded())

		if len(items) > 0:
			sublime.set_clipboard("\n".join(items));
			if len(items) > 1 :
				sublime.status_message("Items copied")
			else :
				sublime.status_message("Item copied")

	def is_enabled(self, paths = []):
		return CACHED_SELECTION(paths).len() > 0

class SideBarCopyPathAbsoluteFromProjectCommand(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		items = []
		for item in SideBarSelection(paths).getSelectedItems():
			items.append(item.pathAbsoluteFromProject())

		if len(items) > 0:
			sublime.set_clipboard("\n".join(items));
			if len(items) > 1 :
				sublime.status_message("Items copied")
			else :
				sublime.status_message("Item copied")

	def is_enabled(self, paths = []):
		return CACHED_SELECTION(paths).len() > 0 and CACHED_SELECTION(paths).hasItemsUnderProject()

class SideBarCopyPathAbsoluteFromProjectEncodedCommand(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		items = []
		for item in SideBarSelection(paths).getSelectedItems():
			items.append(item.pathAbsoluteFromProjectEncoded())

		if len(items) > 0:
			sublime.set_clipboard("\n".join(items));
			if len(items) > 1 :
				sublime.status_message("Items copied")
			else :
				sublime.status_message("Item copied")

	def is_enabled(self, paths = []):
		return CACHED_SELECTION(paths).len() > 0 and CACHED_SELECTION(paths).hasItemsUnderProject()

	def is_visible(self, paths =[]):
		return not s.get('disabled_menuitem_copy_path', False)

class SideBarCopyPathAbsoluteFromProjectEncodedWindowsCommand(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		items = []
		for item in SideBarSelection(paths).getSelectedItems():
			items.append(item.pathAbsoluteFromProjectEncoded())

		if len(items) > 0:
			sublime.set_clipboard(("\n".join(items)).replace('/', '\\'));
			if len(items) > 1 :
				sublime.status_message("Items copied")
			else :
				sublime.status_message("Item copied")

	def is_enabled(self, paths = []):
		return CACHED_SELECTION(paths).len() > 0 and CACHED_SELECTION(paths).hasItemsUnderProject()

	def is_visible(self, paths =[]):
		return not s.get('disabled_menuitem_copy_path_windows', True)

class SideBarCopyTagAhrefCommand(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		items = []
		for item in SideBarSelection(paths).getSelectedItems():
			items.append('<a href="'+item.pathAbsoluteFromProjectEncoded()+'">'+item.namePretty()+'</a>')

		if len(items) > 0:
			sublime.set_clipboard("\n".join(items));
			if len(items) > 1 :
				sublime.status_message("Items copied")
			else :
				sublime.status_message("Item copied")

	def is_enabled(self, paths = []):
		return CACHED_SELECTION(paths).len() > 0 and CACHED_SELECTION(paths).hasItemsUnderProject()

class SideBarCopyTagImgCommand(sublime_plugin.WindowCommand):

	def run(self, paths = []):
		items = []
		for item in SideBarSelection(paths).getSelectedImages():
			try:
				image_type, width, height = self.getImageInfo(item.path())
				items.append('<img src="'+item.pathAbsoluteFromProjectEncoded()+'" width="'+str(width)+'" height="'+str(height)+'">')
			except:
				items.append('<img src="'+item.pathAbsoluteFromProjectEncoded()+'">')
		if len(items) > 0:
			sublime.set_clipboard("\n".join(items));
			if len(items) > 1 :
				sublime.status_message("Items copied")
			else :
				sublime.status_message("Item copied")

	# http://stackoverflow.com/questions/8032642/how-to-obtain-image-size-using-standard-python-class-without-using-external-lib

	def getImageInfo(self, fname):
		import struct
		import imghdr

		'''Determine the image type of fhandle and return its size.
		from draco'''
		fhandle = open(fname, 'rb')
		head = fhandle.read(24)
		if len(head) != 24:
			return
		if imghdr.what(fname) == 'png':
			check = struct.unpack('>i', head[4:8])[0]
			if check != 0x0d0a1a0a:
				return
			width, height = struct.unpack('>ii', head[16:24])
		elif imghdr.what(fname) == 'gif':
			width, height = struct.unpack('<HH', head[6:10])
		elif imghdr.what(fname) == 'jpeg':
			try:
				fhandle.seek(0) # Read 0xff next
				size = 2
				ftype = 0
				while not 0xc0 <= ftype <= 0xcf:
					fhandle.seek(size, 1)
					byte = fhandle.read(1)
					while ord(byte) == 0xff:
						byte = fhandle.read(1)
					ftype = ord(byte)
					size = struct.unpack('>H', fhandle.read(2))[0] - 2
				# We are at a SOFn block
				fhandle.seek(1, 1)  # Skip `precision' byte.
				height, width = struct.unpack('>HH', fhandle.read(4))
			except Exception: #IGNORE:W0703
				return
		else:
			return
		return None, width, height

	def is_enabled(self, paths = []):
		return CACHED_SELECTION(paths).hasImages() and CACHED_SELECTION(paths).hasItemsUnderProject()

class SideBarCopyTagStyleCommand(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		items = []
		for item in SideBarSelection(paths).getSelectedFilesWithExtension('css'):
			items.append('<link rel="stylesheet" type="text/css" href="'+item.pathAbsoluteFromProjectEncoded()+'"/>')

		if len(items) > 0:
			sublime.set_clipboard("\n".join(items));
			if len(items) > 1 :
				sublime.status_message("Items copied")
			else :
				sublime.status_message("Item copied")

	def is_enabled(self, paths = []):
		return CACHED_SELECTION(paths).hasFilesWithExtension('css') and CACHED_SELECTION(paths).hasItemsUnderProject()

class SideBarCopyTagScriptCommand(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		items = []
		for item in SideBarSelection(paths).getSelectedFilesWithExtension('js'):
			items.append('<script type="text/javascript" src="'+item.pathAbsoluteFromProjectEncoded()+'"></script>')

		if len(items) > 0:
			sublime.set_clipboard("\n".join(items));
			if len(items) > 1 :
				sublime.status_message("Items copied")
			else :
				sublime.status_message("Item copied")

	def is_enabled(self, paths = []):
		return CACHED_SELECTION(paths).hasFilesWithExtension('js') and CACHED_SELECTION(paths).hasItemsUnderProject()

class SideBarCopyProjectDirectoriesCommand(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		items = []
		for directory in SideBarProject().getDirectories():
			items.append(directory)

		if len(items) > 0:
			sublime.set_clipboard("\n".join(items));
			if len(items) > 1 :
				sublime.status_message("Items copied")
			else :
				sublime.status_message("Item copied")

	def is_enabled(self, paths = []):
		return True

class SideBarCopyContentUtf8Command(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		items = []
		for item in SideBarSelection(paths).getSelectedFiles():
			items.append(item.contentUTF8())

		if len(items) > 0:
			sublime.set_clipboard("\n".join(items));
			if len(items) > 1 :
				sublime.status_message("Items content copied")
			else :
				sublime.status_message("Item content copied")

	def is_enabled(self, paths = []):
		return CACHED_SELECTION(paths).hasFiles()

class SideBarCopyContentBase64Command(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		items = []
		for item in SideBarSelection(paths).getSelectedFiles():
			items.append(item.contentBase64())

		if len(items) > 0:
			sublime.set_clipboard("\n".join(items));
			if len(items) > 1 :
				sublime.status_message("Items content copied")
			else :
				sublime.status_message("Item content copied")

	def is_enabled(self, paths = []):
		return CACHED_SELECTION(paths).hasFiles()

class SideBarCopyUrlCommand(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		items = []

		for item in SideBarSelection(paths).getSelectedItems():
			if item.isUnderCurrentProject():
				items.append(item.url('url_production'))

		if len(items) > 0:
			sublime.set_clipboard("\n".join(items));
			if len(items) > 1 :
				sublime.status_message("Items URL copied")
			else :
				sublime.status_message("Item URL copied")

	def is_enabled(self, paths = []):
		return CACHED_SELECTION(paths).hasItemsUnderProject()

class SideBarCopyUrlDecodedCommand(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		items = []

		for item in SideBarSelection(paths).getSelectedItems():
			if item.isUnderCurrentProject():
				txt = item.url('url_production')
				try:
					txt = urlunquote(txt.encode('utf8')).decode('utf8')
				except TypeError:
					txt = urlunquote(txt)
				items.append(txt)

		if len(items) > 0:
			sublime.set_clipboard("\n".join(items));
			if len(items) > 1 :
				sublime.status_message("Items URL copied")
			else :
				sublime.status_message("Item URL copied")

	def is_enabled(self, paths = []):
		return CACHED_SELECTION(paths).hasItemsUnderProject()

class SideBarDuplicateCommand(sublime_plugin.WindowCommand):
	def run(self, paths = [], new = False):
		import functools
		Window().run_command('hide_panel');
		view = Window().show_input_panel("Duplicate As:", new or SideBarSelection(paths).getSelectedItems()[0].path(), functools.partial(self.on_done, SideBarSelection(paths).getSelectedItems()[0].path()), None, None)
		view.sel().clear()
		view.sel().add(sublime.Region(view.size()-len(SideBarSelection(paths).getSelectedItems()[0].name()), view.size()-len(SideBarSelection(paths).getSelectedItems()[0].extension())))

	def on_done(self, old, new):
		key = 'duplicate-'+str(time.time())
		SideBarDuplicateThread(old, new, key).start()

	def is_enabled(self, paths = []):
		return CACHED_SELECTION(paths).len() == 1 and CACHED_SELECTION(paths).hasProjectDirectories() == False

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
		window_set_status(key, 'Duplicating…')

		item = SideBarItem(old, os.path.isdir(old))
		try:
			if not item.copy(new):
				window_set_status(key, '')
				if SideBarItem(new, os.path.isdir(new)).overwrite():
					self.run()
				else:
					SideBarDuplicateCommand(sublime_plugin.WindowCommand).run([old], new)
				return
		except:
			window_set_status(key, '')
			sublime.error_message("Unable to copy:\n\n"+old+"\n\nto\n\n"+new)
			SideBarDuplicateCommand(sublime_plugin.WindowCommand).run([old], new)
			return
		item = SideBarItem(new, os.path.isdir(new))
		if item.isFile():
			item.edit();
		SideBarProject().refresh();
		window_set_status(key, '')

class SideBarRenameCommand(sublime_plugin.WindowCommand):
	def run(self, paths = [], newLeaf = False):
		import functools
		branch, leaf = os.path.split(SideBarSelection(paths).getSelectedItems()[0].path())
		Window().run_command('hide_panel');
		view = Window().show_input_panel("New Name:", newLeaf or leaf, functools.partial(self.on_done, SideBarSelection(paths).getSelectedItems()[0].path(), branch), None, None)
		view.sel().clear()
		view.sel().add(sublime.Region(view.size()-len(SideBarSelection(paths).getSelectedItems()[0].name()), view.size()-len(SideBarSelection(paths).getSelectedItems()[0].extension())))

	def on_done(self, old, branch, leaf):
		key = 'rename-'+str(time.time())
		SideBarRenameThread(old, branch, leaf, key).start()

	def is_enabled(self, paths = []):
		return CACHED_SELECTION(paths).len() == 1 and CACHED_SELECTION(paths).hasProjectDirectories() == False

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
		window_set_status(key, 'Renaming…')

		Window().run_command('hide_panel');
		leaf = leaf.strip();
		new = os.path.join(branch, leaf)
		item = SideBarItem(old, os.path.isdir(old))
		try:
			if not item.move(new):
				if SideBarItem(new, os.path.isdir(new)).overwrite():
					self.run()
				else:
					window_set_status(key, '')
					SideBarRenameCommand(sublime_plugin.WindowCommand).run([old], leaf)
		except:
			window_set_status(key, '')
			sublime.error_message("Unable to rename:\n\n"+old+"\n\nto\n\n"+new)
			SideBarRenameCommand(sublime_plugin.WindowCommand).run([old], leaf)
			raise
			return
		SideBarProject().refresh();
		window_set_status(key, '')

class SideBarMassRenameCommand(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		import functools
		Window().run_command('hide_panel');
		Window().show_input_panel("Find:", '', functools.partial(self.on_find, paths), None, None)

	def on_find(self, paths, find):
		if not find:
			return
		import functools
		Window().run_command('hide_panel');
		Window().show_input_panel("Replace:", '', functools.partial(self.on_replace, paths, find), None, None)

	def on_replace(self, paths, find, replace):
		key = 'mass-renaming-'+str(time.time())
		SideBarMassRenameThread(paths, find, replace, key).start()

	def is_enabled(self, paths = []):
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

		if find == '':
			return None
		else:
			window_set_status(key, 'Mass renaming…')

			to_rename_or_move = []
			for item in SideBarSelection(paths).getSelectedItemsWithoutChildItems():
				self.recurse(item.path(), to_rename_or_move)
			to_rename_or_move.sort()
			to_rename_or_move.reverse()
			for item in to_rename_or_move:
				if find in item:
					origin = SideBarItem(item, os.path.isdir(item))
					destination = SideBarItem(origin.pathProject()+''+(origin.pathWithoutProject().replace(find, replace)), os.path.isdir(item))
					origin.move(destination.path());

			SideBarProject().refresh();
			window_set_status(key, '')

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
	def run(self, paths = [], new = False):
		import functools
		Window().run_command('hide_panel');
		view = Window().show_input_panel("New Location:", new or SideBarSelection(paths).getSelectedItems()[0].path(), functools.partial(self.on_done, SideBarSelection(paths).getSelectedItems()[0].path()), None, None)
		view.sel().clear()
		view.sel().add(sublime.Region(view.size()-len(SideBarSelection(paths).getSelectedItems()[0].name()), view.size()-len(SideBarSelection(paths).getSelectedItems()[0].extension())))

	def on_done(self, old, new):
		key = 'move-'+str(time.time())
		SideBarMoveThread(old, new, key).start()

	def is_enabled(self, paths = []):
		return CACHED_SELECTION(paths).len() == 1 and CACHED_SELECTION(paths).hasProjectDirectories() == False

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
		window_set_status(key, 'Moving…')

		item = SideBarItem(old, os.path.isdir(old))
		try:
			if not item.move(new):
				if SideBarItem(new, os.path.isdir(new)).overwrite():
					self.run()
				else:
					window_set_status(key, '')
					SideBarMoveCommand(sublime_plugin.WindowCommand).run([old], new)
				return
		except:
			window_set_status(key, '')
			sublime.error_message("Unable to move:\n\n"+old+"\n\nto\n\n"+new)
			SideBarMoveCommand(sublime_plugin.WindowCommand).run([old], new)
			raise
			return
		SideBarProject().refresh();
		window_set_status(key, '')

class SideBarDeleteThread(threading.Thread):
	def __init__(self, paths):
		self.paths = paths
		threading.Thread.__init__(self)

	def run(self):
		SideBarDeleteCommand(sublime_plugin.WindowCommand)._delete_threaded(self.paths)

class SideBarDeleteCommand(sublime_plugin.WindowCommand):
	def run(self, paths = [], confirmed = 'False'):

		if confirmed == 'False' and s.get('confirm_before_deleting', True):
			if sublime.platform() == 'osx':
				if sublime.ok_cancel_dialog('Delete the selected items?'):
					self.run(paths, 'True')
			else:
				self.confirm([item.path() for item in SideBarSelection(paths).getSelectedItems()], [item.pathWithoutProject() for item in SideBarSelection(paths).getSelectedItems()])
		else:
			SideBarDeleteThread(paths).start()

	def _delete_threaded(self, paths):
		key = 'delete-'+str(time.time())
		window_set_status(key, 'Deleting…')
		try:
			from .send2trash import send2trash
			for item in SideBarSelection(paths).getSelectedItemsWithoutChildItems():
				if s.get('close_affected_buffers_when_deleting_even_if_dirty', False):
					item.closeViews()
				if s.get('disable_send_to_trash', False):
					if sublime.platform() == 'windows':
						self.remove('\\\\?\\'+item.path());
					else:
						self.remove(item.path());
				else:
					send2trash(item.path())
			SideBarProject().refresh();
		except:
			should_confirm = s.get('confirm_before_permanently_deleting', True)
			if not should_confirm or sublime.ok_cancel_dialog('There is no trash bin, permanently delete?', 'Yes, Permanent Deletion'):
				for item in SideBarSelection(paths).getSelectedItemsWithoutChildItems():
					if s.get('close_affected_buffers_when_deleting_even_if_dirty', False):
						item.closeViews()
					if sublime.platform() == 'windows':
						self.remove('\\\\?\\'+item.path());
					else:
						self.remove(item.path());
				SideBarProject().refresh();
		window_set_status(key, '')

	def confirm(self, paths, display_paths):
		import functools
		window = sublime.active_window()
		window.show_input_panel("BUG!", '', '', None, None)
		window.run_command('hide_panel');

		yes = []
		yes.append('Yes, delete the selected items.');
		for item in display_paths:
			yes.append(item);

		no = []
		no.append('No');
		no.append('Cancel the operation.');

		while len(no) != len(yes):
			no.append('');

		if sublime.platform() == 'osx':
			sublime.set_timeout(lambda:window.show_quick_panel([yes, no], functools.partial(self.on_confirm, paths)), 200);
		else:
			window.show_quick_panel([yes, no], functools.partial(self.on_confirm, paths))

	def on_confirm(self, paths, result):
		if result != -1:
			if result == 0:
				self.run(paths, 'True')

	def on_done(self, old, new):
		if s.get('close_affected_buffers_when_deleting_even_if_dirty', False):
			item = SideBarItem(new, os.path.isdir(new))
			item.closeViews()
		if sublime.platform() == 'windows':
			self.remove('\\\\?\\'+new);
		else:
			self.remove(new)
		SideBarProject().refresh();

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
						print("Unable to remove file:\n"+path)
						os.remove(path)
		else:
			print('path is none')
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
						print("Unable to remove folder:\n"+path)
						shutil.rmtree(path)

	def is_enabled(self, paths = []):
		return CACHED_SELECTION(paths).len() > 0 and CACHED_SELECTION(paths).hasProjectDirectories() == False

class SideBarEmptyCommand(sublime_plugin.WindowCommand):
	def run(self, paths = [], confirmed = 'False'):

		if confirmed == 'False' and s.get('confirm_before_deleting', True):
			if sublime.platform() == 'osx':
				if sublime.ok_cancel_dialog('empty the content of the folder?'):
					self.run(paths, 'True')
			else:
				self.confirm([item.path() for item in SideBarSelection(paths).getSelectedDirectoriesOrDirnames()], [item.pathWithoutProject() for item in SideBarSelection(paths).getSelectedDirectoriesOrDirnames()])
		else:
			key = 'move-'+str(time.time())
			SideBarEmptyThread(paths, key).start()

	def confirm(self, paths, display_paths):
		import functools
		window = sublime.active_window()
		window.show_input_panel("BUG!", '', '', None, None)
		window.run_command('hide_panel');

		yes = []
		yes.append('Yes, empty the selected items.');
		for item in display_paths:
			yes.append(item);

		no = []
		no.append('No');
		no.append('Cancel the operation.');

		while len(no) != len(yes):
			no.append('');

		if sublime.platform() == 'osx':
			sublime.set_timeout(lambda:window.show_quick_panel([yes, no], functools.partial(self.on_confirm, paths)), 200);
		else:
			window.show_quick_panel([yes, no], functools.partial(self.on_confirm, paths))

	def on_confirm(self, paths, result):
		if result != -1:
			if result == 0:
				self.run(paths, 'True')

	def is_enabled(self, paths = []):
		return CACHED_SELECTION(paths).len() > 0

	def is_visible(self, paths =[]):
		return not s.get('disabled_menuitem_empty', True)

class SideBarEmptyThread(threading.Thread):
	def __init__(self, paths, key):
		self.paths = paths
		self.key = key
		threading.Thread.__init__(self)

	def run(self):
		paths = self.paths
		key = self.key
		window_set_status(key, 'Emptying…')
		try:
			from .send2trash import send2trash
			for item in SideBarSelection(paths).getSelectedDirectoriesOrDirnames():
				for content in os.listdir(item.path()):
					file = os.path.join(item.path(), content)
					if not SideBarSelection().isNone(file):
						send2trash(file)
				if s.get('close_affected_buffers_when_deleting_even_if_dirty', False):
					item.closeViews()
		except:
			pass
		SideBarProject().refresh();
		window_set_status(key, '')

class SideBarRevealCommand(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		if len(paths) > 1:
			paths = SideBarSelection(paths).getSelectedDirectoriesOrDirnames()
		else:
			paths = SideBarSelection(paths).getSelectedItems()
		for item in paths:
			item.reveal()

	def is_enabled(self, paths = []):
		return CACHED_SELECTION(paths).len() > 0

class SideBarProjectOpenFileCommand(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		project = SideBarProject()
		if project.hasOpenedProject():
			SideBarItem(project.getProjectFile(), False).edit();

	def is_enabled(self, paths = []):
		return SideBarProject().hasOpenedProject()

class SideBarPreviewEditUrlsCommand(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		item = SideBarItem(os.path.dirname(sublime.packages_path())+'/Settings/SideBarEnhancements.json', False)
		item.dirnameCreate();
		item.edit();

class SideBarProjectItemAddCommand(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		project = SideBarProject()
		for item in SideBarSelection(paths).getSelectedDirectories():
			project.add(item.path())

	def is_enabled(self, paths = []):
		return CACHED_SELECTION(paths).hasDirectories() and CACHED_SELECTION(paths).hasProjectDirectories() == False

class SideBarProjectItemRemoveFolderCommand(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		Window().run_command('remove_folder', {"dirs":paths})

	def is_enabled(self, paths =[]):
		selection = CACHED_SELECTION(paths)
		project = SideBarProject()
		return project.hasDirectories() and all([item.path() in project.getDirectories() or not item.exists() for item in selection.getSelectedItems()])

class SideBarProjectItemExcludeCommand(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		project = SideBarProject()
		for item in SideBarSelection(paths).getSelectedItems():
			if item.isDirectory():
				project.excludeDirectory(item.path(), item.pathRelativeFromProject())
			else:
				project.excludeFile(item.path(), item.pathRelativeFromProject())

	def is_enabled(self, paths = []):
		return CACHED_SELECTION(paths).len() > 0 and CACHED_SELECTION(paths).hasProjectDirectories() == False

class SideBarProjectItemExcludeFromIndexCommand(sublime_plugin.WindowCommand):
	def run(self, paths = [], type = 'item'):
		Preferences = sublime.load_settings("Preferences.sublime-settings")
		excluded = Preferences.get("binary_file_patterns", [])
		for item in self.items(paths, type, SideBarSelection(paths)):
			excluded.append(item)
		for k, v in enumerate(excluded):
			excluded[k] = excluded[k].replace('\\', '/')
			excluded[k] = re.sub('([a-z])\:/', '/\\1/', excluded[k], 0, re.I)
			excluded[k] = re.sub('/$', '/**', excluded[k])
		excluded = list(set(excluded))
		excluded = sorted(excluded)
		Preferences.set("binary_file_patterns", excluded);
		sublime.save_settings("Preferences.sublime-settings");

	def is_visible(self, paths = [], type = 'item'):
		return len(self.items(paths, type, CACHED_SELECTION(paths))) > 0

	def description(self, paths = [], type = 'item'):
		items = self.items(paths, type, CACHED_SELECTION(paths))
		return 'Exclude From Index (mark as binary) "'+(",".join(items))+'"'

	def items(self, paths = [], type = 'item', object = None):
		items = []
		if type == 'item':
			for item in object.getSelectedItems():
				if item.isDirectory():
					items.append(re.sub('([a-z])\:/', '/\\1/', (item.path().replace('\\', '/')+'/**'), 0, re.I))
				else:
					items.append(re.sub('([a-z])\:/', '/\\1/', (item.path().replace('\\', '/')), 0, re.I))
		elif type == 'relative':
			for item in object.getSelectedItems():
				if item.isDirectory():
					items.append(item.pathRelativeFromProject().replace('\\', '/')+'/**')
				else:
					items.append(item.pathRelativeFromProject().replace('\\', '/'))
		elif type == 'extension':
			for item in object.getSelectedFiles():
				items.append('*'+item.extension())
		elif type == 'file':
			for item in object.getSelectedFiles():
				items.append(item.name())
		elif type == 'directory':
			for item in object.getSelectedDirectories():
				items.append(item.name() +'/**')
		items = list(set(items))
		return items

class SideBarOpenBrowsersCommand(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		browsers = s.get('open_all_browsers', [])
		if browsers:
			window =  Window()
			for browser in browsers:
				window.run_command("side_bar_open_in_browser", {'paths':paths, 'type':'testing', 'browser':browser})

class SideBarOpenInBrowserCommand(sublime_plugin.WindowCommand):
	def run(self, paths = [], type = False, browser = ""):

		if not browser:
			browser = s.get('default_browser', '')

		if type == False or type == 'testing':
			type = 'url_testing'
		elif type == 'production':
			type = 'url_production'
		else:
			type = 'url_testing'

		SideBarOpenInBrowserThread(paths, type, browser).start()

	def is_enabled(self, paths = []):
		return CACHED_SELECTION(paths).len() > 0

	def is_visible(self, paths =[]):
		return not s.get('disabled_menuitem_open_in_browser', False)

class SideBarOpenInBrowserThread(threading.Thread):
	def __init__(self, paths, type, browser):
		self.paths = paths
		self.type = type
		self.browser = browser
		threading.Thread.__init__(self)

	def run(self):
		paths = self.paths
		type = self.type
		browser = self.browser

		for item in SideBarSelection(paths).getSelectedItems():
			url = item.url(type) or item.uri()
			self.try_open(url, browser)

	def try_open(self, url, browser):
		import subprocess

		if sublime.platform() == 'windows':
			import winreg

		browser = browser.lower().strip();
		items = []

		if browser == 'chrome':
			if sublime.platform() == 'osx':
				items.extend(['open'])
				commands = ['-a', '/Applications/Google Chrome.app', url]
			elif sublime.platform() == 'windows':
				aKey = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders")
				reg_value, reg_type = winreg.QueryValueEx (aKey, "Local AppData")

				if s.get('portable_browser', '') != '':
					items.extend([s.get('portable_browser', '')])
				items.extend([
					'%HOMEPATH%\\AppData\\Local\\Google\\Chrome\\Application\\chrome.exe'

					,reg_value+'\\Chrome\\Application\\chrome.exe'
					,reg_value+'\\Google\\Chrome\\Application\\chrome.exe'
					,'%HOMEPATH%\\Google\\Chrome\\Application\\chrome.exe'
					,'%PROGRAMFILES%\\Google\\Chrome\\Application\\chrome.exe'
					,'%PROGRAMFILES(X86)%\\Google\\Chrome\\Application\\chrome.exe'
					,'%USERPROFILE%\\Local\ Settings\\Application\ Data\\Google\\Chrome\\chrome.exe'
					,'%HOMEPATH%\\Chromium\\Application\\chrome.exe'
					,'%PROGRAMFILES%\\Chromium\\Application\\chrome.exe'
					,'%PROGRAMFILES(X86)%\\Chromium\\Application\\chrome.exe'
					,'%HOMEPATH%\\Local\ Settings\\Application\ Data\\Google\\Chrome\\Application\\chrome.exe'
					,'%HOMEPATH%\\Local Settings\\Application Data\\Google\\Chrome\\Application\\chrome.exe'
					,'chrome.exe'
				])


				commands = ['-new-tab', url]
			else:
				if s.get('portable_browser', '') != '':
					items.extend([s.get('portable_browser', '')])
				items.extend([
					'/usr/bin/google-chrome'
					,'/opt/google/chrome/chrome'
					,'chrome'
					,'google-chrome'
				])
				commands = ['-new-tab', url]

		elif browser == 'canary':
			if sublime.platform() == 'osx':
					items.extend(['open'])
					commands = ['-a', '/Applications/Google Chrome Canary.app', url]
			elif sublime.platform() == 'windows':
				aKey = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders")
				reg_value, reg_type = winreg.QueryValueEx (aKey, "Local AppData")

				if s.get('portable_browser', '') != '':
					items.extend([s.get('portable_browser', '')])
				items.extend([
					'%HOMEPATH%\\AppData\\Local\\Google\\Chrome SxS\\Application\\chrome.exe'

					,reg_value+'\\Chrome SxS\\Application\\chrome.exe'
					,reg_value+'\\Google\\Chrome SxS\\Application\\chrome.exe'
					,'%HOMEPATH%\\Google\\Chrome SxS\\Application\\chrome.exe'
					,'%PROGRAMFILES%\\Google\\Chrome SxS\\Application\\chrome.exe'
					,'%PROGRAMFILES(X86)%\\Google\\Chrome SxS\\Application\\chrome.exe'
					,'%USERPROFILE%\\Local\ Settings\\Application\ Data\\Google\\Chrome SxS\\chrome.exe'
					,'%HOMEPATH%\\Local\ Settings\\Application\ Data\\Google\\Chrome SxS\\Application\\chrome.exe'
					,'%HOMEPATH%\\Local Settings\\Application Data\\Google\\Chrome SxS\\Application\\chrome.exe'
				])

				commands = ['-new-tab', url]

		elif browser == 'chromium':
			if sublime.platform() == 'osx':
				items.extend(['open'])
				commands = ['-a', '/Applications/Chromium.app', url]
			elif sublime.platform() == 'windows':
				aKey = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders")
				reg_value, reg_type = winreg.QueryValueEx (aKey, "Local AppData")
				if s.get('portable_browser', '') != '':
					items.extend([s.get('portable_browser', '')])
				items.extend([
					'%HOMEPATH%\\AppData\\Local\\Google\\Chrome SxS\\Application\\chrome.exe'

					, reg_value+'\\Chromium\\Application\\chromium.exe'
					,'%USERPROFILE%\\Local Settings\\Application Data\\Google\\Chrome\\chromium.exe'
					,'%USERPROFILE%\\Local\ Settings\\Application\ Data\\Google\\Chrome\\chromium.exe'
					,'%HOMEPATH%\\Chromium\\Application\\chromium.exe'
					,'%PROGRAMFILES%\\Chromium\\Application\\chromium.exe'
					,'%PROGRAMFILES(X86)%\\Chromium\\Application\\chromium.exe'
					,'%HOMEPATH%\\Local Settings\\Application\ Data\\Google\\Chrome\\Application\\chromium.exe'
					,'%HOMEPATH%\\Local Settings\\Application Data\\Google\\Chrome\\Application\\chromium.exe'
					,'chromium.exe'

					, reg_value+'\\Chromium\\Application\\chrome.exe'
					,'%USERPROFILE%\\Local Settings\\Application Data\\Google\\Chrome\\chrome.exe'
					,'%USERPROFILE%\\Local\ Settings\\Application\ Data\\Google\\Chrome\\chrome.exe'
					,'%HOMEPATH%\\Chromium\\Application\\chrome.exe'
					,'%PROGRAMFILES%\\Chromium\\Application\\chrome.exe'
					,'%PROGRAMFILES(X86)%\\Chromium\\Application\\chrome.exe'
					,'%HOMEPATH%\\Local\ Settings\\Application\ Data\\Google\\Chrome\\Application\\chrome.exe'
					,'%HOMEPATH%\\Local Settings\\Application Data\\Google\\Chrome\\Application\\chrome.exe'
					,'chrome.exe'

				])
				commands = ['-new-tab', url]
			else:
				if s.get('portable_browser', '') != '':
					items.extend([s.get('portable_browser', '')])
				items.extend([
					'/usr/bin/chromium'
					,'chromium'
					,'/usr/bin/chromium-browser'
					,'chromium-browser'
				])
				commands = ['-new-tab', url]
		elif browser == 'firefox':
			if sublime.platform() == 'osx':
				items.extend(['open'])
				commands = ['-a', '/Applications/Firefox.app', url]
			else:
				if s.get('portable_browser', '') != '':
					items.extend([s.get('portable_browser', '')])
				items.extend([
					'/usr/bin/firefox'

					,'%PROGRAMFILES%\\Firefox Developer Edition\\firefox.exe'
					,'%PROGRAMFILES(X86)%\\Firefox Developer Edition\\firefox.exe'

					,'%PROGRAMFILES%\\Nightly\\firefox.exe'
					,'%PROGRAMFILES(X86)%\\Nightly\\firefox.exe'

					,'%PROGRAMFILES%\\Mozilla Firefox\\firefox.exe'
					,'%PROGRAMFILES(X86)%\\Mozilla Firefox\\firefox.exe'

					,'firefox'
					,'firefox.exe'
				])
				commands = ['-new-tab', url]
		elif browser == 'opera':
			if sublime.platform() == 'osx':
				items.extend(['open'])
				commands = ['-a', '/Applications/Opera.app', url]
			else:
				if s.get('portable_browser', '') != '':
					items.extend([s.get('portable_browser', '')])
				items.extend([
					'/usr/bin/opera'
					,'/usr/bin/opera-next'
					,'/usr/bin/operamobile'

					,'%PROGRAMFILES%\\Opera\\opera.exe'
					,'%PROGRAMFILES(X86)%\\Opera\\opera.exe'

					,'%PROGRAMFILES%\\Opera\\launcher.exe'
					,'%PROGRAMFILES(X86)%\\Opera\\launcher.exe'

					,'%PROGRAMFILES%\\Opera Next\\opera.exe'
					,'%PROGRAMFILES(X86)%\\Opera Next\\opera.exe'

					,'%PROGRAMFILES%\\Opera Mobile Emulator\\OperaMobileEmu.exe'
					,'%PROGRAMFILES(X86)%\\Opera Mobile Emulator\\OperaMobileEmu.exe'

					,'opera'
					,'opera.exe'
				])
				commands = ['-newtab', url]
		elif browser == 'ie':
			if s.get('portable_browser', '') != '':
				items.extend([s.get('portable_browser', '')])
			items.extend([
				'%PROGRAMFILES%\\Internet Explorer\\iexplore.exe'
				,'%PROGRAMFILES(X86)%\\Internet Explorer\\iexplore.exe'

				,'iexplore'
				,'iexplore.exe'
			])
			commands = ['-newtab', url]
		elif browser == 'edge':
			if s.get('portable_browser', '') != '':
				items.extend([s.get('portable_browser', '')])
			items.extend(['open'])
			commands = ['-newtab', url]
		elif browser == 'safari':
			if sublime.platform() == 'osx':
				items.extend(['open'])
				commands = ['-a', 'Safari', url]
			else:
				if s.get('portable_browser', '') != '':
					items.extend([s.get('portable_browser', '')])
				items.extend([
					'/usr/bin/safari'

					,'%PROGRAMFILES%\\Safari\\Safari.exe'
					,'%PROGRAMFILES(X86)%\\Safari\\Safari.exe'

					,'Safari'
					,'Safari.exe'
				])
				commands = ['-new-tab', '-url', url]
		else:
			if s.get('portable_browser', '') != '':
				items.extend([s.get('portable_browser', '')])
			commands = ['-new-tab', url]

		for item in items:
			try:
				command2 = list(commands)
				command2.insert(0, expandVars(item))
				subprocess.Popen(command2)
				return
			except:
				try:
					command2 = list(commands)
					command2.insert(0, item)
					subprocess.Popen(command2)
					return
				except:
					pass
		try:
			if sublime.platform() == 'windows':
				if browser and browser == 'edge':
					commands = ['cmd','/c','start', 'microsoft-edge:' + url]
				else:
					commands = ['cmd','/c','start', '', url]
				subprocess.Popen(commands)
			elif sublime.platform() == 'linux':
				commands = ['xdg-open', url]
				subprocess.Popen(commands)
			else:
				commands = ['open', url]
				subprocess.Popen(commands)
			return
		except:
			pass

		sublime.error_message('Browser "'+browser+'" not found!\nIs installed? Which location...?')

class SideBarOpenInNewWindowCommand(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		import subprocess
		items = []

		executable_path = sublime.executable_path()

		if sublime.platform() == 'osx':
			app_path = executable_path[:executable_path.rfind(".app/")+5]
			executable_path = app_path+"Contents/SharedSupport/bin/subl"

		items.append(executable_path)

		for item in SideBarSelection(paths).getSelectedItems():
			items.append(item.forCwdSystemPath())
			items.append(item.path())
		subprocess.Popen(items, cwd=items[1])

	def is_visible(self, paths =[]):
		return not s.get('disabled_menuitem_open_in_new_window', False)

class SideBarOpenWithFinderCommand(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		import subprocess
		for item in SideBarSelection(paths).getSelectedDirectoriesOrDirnames():
			subprocess.Popen(['open', item.name()], cwd=item.dirname())

	def is_visible(self, paths =[]):
		return sublime.platform() == 'osx'

class SideBarStatusBarFileSize(sublime_plugin.EventListener):

	def on_activated(self, v):
		if v.file_name() and s.get('statusbar_file_size', False):
			try:
				self.show(v, hurry_size(os.path.getsize(v.file_name())))
			except:
				pass

	def on_post_save(self, v):
		if v.file_name() and s.get('statusbar_file_size', False):
			try:
				self.show(v, hurry_size(os.path.getsize(v.file_name())))
			except:
				pass

	def show(self, v, size):
		v.set_status('statusbar_file_size', size);

class SideBarStatusBarModifiedTime(sublime_plugin.EventListener):

	def on_activated(self, v):
		if v.file_name() and s.get('statusbar_modified_time', False):
			try:
				self.show(v, os.path.getmtime(v.file_name()))
			except:
				pass

	def on_post_save(self, v):
		if v.file_name() and s.get('statusbar_modified_time', False):
			try:
				self.show(v, os.path.getmtime(v.file_name()))
			except:
				pass

	def show(self, v, mtime):
		modified_time = time.strftime(s.get('statusbar_modified_time_format', '%A %b %d %H:%M:%S %Y'), time.localtime(mtime))
		if s.get('statusbar_modified_time_locale', '') != '':
			modified_time = modified_time.decode(s.get('statusbar_modified_time_locale', ''))
		v.set_status('statusbar_modified_time', modified_time);

class SideBarDefaultNewFolder(sublime_plugin.EventListener):
	def on_new(self, view):
		paths = SideBarProject().getDirectories()
		if paths:
			view.settings().set('default_dir', paths[0])


class SideBarAutoCloseEmptyGroupsCommand(sublime_plugin.EventListener):
	def on_close(self, view):
		if s.get('auto_close_empty_groups', False):
			sublime.set_timeout(self.run, 250);

	def run(self):
		window = Window()
		if window.num_groups() > 1:
			to_close = []
			for i in range(1, window.num_groups()):
				if len(window.views_in_group(i)) < 1:
					to_close.append(i)
			to_close.reverse()
			for item in to_close:
				window.focus_group(item)
				window.run_command('close_pane')
			if len(to_close) > 0:
				window.focus_group(0)
				window.run_command('close_file')

class SideBarDonateCommand(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		sublime.message_dialog('Sidebar Enhancements: Thanks for your support ^.^')
		browser = s.get('default_browser', '')
		SideBarOpenInBrowserThread('','','').try_open("https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=DD4SL2AHYJGBW", browser)

class zzzzzSideBarCommand(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		pass

	def is_visible(self, paths = []): # <- WORKS AS AN ONPOPUPSHOWN
		Cache.cached = False
		return False
