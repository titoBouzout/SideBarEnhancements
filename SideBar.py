# coding=utf8
import sublime, sublime_plugin
import os

import threading, time

from sidebar.SideBarItem import SideBarItem
from sidebar.SideBarSelection import SideBarSelection
from sidebar.SideBarProject import SideBarProject

from send2trash import send2trash

# needed for getting local app data path on windows
if sublime.platform() == 'windows':
	import _winreg

def expand_vars(path):
	for k, v in os.environ.iteritems():
		# dirty hack, this should be autofixed in python3
		try:
			k = unicode(k.encode('utf8'))
			v = unicode(v.encode('utf8'))
			path = path.replace('%'+k+'%', v).replace('%'+k.lower()+'%', v)
		except:
			pass
	return path
#NOTES
# A "directory" for this plugin is a "directory"
# A "directory" for a user is a "folder"

s = sublime.load_settings('Side Bar.sublime-settings')

def check_version():
	version = '11.13.2012.1305.0';
	if s.get('version') != version:
		SideBarItem(sublime.packages_path()+'/SideBarEnhancements/messages/'+version+'.txt', False).edit();
		s.set('version', version);
		sublime.save_settings('Side Bar.sublime-settings')

sublime.set_timeout(lambda:check_version(), 3000);

class SideBarNewFile2Command(sublime_plugin.WindowCommand):
	def run(self, paths = [], name = ""):
		import functools
		self.window.run_command('hide_panel');
		self.window.show_input_panel("File Name:", name, functools.partial(SideBarNewFileCommand(sublime_plugin.WindowCommand).on_done, paths, True), None, None)

class SideBarNewFileCommand(sublime_plugin.WindowCommand):
	def run(self, paths = [], name = ""):
		import functools
		self.window.run_command('hide_panel');
		self.window.show_input_panel("File Name:", name, functools.partial(self.on_done, paths, False), None, None)

	def on_done(self, paths, relative_to_project, name):
		if relative_to_project and s.get('new_files_relative_to_project_root'):
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

class SideBarNewDirectoryCommand(sublime_plugin.WindowCommand):
	def run(self, paths = [], name = ""):
		import functools
		self.window.run_command('hide_panel');
		self.window.show_input_panel("Folder Name:", name, functools.partial(self.on_done, paths), None, None)

	def on_done(self, paths, name):
		for item in SideBarSelection(paths).getSelectedDirectoriesOrDirnames():
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
		return SideBarSelection(paths).len() > 0

class SideBarEditCommand(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		for item in SideBarSelection(paths).getSelectedFiles():
			item.edit()

	def is_enabled(self, paths = []):
		return SideBarSelection(paths).hasFiles()

	def is_visible(self, paths =[]):
		return not s.get('disabled_menuitem_edit')

class SideBarOpenCommand(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		for item in SideBarSelection(paths).getSelectedFiles():
			item.open()

	def is_enabled(self, paths = []):
		return SideBarSelection(paths).hasFiles()

	def is_visible(self, paths =[]):
		return not s.get('disabled_menuitem_open_run')

class SideBarFilesOpenWithEditApplicationsCommand(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		item = SideBarItem(os.path.join(sublime.packages_path(), 'User', 'SideBarEnhancements', 'Open With', 'Side Bar.sublime-menu'), False)
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
									"extensions":"psd|png|jpg|jpeg"  //any file with these extensions
								}
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
									"extensions":"" //open all even folders
								}
			},
			//application n
			{
				"caption": "Chrome",
				"id": "side-bar-files-open-with-chrome",

				"command": "side_bar_files_open_with",
				"args": {
									"paths": [],
									"application": "C:\\\\Documents and Settings\\\\tito\\\\Configuración local\\\\Datos de programa\\\\Google\\\\Chrome\\\\Application\\\\chrome.exe",
									"extensions":".*" //any file with extension
								}
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
		import sys
		application_dir, application_name = os.path.split(application)
		application_dir  = application_dir.encode(sys.getfilesystemencoding())
		application_name = application_name.encode(sys.getfilesystemencoding())
		application      = application.encode(sys.getfilesystemencoding())

		if extensions == '*':
			extensions = '.*'
		if extensions == '':
			items = SideBarSelection(paths).getSelectedItems()
		else:
			items = SideBarSelection(paths).getSelectedFilesWithExtension(extensions)

		import subprocess
		for item in items:
			if sublime.platform() == 'osx':
				subprocess.Popen(['open', '-a', application, item.nameSystem()], cwd=item.dirnameSystem())
			elif sublime.platform() == 'windows':
				subprocess.Popen([application_name, item.pathSystem()], cwd=expand_vars(application_dir), shell=True)
			else:
				subprocess.Popen([application_name, item.nameSystem()], cwd=item.dirnameSystem())

	def is_enabled(self, paths = [], application = "", extensions = ""):
		if extensions == '*':
			extensions = '.*'
		if extensions == '':
			return SideBarSelection(paths).len() > 0
		else:
			return SideBarSelection(paths).hasFilesWithExtension(extensions)

	def is_visible(self, paths = [], application = "", extensions = ""):
		if extensions == '*':
			extensions = '.*'
		if extensions == '':
			return SideBarSelection(paths).len() > 0
		else:
			has = SideBarSelection(paths).hasFilesWithExtension(extensions)
			return has or (not has and not s.get("hide_open_with_entries_when_there_are_no_applicable"))

class SideBarFindInSelectedCommand(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		items = []
		for item in SideBarSelection(paths).getSelectedItemsWithoutChildItems():
			items.append(item.path())
		self.window.run_command('hide_panel');
		if int(sublime.version()) >= 2134:
			self.window.run_command("show_panel", {"panel": "find_in_files", "where":",".join(items) })
		else:
			self.window.run_command("show_panel", {"panel": "find_in_files", "location":",".join(items) })

	def is_enabled(self, paths = []):
		return SideBarSelection(paths).len() > 0

class SideBarFindInParentCommand(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		items = []
		for item in SideBarSelection(paths).getSelectedItems():
			items.append(item.dirname())
		items = list(set(items))
		self.window.run_command('hide_panel');
		if int(sublime.version()) >= 2134:
			self.window.run_command("show_panel", {"panel": "find_in_files", "where":",".join(items) })
		else:
			self.window.run_command("show_panel", {"panel": "find_in_files", "location":",".join(items) })

	def is_enabled(self, paths = []):
		return SideBarSelection(paths).len() > 0

class SideBarFindInProjectFoldersCommand(sublime_plugin.WindowCommand):
	def run(self):
		self.window.run_command('hide_panel');
		if int(sublime.version()) >= 2137:
			self.window.run_command("show_panel", {"panel": "find_in_files", "where":"<project>"})
		elif int(sublime.version()) >= 2136:
			self.window.run_command("show_panel", {"panel": "find_in_files", "where":"<open folders>"})
		elif int(sublime.version()) >= 2134:
			self.window.run_command("show_panel", {"panel": "find_in_files", "where":""})
		else:
			self.window.run_command("show_panel", {"panel": "find_in_files", "location":"<open folders>"})

class SideBarFindInProjectCommand(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		self.window.run_command('hide_panel');
		if int(sublime.version()) >= 2137:
			self.window.run_command("show_panel", {"panel": "find_in_files", "where":"<project>"})
		elif int(sublime.version()) >= 2136:
			self.window.run_command("show_panel", {"panel": "find_in_files", "where":"<open folders>"})
		elif int(sublime.version()) >= 2134:
			self.window.run_command("show_panel", {"panel": "find_in_files", "where":""})
		else:
			self.window.run_command("show_panel", {"panel": "find_in_files", "location":"<open folders>"})

	def is_visible(self, paths = []):
		return not s.get('disabled_menuitem_find_in_project')

class SideBarFindInProjectFolderCommand(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		items = []
		for item in SideBarSelection(paths).getSelectedItemsWithoutChildItems():
			items.append(SideBarProject().getDirectoryFromPath(item.path()))
		items = list(set(items))
		if items:
			self.window.run_command('hide_panel');
			self.window.run_command("show_panel", {"panel": "find_in_files", "where":",".join(items)})

class SideBarFindInFilesWithExtensionCommand(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		items = []
		for item in SideBarSelection(paths).getSelectedItems():
			items.append('*'+item.extension())
		items = list(set(items))
		self.window.run_command('hide_panel');
		if int(sublime.version()) >= 2134:
			self.window.run_command("show_panel", {"panel": "find_in_files", "where":",".join(items) })
		else:
			self.window.run_command("show_panel", {"panel": "find_in_files", "location":",".join(items) })

	def is_enabled(self, paths = []):
		return SideBarSelection(paths).hasFiles()

	def description(self, paths = []):
		items = []
		for item in SideBarSelection(paths).getSelectedFiles():
			items.append('*'+item.extension())
		items = list(set(items))
		if len(items) > 1:
			return 'In Files With Extensions '+(",".join(items))+u'…'
		elif len(items) > 0:
			return 'In Files With Extension '+(",".join(items))+u'…'
		else:
			return u'In Files With Extension…'


sidebar_instant_search = 0

class SideBarFindFilesPathContainingCommand(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		global sidebar_instant_search
		if paths == [] and SideBarProject().getDirectories():
			paths = SideBarProject().getDirectories()
		else:
			paths = [item.path() for item in SideBarSelection(paths).getSelectedDirectoriesOrDirnames()]
		if paths == []:
			return
		view = self.window.new_file()
		view.settings().set('word_wrap', False)
		view.set_name('Instant File Search')
		view.set_syntax_file('Packages/SideBarEnhancements/SideBar Results.hidden-tmLanguage')
		view.set_scratch(True)
		edit = view.begin_edit()
		view.settings().set('sidebar_instant_search_paths', paths)
		view.replace(edit, sublime.Region(0, view.size()), "Type to search: ")
		view.end_edit(edit)
		view.sel().clear()
		view.sel().add(sublime.Region(16))
		sidebar_instant_search += 1

	def is_enabled(self, paths=[]):
		return True

class SideBarFindResultsViewListener(sublime_plugin.EventListener):

	def on_modified(self, view):
		global sidebar_instant_search
		if sidebar_instant_search > 0 and view.settings().has('sidebar_instant_search_paths'):
			row, col = view.rowcol(view.sel()[0].begin())
			if row != 0 or not view.sel()[0].empty():
				return
			paths = view.settings().get('sidebar_instant_search_paths')
			searchTerm = view.substr(view.line(0)).replace("Type to search:", "").strip()
			start_time = time.time()
			view.settings().set('sidebar_search_paths_start_time', start_time)
			if searchTerm:
				sublime.set_timeout(lambda:SideBarFindFilesPathContainingSearchThread(paths, searchTerm, view, start_time).start(), 300)

	def on_close(self, view):
		if view.settings().has('sidebar_instant_search_paths'):
			global sidebar_instant_search
			sidebar_instant_search -= 1

class SideBarFindFilesPathContainingSearchThread(threading.Thread):
		def __init__(self, paths, searchTerm, view, start_time):
			if view.settings().get('sidebar_search_paths_start_time') != start_time:
				self.should_run = False
			else:
				self.should_run = True
			self.view = view
			self.searchTerm = searchTerm
			self.paths = paths
			self.start_time = start_time
			threading.Thread.__init__(self)

		def run(self):
			if not self.should_run:
				return
			# print 'run forrest run'
			self.total = 0
			self.highlight_from = 0
			self.match_result = u''
			self.match_result += 'Type to search: '+self.searchTerm+'\n'
			for item in SideBarSelection(self.paths).getSelectedDirectoriesOrDirnames():
				self.files = []
				self.num_files = 0
				self.find(item.path())
				self.match_result += '\n'
				length = len(self.files)
				if length > 1:
					self.match_result += str(length)+' matches'
				elif length > 0:
					self.match_result += '1 match'
				else:
					self.match_result += 'No match'
				self.match_result += ' in '+str(self.num_files)+' files for term "'+self.searchTerm+'" under \n"'+item.path()+'"\n\n'
				if self.highlight_from == 0:
					self.highlight_from = len(self.match_result)
				self.match_result += ('\n'.join(self.files))
				self.total = self.total + length
			self.match_result += '\n'
			sublime.set_timeout(lambda:self.on_done(), 0)

		def on_done(self):
			if self.start_time == self.view.settings().get('sidebar_search_paths_start_time'):
				view = self.view;
				edit = view.begin_edit()
				sel = sublime.Region(view.sel()[0].begin(), view.sel()[0].end())
				view.replace(edit, sublime.Region(0, view.size()), self.match_result);
				view.end_edit(edit)
				view.erase_regions("sidebar_search_instant_highlight")
				if self.total < 30000 and len(self.searchTerm) > 1:
					regions = [item for item in view.find_all(self.searchTerm, sublime.LITERAL|sublime.IGNORECASE) if item.begin() >= self.highlight_from]
					view.add_regions("sidebar_search_instant_highlight", regions, 'string', sublime.DRAW_EMPTY|sublime.DRAW_OUTLINED|sublime.DRAW_EMPTY_AS_OVERWRITE)
				view.sel().clear()
				view.sel().add(sel)

		def find(self, path):
			if os.path.isfile(path) or os.path.islink(path):
				self.num_files = self.num_files+1
				if self.match(path):
					self.files.append(path)
			elif os.path.isdir(path):
				for content in os.listdir(path):
					file = os.path.join(path, content)
					if os.path.isfile(file) or os.path.islink(file):
						self.num_files = self.num_files+1
						if self.match(file):
							self.files.append(file)
					else:
						self.find(file)

		def match(self, path):
			return False if path.lower().find(self.searchTerm.lower()) == -1 else True

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
		return SideBarSelection(paths).len() > 0 and SideBarSelection(paths).hasProjectDirectories() == False


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
		return SideBarSelection(paths).len() > 0

class SideBarPasteCommand(sublime_plugin.WindowCommand):
	def run(self, paths = [], in_parent = 'False', test = 'True', replace = 'False'):
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
									sublime.error_message("Unable to cut and paste, destination exists.")
									return
							except:
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
									sublime.error_message("Unable to copy and paste, destination exists.")
									return
							except:
								sublime.error_message("Unable to copy:\n\n"+path.path()+"\n\nto\n\n"+new)
								return

			if test == 'True' and len(already_exists_paths):
				self.confirm(paths, in_parent, already_exists_paths)
			elif test == 'True' and not len(already_exists_paths):
				self.run(paths, in_parent, 'False', 'False')
			elif test == 'False':
				cut = s.set('cut', '')
				SideBarProject().refresh();

	def confirm(self, paths, in_parent, data):
		import functools
		window = sublime.active_window()
		# window.show_input_panel("BUG!", '', '', None, None)
		# window.run_command('hide_panel');

		yes = []
		yes.append('Yes, Replace the following items:');
		for item in data:
			yes.append(SideBarItem(item, os.path.isdir(item)).pathWithoutProject())

		no = []
		no.append('No');
		no.append('Continue without replacing');

		window.show_quick_panel([yes, no], functools.partial(self.on_done, paths, in_parent))

	def on_done(self, paths, in_parent, result):
		if result != -1:
			if result == 0:
				self.run(paths, in_parent, 'False', 'True')
			else:
				self.run(paths, in_parent, 'False', 'False')

	def is_enabled(self, paths = [], in_parent = False):
		s = sublime.load_settings("SideBarEnhancements/Clipboard.sublime-settings")
		return s.get('cut', '') + s.get('copy', '') != '' and len(SideBarSelection(paths).getSelectedDirectoriesOrDirnames()) == 1

	def is_visible(self, paths = [], in_parent = False):
		if in_parent == 'True':
			return not s.get('disabled_menuitem_paste_in_parent')
		else:
			return True

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
		return SideBarSelection(paths).len() > 0

	def is_visible(self, paths =[]):
		return not s.get('disabled_menuitem_copy_name')

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
		return SideBarSelection(paths).len() > 0


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
		return SideBarSelection(paths).len() > 0

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
		return SideBarSelection(paths).len() > 0

	def is_visible(self, paths =[]):
		return not s.get('disabled_menuitem_copy_dir_path')

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
		return SideBarSelection(paths).len() > 0

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
		return SideBarSelection(paths).len() > 0 and SideBarSelection(paths).hasItemsUnderProject()



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
		return SideBarSelection(paths).len() > 0 and SideBarSelection(paths).hasItemsUnderProject()

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
		return SideBarSelection(paths).len() > 0

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
		return SideBarSelection(paths).len() > 0

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
		return SideBarSelection(paths).len() > 0 and SideBarSelection(paths).hasItemsUnderProject()

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
		return SideBarSelection(paths).len() > 0 and SideBarSelection(paths).hasItemsUnderProject()

	def is_visible(self, paths =[]):
		return not s.get('disabled_menuitem_copy_path')

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
		return SideBarSelection(paths).len() > 0 and SideBarSelection(paths).hasItemsUnderProject()

class SideBarCopyTagImgCommand(sublime_plugin.WindowCommand):

	def run(self, paths = []):
		items = []
		for item in SideBarSelection(paths).getSelectedImages():
			try:
				image_type, width, height = self.getImageInfo(item.contentBinary())
				items.append('<img src="'+item.pathAbsoluteFromProjectEncoded()+'" width="'+str(width)+'" height="'+str(height)+'">')
			except:
				items.append('<img src="'+item.pathAbsoluteFromProjectEncoded()+'">')
		if len(items) > 0:
			sublime.set_clipboard("\n".join(items));
			if len(items) > 1 :
				sublime.status_message("Items copied")
			else :
				sublime.status_message("Item copied")

	#Project:http://code.google.com/p/bfg-pages/
	#License:http://www.opensource.org/licenses/bsd-license.php
	def getImageInfo(self, data):
		import StringIO
		import struct
		data = str(data)
		size = len(data)
		height = -1
		width = -1
		content_type = ''

		# handle GIFs
		if (size >= 10) and data[:6] in ('GIF87a', 'GIF89a'):
			# Check to see if content_type is correct
			content_type = 'image/gif'
			w, h = struct.unpack("<HH", data[6:10])
			width = int(w)
			height = int(h)

		# See PNG 2. Edition spec (http://www.w3.org/TR/PNG/)
		# Bytes 0-7 are below, 4-byte chunk length, then 'IHDR'
		# and finally the 4-byte width, height
		elif ((size >= 24) and data.startswith('\211PNG\r\n\032\n')
					and (data[12:16] == 'IHDR')):
			content_type = 'image/png'
			w, h = struct.unpack(">LL", data[16:24])
			width = int(w)
			height = int(h)

		# Maybe this is for an older PNG version.
		elif (size >= 16) and data.startswith('\211PNG\r\n\032\n'):
			# Check to see if we have the right content type
			content_type = 'image/png'
			w, h = struct.unpack(">LL", data[8:16])
			width = int(w)
			height = int(h)

		# handle JPEGs
		elif (size >= 2) and data.startswith('\377\330'):
			content_type = 'image/jpeg'
			jpeg = StringIO.StringIO(data)
			jpeg.read(2)
			b = jpeg.read(1)
			try:
				while (b and ord(b) != 0xDA):
					while (ord(b) != 0xFF): b = jpeg.read(1)
					while (ord(b) == 0xFF): b = jpeg.read(1)
					if (ord(b) >= 0xC0 and ord(b) <= 0xC3):
						jpeg.read(3)
						h, w = struct.unpack(">HH", jpeg.read(4))
						break
					else:
						jpeg.read(int(struct.unpack(">H", jpeg.read(2))[0])-2)
					b = jpeg.read(1)
				width = int(w)
				height = int(h)
			except struct.error:
				pass
			except ValueError:
				pass
		return content_type, width, height

	def is_enabled(self, paths = []):
		return SideBarSelection(paths).hasImages() and SideBarSelection(paths).hasItemsUnderProject()

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
		return SideBarSelection(paths).hasFilesWithExtension('css') and SideBarSelection(paths).hasItemsUnderProject()

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
		return SideBarSelection(paths).hasFilesWithExtension('js') and SideBarSelection(paths).hasItemsUnderProject()

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
		return SideBarSelection(paths).hasFiles()

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
		return SideBarSelection(paths).hasFiles()

class SideBarCopyUrlCommand(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		items = []
		project = SideBarProject()
		url = project.getPreference('url_production')
		if url:
			if url[-1:] != '/':
				url = url+'/'
			for item in SideBarSelection(paths).getSelectedItems():
				if item.isUnderCurrentProject():
					items.append(url + item.pathRelativeFromProjectEncoded())

		if len(items) > 0:
			sublime.set_clipboard("\n".join(items));
			if len(items) > 1 :
				sublime.status_message("Items URL copied")
			else :
				sublime.status_message("Item URL copied")

	def is_enabled(self, paths = []):
		return SideBarSelection(paths).hasItemsUnderProject()

class SideBarDuplicateCommand(sublime_plugin.WindowCommand):
	def run(self, paths = [], new = False):
		import functools
		self.window.run_command('hide_panel');
		self.window.show_input_panel("Duplicate As:", new or SideBarSelection(paths).getSelectedItems()[0].path(), functools.partial(self.on_done, SideBarSelection(paths).getSelectedItems()[0].path()), None, None)

	def on_done(self, old, new):
		item = SideBarItem(old, os.path.isdir(old))
		try:
			if not item.copy(new):
				sublime.error_message("Unable to duplicate, destination exists.")
				self.run([old], new)
				return
		except:
			sublime.error_message("Unable to copy:\n\n"+old+"\n\nto\n\n"+new)
			self.run([old], new)
			return
		item = SideBarItem(new, os.path.isdir(new))
		if item.isFile():
			item.edit();
		SideBarProject().refresh();

	def is_enabled(self, paths = []):
		return SideBarSelection(paths).len() == 1 and SideBarSelection(paths).hasProjectDirectories() == False

class SideBarRenameCommand(sublime_plugin.WindowCommand):
	def run(self, paths = [], newLeaf = False):
		import functools
		branch, leaf = os.path.split(SideBarSelection(paths).getSelectedItems()[0].path())
		self.window.run_command('hide_panel');
		self.window.show_input_panel("New Name:", newLeaf or leaf, functools.partial(self.on_done, SideBarSelection(paths).getSelectedItems()[0].path(), branch), None, None)

	def on_done(self, old, branch, leaf):
		self.window.run_command('hide_panel');
		leaf = leaf.strip();
		new = os.path.join(branch, leaf)
		item = SideBarItem(old, os.path.isdir(old))
		try:
			if not item.move(new):
				sublime.error_message("Unable to rename, destination exists.")
				self.run([old], leaf)
				return
		except:
			sublime.error_message("Unable to rename:\n\n"+old+"\n\nto\n\n"+new)
			self.run([old], leaf)
			raise
			return
		SideBarProject().refresh();

	def is_enabled(self, paths = []):
		return SideBarSelection(paths).len() == 1 and SideBarSelection(paths).hasProjectDirectories() == False

class SideBarMoveCommand(sublime_plugin.WindowCommand):
	def run(self, paths = [], new = False):
		import functools
		self.window.run_command('hide_panel');
		self.window.show_input_panel("New Location:", new or SideBarSelection(paths).getSelectedItems()[0].path(), functools.partial(self.on_done, SideBarSelection(paths).getSelectedItems()[0].path()), None, None)

	def on_done(self, old, new):
		item = SideBarItem(old, os.path.isdir(old))
		try:
			if not item.move(new):
				sublime.error_message("Unable to move, destination exists.")
				self.run([old], new)
				return
		except:
			sublime.error_message("Unable to move:\n\n"+old+"\n\nto\n\n"+new)
			self.run([old], new)
			return
		SideBarProject().refresh();

	def is_enabled(self, paths = []):
		return SideBarSelection(paths).len() == 1 and SideBarSelection(paths).hasProjectDirectories() == False

class SideBarDeleteCommand(sublime_plugin.WindowCommand):
	def run(self, paths = [], confirmed = 'False'):

		if confirmed == 'False' and s.get('confirm_before_deleting', True):
			if sublime.platform() == 'osx':
				if sublime.ok_cancel_dialog('delete the selected items?'):
					self.run(paths, 'True')
			else:
				self.confirm([item.path() for item in SideBarSelection(paths).getSelectedItems()], [item.pathWithoutProject() for item in SideBarSelection(paths).getSelectedItems()])
		else:
			try:
				for item in SideBarSelection(paths).getSelectedItemsWithoutChildItems():
					if s.get('close_affected_buffers_when_deleting_even_if_dirty', False):
						item.close_associated_buffers()
					send2trash(item.path())
				SideBarProject().refresh();
			except:
				import functools
				self.window.show_input_panel("BUG!", '', '', None, None)
				self.window.run_command('hide_panel');
				self.window.show_input_panel("Permanently Delete:", SideBarSelection(paths).getSelectedItems()[0].path(), functools.partial(self.on_done, SideBarSelection(paths).getSelectedItems()[0].path()), None, None)

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
			item.close_associated_buffers()
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
				print "Unable to remove file:\n\n"+path
		else:
			print 'path is none'
			print path

	def remove_safe_dir(self, path):
		if not SideBarSelection().isNone(path):
			try:
				os.rmdir(path)
			except:
				print "Unable to remove folder:\n\n"+path

	def is_enabled(self, paths = []):
		return SideBarSelection(paths).len() > 0 and SideBarSelection(paths).hasProjectDirectories() == False


class SideBarEmptyCommand(sublime_plugin.WindowCommand):
	def run(self, paths = [], confirmed = 'False'):

		if confirmed == 'False' and s.get('confirm_before_deleting', True):
			if sublime.platform() == 'osx':
				if sublime.ok_cancel_dialog('empty the content of the folder?'):
					self.run(paths, 'True')
			else:
				self.confirm([item.path() for item in SideBarSelection(paths).getSelectedDirectoriesOrDirnames()], [item.pathWithoutProject() for item in SideBarSelection(paths).getSelectedDirectoriesOrDirnames()])
		else:
			try:
				for item in SideBarSelection(paths).getSelectedDirectoriesOrDirnames():
					for content in os.listdir(item.path()):
						file = os.path.join(item.path(), content)
						if not SideBarSelection().isNone(file):
							send2trash(file)
					if s.get('close_affected_buffers_when_deleting_even_if_dirty', False):
						item.close_associated_buffers()
			except:
				pass
			SideBarProject().refresh();

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
		if sublime.platform() == 'osx':
			sublime.set_timeout(lambda:window.show_quick_panel([yes, no], functools.partial(self.on_confirm, paths)), 200);
		else:
			window.show_quick_panel([yes, no], functools.partial(self.on_confirm, paths))

	def on_confirm(self, paths, result):
		if result != -1:
			if result == 0:
				self.run(paths, 'True')

	def is_enabled(self, paths = []):
		return SideBarSelection(paths).len() > 0

	def is_visible(self, paths =[]):
		return not s.get('disabled_menuitem_empty')

class SideBarRevealCommand(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		for item in SideBarSelection(paths).getSelectedItems():
			item.reveal()

	def is_enabled(self, paths = []):
		return SideBarSelection(paths).len() > 0

class SideBarProjectOpenFileCommand(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		project = SideBarProject()
		if project.hasOpenedProject():
			SideBarItem(project.getProjectFile(), False).edit();

class SideBarProjectOpenProjectPreviewUrlsFileCommand(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		SideBarItem(sublime.packages_path()+'/../Settings/SideBarEnhancements.json', False).edit();

class SideBarProjectItemAddCommand(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		project = SideBarProject()
		if project.hasOpenedProject():
			for item in SideBarSelection(paths).getSelectedDirectories():
				project.rootAdd(item.path())

	def is_enabled(self, paths = []):
		return SideBarSelection(paths).hasDirectories()

class SideBarProjectItemExcludeCommand(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		project = SideBarProject()
		if project.hasOpenedProject():
			for item in SideBarSelection(paths).getSelectedItems():
				if item.isDirectory():
					project.excludeDirectory(item.path())
				else:
					project.excludeFile(item.path())

	def is_enabled(self, paths = []):
		return SideBarSelection(paths).len() > 0

class SideBarOpenInBrowserCommand(sublime_plugin.WindowCommand):
	def run(self, paths = [], type = False):

		browser = s.get("default_browser")
		if browser == '':
			browser = 'firefox'

		if type == False or type == 'testing':
			type = 'url_testing'
		elif type == 'production':
			type = 'url_production'
		else:
			type = 'url_testing'

		for item in SideBarSelection(paths).getSelectedItems():
			if item.projectURL(type):
				self.try_open(item.projectURL(type), browser)
			else:
				self.try_open(item.uri(), browser)

	# def run(self, paths = [], type = False):
	# 	import webbrowser
	# 	try:
	# 		browser = webbrowser.get(s.get("default_browser"))
	# 	except:
	# 		browser = webbrowser

	# 	if type == False or type == 'testing':
	# 		type = 'url_testing'
	# 	elif type == 'production':
	# 		type = 'url_production'
	# 	else:
	# 		type = 'url_testing'

	# 	for item in SideBarSelection(paths).getSelectedItems():
	# 		if item.projectURL(type):
	# 			browser.open_new_tab(item.projectURL(type) + item.pathRelativeFromProjectEncoded())
	# 		else:
	# 			browser.open_new_tab(item.uri())

	def try_open(self, url, browser):
		import subprocess

		browser = browser.lower().strip();
		items = []

		if browser == 'chrome':
			if sublime.platform() == 'osx':
				items.extend(['open'])
				commands = ['-a', '/Applications/Google Chrome.app', url]
			elif sublime.platform() == 'windows':
				# read local app data path from registry
				aKey = _winreg.OpenKey(_winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders")
				reg_value, reg_type = _winreg.QueryValueEx (aKey, "Local AppData")

				if s.get('portable_browser') != '':
					items.extend([s.get('portable_browser')])
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

				if s.get('portable_browser') != '':
					items.extend([s.get('portable_browser')])
				items.extend([
					'/usr/bin/google-chrome'
					,'chrome'
					,'google-chrome'
				])
				commands = ['-new-tab', url]

		elif browser == 'chromium':
			if sublime.platform() == 'osx':
				items.extend(['open'])
				commands = ['-a', '/Applications/Chromium.app', url]
			elif sublime.platform() == 'windows':
				# read local app data path from registry
				aKey = _winreg.OpenKey(_winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders")
				reg_value, reg_type = _winreg.QueryValueEx (aKey, "Local AppData")
				if s.get('portable_browser') != '':
					items.extend([s.get('portable_browser')])
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
				if s.get('portable_browser') != '':
					items.extend([s.get('portable_browser')])
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
				if s.get('portable_browser') != '':
					items.extend([s.get('portable_browser')])
				items.extend([
					'/usr/bin/firefox'

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
				if s.get('portable_browser') != '':
					items.extend([s.get('portable_browser')])
				items.extend([
					'/usr/bin/opera'
					,'/usr/bin/opera-next'
					,'/usr/bin/operamobile'

					,'%PROGRAMFILES%\\Opera\\opera.exe'
					,'%PROGRAMFILES(X86)%\\Opera\\opera.exe'

					,'%PROGRAMFILES%\\Opera Next\\opera.exe'
					,'%PROGRAMFILES(X86)%\\Opera Next\\opera.exe'

					,'%PROGRAMFILES%\\Opera Mobile Emulator\\OperaMobileEmu.exe'
					,'%PROGRAMFILES(X86)%\\Opera Mobile Emulator\\OperaMobileEmu.exe'

					,'opera'
					,'opera.exe'
				])
				commands = ['-newtab', url]
		elif browser == 'safari':
			if sublime.platform() == 'osx':
				items.extend(['open'])
				commands = ['-a', 'Safari', url]
			else:
				if s.get('portable_browser') != '':
					items.extend([s.get('portable_browser')])
				items.extend([
					'/usr/bin/safari'

					,'%PROGRAMFILES%\\Safari\\Safari.exe'
					,'%PROGRAMFILES(X86)%\\Safari\\Safari.exe'

					,'Safari'
					,'Safari.exe'
				])
				commands = ['-new-tab', '-url', url]
		else:
			sublime.error_message('Browser "'+browser+'" not found!\nUse any of the following: firefox, chrome, chromium, opera, safari')
			return

		for item in items:
			try:
				command2 = list(commands)
				command2.insert(0, expand_vars(item))
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

		sublime.error_message('Browser "'+browser+'" not found!\nIs installed? Which location...?')

	def is_enabled(self, paths = []):
		return SideBarSelection(paths).len() > 0

	def is_visible(self, paths =[]):
		return not s.get('disabled_menuitem_open_in_browser')

class SideBarOpenInNewWindowCommand(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		import subprocess
		for item in SideBarSelection(paths).getSelectedDirectoriesOrDirnames():
			if sublime.platform() == 'osx':
				try:
					subprocess.Popen(['subl', '.'], cwd=item.pathSystem())
				except:
					try:
						subprocess.Popen(['sublime', '.'], cwd=item.pathSystem())
					except:
						subprocess.Popen(['/Applications/Sublime Text 2.app/Contents/SharedSupport/bin/subl', '.'], cwd=item.pathSystem())
			elif sublime.platform() == 'windows':
				try:
					subprocess.Popen(['subl', '.'], cwd=item.pathSystem(), shell=True)
				except:
					try:
						subprocess.Popen(['sublime', '.'], cwd=item.pathSystem(), shell=True)
					except:
						subprocess.Popen(['sublime_text.exe', '.'], cwd=item.pathSystem(), shell=True)
			else:
				try:
					subprocess.Popen(['subl', '.'], cwd=item.pathSystem())
				except:
					subprocess.Popen(['sublime', '.'], cwd=item.pathSystem())

	def is_visible(self, paths =[]):
		return not s.get('disabled_menuitem_open_in_new_window')

class SideBarOpenWithFinderCommand(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		import subprocess
		for item in SideBarSelection(paths).getSelectedDirectoriesOrDirnames():
			subprocess.Popen(['open', item.nameSystem()], cwd=item.dirnameSystem())

	def is_visible(self, paths =[]):
		return sublime.platform() == 'osx'

class SideBarProjectItemRemoveFolderCommand(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		self.window.run_command('remove_folder', {"dirs":paths})

	def is_enabled(self, paths =[]):
		return SideBarSelection(paths).len() == 1 and SideBarSelection(paths).hasProjectDirectories() == True
