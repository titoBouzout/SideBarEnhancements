# coding=utf8
import sublime, sublime_plugin
import os

import re
import threading

from sidebar.SideBarItem import SideBarItem
from sidebar.SideBarSelection import SideBarSelection
from sidebar.SideBarProject import SideBarProject

def disable_default():
	default = sublime.packages_path()+'/Default/Side Bar.sublime-menu'
	desired = sublime.packages_path()+'/SideBarEnhancements/disable_default/Side Bar.sublime-menu.txt'
	if file(default, 'r').read() ==  file(desired, 'r').read():
		file(default, 'w+').write('[/*'+file(desired, 'r').read()+'*/]')

	default = sublime.packages_path()+'/Default/Side Bar Mount Point.sublime-menu'
	desired = sublime.packages_path()+'/SideBarEnhancements/disable_default/Side Bar Mount Point.sublime-menu.txt'
	if file(default, 'r').read() ==  file(desired, 'r').read():
		file(default, 'w+').write('[/*'+file(desired, 'r').read()+'*/]')

try:
	disable_default();
except:
	pass

#NOTES
# A "directory" for this plugin is a "directory"
# A "directory" for a user is a "folder"

s = sublime.load_settings('Side Bar.sublime-settings')

class SideBarNewFileCommand(sublime_plugin.WindowCommand):
	def run(self, paths = [], name = ""):
		import functools
		self.window.run_command('hide_panel');
		self.window.show_input_panel("File Name:", name, functools.partial(self.on_done, paths), None, None)

	def on_done(self, paths, name):
		for item in SideBarSelection(paths).getSelectedDirectoriesOrDirnames():
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

	def is_enabled(self, paths = []):
		return SideBarSelection(paths).len() > 0

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

class SideBarOpenCommand(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		for item in SideBarSelection(paths).getSelectedFiles():
			item.open()

	def is_enabled(self, paths = []):
		return SideBarSelection(paths).hasFiles()

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
				subprocess.Popen([application_name, item.pathSystem()], cwd=application_dir, shell=True)
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
		if int(sublime.version()) >= 2136:
			self.window.run_command("show_panel", {"panel": "find_in_files", "where":"<open folders>"})
		elif int(sublime.version()) >= 2134:
			self.window.run_command("show_panel", {"panel": "find_in_files", "where":""})
		else:
			self.window.run_command("show_panel", {"panel": "find_in_files", "location":"<open folders>"})

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
			
			
	######## ########      ######  ########    ###    ########  ######## 
	##       ##     ##    ##    ##    ##      ## ##   ##     ##    ##    
	##       ##     ##    ##          ##     ##   ##  ##     ##    ##    
	######   ########      ######     ##    ##     ## ########     ##    
	##       ##     ##          ##    ##    ######### ##   ##      ##    
	##       ##     ##    ##    ##    ##    ##     ## ##    ##     ##    
	##       ########      ######     ##    ##     ## ##     ##    ##    

class SideBarFindFilesPathContainingCommand(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		import functools
		search_path = sublime.active_window().active_view().file_name()
		view = self.window.new_file() 
		view.settings().set('word_wrap', False)
		view.set_name('Open Files Matching')
		view.set_syntax_file('Packages/SideBarEnhancements/SideBar Results.hidden-tmLanguage')
		view.set_scratch(True)
		edit = view.begin_edit()
		view.settings().set('sidebar_results', True)
		view.settings().set('ignore_mod', False)
		view.settings().set('sidebar_search_path', search_path)
		view.replace(edit, sublime.Region(0, view.size()), "Type to search:     \n\nResults:" + "\n"*100)
		view.sel().clear()
		view.sel().add(sublime.Region(20))
		view.end_edit(edit)
		
		
class SideBarFindResultsViewListener(sublime_plugin.EventListener):  

	def on_modified(self, view):
		if view.settings().get('sidebar_results') == True:
			path = view.settings().get('sidebar_search_path')
			self.view = view
			searchTerm = view.substr(view.line(0)).replace("Type to search:     ", "").strip()
			self.searchTerm = searchTerm
			contents = view.substr(sublime.Region(0, view.size()))
			thread = SideBarFindFilesPathContainingSearchThread([path], searchTerm, view, contents)
			if view.settings().get('ignore_mod') == False:
			# if ignore_mod == False:
					thread.start()
					
					self.check_threads([thread])
			
	def check_threads(self, threads):
		global ignore_mod
		next_threads = []
		for thread in threads:
			if thread.is_alive():
					next_threads.append(thread)
					continue
			if thread.open_results:
				# I have done a quick fix for this...
				# I use your open-include, but I had to modify it to make it just use the absolute paths,
				# and I had to delete the bit that checked if the filename was None, but maybe the final  
				# function should be included in SideBar.py?
				sublime.active_window().run_command("open_results")
				sublime.active_window().focus_view(self.view)
				
				# Maybe you prefer to keep the search window open after opening the results?
				sublime.active_window().run_command("close")
				
			if thread.result:
				view = self.view
				view.settings().set('ignore_mod', True)
				edit = view.begin_edit()
				new_contents = thread.result.lstrip() + "\n"*thread.extra_line_count
				view.replace(edit, sublime.Region(view.line(0).b + 2, view.size()), new_contents);
				
				total_contents = view.substr(sublime.Region(0, view.size()))
				pattern = re.compile("(" + self.searchTerm + ")", re.IGNORECASE)
				
				# Here I am finding the region for the first three lines so
				# that I can test not highlight the searchTerm if it appears
				# in those lines.
				# There may be a better way of doing this:
				line1 = view.full_line(0)
				line2 = view.full_line(line1.b)
				line3 = view.full_line(line2.b)
				first_three_lines = sublime.Region(line1.a, line3.b)
				
				regions = []
				for m in pattern.finditer(total_contents):
					new_region = sublime.Region(m.start(), m.end())
					if first_three_lines.contains(new_region):
						continue
					regions.append(new_region)
				
				# I don't particularly like the default highlight style. I would prefer a more
				# subtle green text or something.
				view.add_regions("highlight_matches", regions, "number")
					
				view.end_edit(edit)
				# ignore_mod = False
				view.settings().set('ignore_mod', False)
		threads = next_threads
		
		if len(threads):
			sublime.set_timeout(lambda: self.check_threads(threads), 100)
			return  
			
	
class SideBarFindFilesPathContainingSearchThread(threading.Thread):
		def __init__(self, paths, searchTerm, view, contents):
				self.result = False
				self.open_results = False
				self.view = view
				self.view_contents = contents
				self.searchTerm = searchTerm
				self.paths = paths
				threading.Thread.__init__(self)

		def run(self):
				self.searchTerm = self.searchTerm.strip()
				self.total = 0
				view = self.view
				match_result = u''
				for item in SideBarSelection(self.paths).getSelectedDirectoriesOrDirnames():
					self.files = []
					self.num_files = 0
					self.find(item.path())
					match_result += ('\n'.join(self.files))+'\n'
					length = len(self.files)
					if length > 1:
						match_result += str(length)+' matches\n'
					elif length > 0:
						match_result += '1 match\n'
					else:
						match_result += 'No match\n'
					self.total = self.total + length

				extra_line_count = 100 - len(match_result.split("\n"))
				self.extra_line_count = extra_line_count
				if extra_line_count < 0:
					extra_line_count = 0
					
				if self.total > 0:          
					# This is my method to check for a return key-press.
					lines = self.view_contents.split("\n")
					if len(lines) > 3:
						# I like the idea of using the return key instead of another shortcut, so
						# I am using this to check if the user presses return, then I will open the results, or
						# selected results with your open-include (not implemented).
						if lines[3] == "Results:":
							# I will check for this value in SideBarFindResultsViewListener.check_threads()
							self.open_results = True
					
					self.result = "Results:\n" + match_result.lstrip() + "\n"*extra_line_count
					return
				else:
					self.result = 'No matches...' + "\n"*100
					return

		def find(self, path):
			if os.path.isfile(path) or os.path.islink(path):
				self.num_files = self.num_files+1
				if self.match(path):
					self.files.append(path)
			else:
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

		def is_enabled(self, paths=[]):
			return SideBarSelection(paths).len() > 0

	
                    
														
	######## ########     ######## ##    ## ########  
	##       ##     ##    ##       ###   ## ##     ## 
	##       ##     ##    ##       ####  ## ##     ## 
	######   ########     ######   ## ## ## ##     ## 
	##       ##     ##    ##       ##  #### ##     ## 
	##       ##     ##    ##       ##   ### ##     ## 
	##       ########     ######## ##    ## ########  
					

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
		window.show_input_panel("BUG!", '', '', None, None)
		window.run_command('hide_panel');

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
		return SideBarSelection(paths).len() > 0

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
		return SideBarSelection(paths).len() > 0

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
		return SideBarSelection(paths).len() > 0

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
		return SideBarSelection(paths).len() > 0

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
		return SideBarSelection(paths).len() > 0

class SideBarCopyTagImgCommand(sublime_plugin.WindowCommand):

	def run(self, paths = []):
		items = []
		for item in SideBarSelection(paths).getSelectedImages():
			try:
				image_type, width, height = self.getImageInfo(item.contentBinary())
				items.append('<img src="'+item.pathAbsoluteFromProjectEncoded()+'" width="'+str(width)+'" height="'+str(height)+'" border="0"/>')
			except:
				items.append('<img src="'+item.pathAbsoluteFromProjectEncoded()+'" border="0"/>')
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
		return SideBarSelection(paths).hasImages()



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
		return SideBarSelection(paths).hasFilesWithExtension('css')

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
		return SideBarSelection(paths).hasFilesWithExtension('js')

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
			self.confirm([item.path() for item in SideBarSelection(paths).getSelectedItems()], [item.pathWithoutProject() for item in SideBarSelection(paths).getSelectedItems()])
		else:
			import sys
			try:
				path = os.path.join(sublime.packages_path(), 'SideBarEnhancements')
				if path not in sys.path:
					sys.path.append(path)
				import send2trash
				for item in SideBarSelection(paths).getSelectedItemsWithoutChildItems():
					if s.get('close_affected_buffers_when_deleting_even_if_dirty', False):
						self.close_affected_buffers(item.path())
					send2trash.send2trash(item.path())
				SideBarProject().refresh();
			except:
				import functools
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

		window.show_quick_panel([yes, no], functools.partial(self.on_confirm, paths))

	def on_confirm(self, paths, result):
		if result != -1:
			if result == 0:
				self.run(paths, 'True')

	def on_done(self, old, new):
		if s.get('close_affected_buffers_when_deleting_even_if_dirty', False):
			self.close_affected_buffers(new)
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

	def remove_safe_dir(self, path):
		if not SideBarSelection().isNone(path):
			try:
				os.rmdir(path)
			except:
				print "Unable to remove folder:\n\n"+path

	def close_affected_buffers(self, path):
		for window in sublime.windows():
			active_view = window.active_view()
			views = []
			for view in window.views():
				if view.file_name():
					views.append(view)
			views.reverse();
			for view in views:
				if path == view.file_name():
					if len(window.views()) == 1:
						window.new_file()
					window.focus_view(view)
					window.run_command('revert')
					window.run_command('close')
				elif view.file_name().find(path+'\\') == 0:
					if len(window.views()) == 1:
						window.new_file()
					window.focus_view(view)
					window.run_command('revert')
					window.run_command('close')
				elif view.file_name().find(path+'/') == 0:
					if len(window.views()) == 1:
						window.new_file()
					window.focus_view(view)
					window.run_command('revert')
					window.run_command('close')

			# try to repaint
			try:
				window.focus_view(active_view)
				window.focus_view(window.active_view())
			except:
				try:
					window.focus_view(window.active_view())
				except:
					pass

	def is_enabled(self, paths = []):
		return SideBarSelection(paths).len() > 0 and SideBarSelection(paths).hasProjectDirectories() == False

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
		import webbrowser
		project = SideBarProject()
		if type == False or type == 'testing':
			url = project.getPreference('url')
		elif type == 'production':
			url = project.getPreference('url_production')
		else:
			url = project.getPreference('url')
		if url:
			if url[-1:] != '/':
				url = url+'/'
			for item in SideBarSelection(paths).getSelectedItems():
				if item.isUnderCurrentProject():
					webbrowser.open_new_tab(url + item.pathRelativeFromProjectEncoded())
				else:
					webbrowser.open_new_tab(item.uri())
		else:
			for item in SideBarSelection(paths).getSelectedItems():
				webbrowser.open_new_tab(item.uri())
			sublime.status_message('Preference "url" was not found in project file.\n"'+project.getProjectFile()+'", opening local file')

	def is_enabled(self, paths = []):
		return SideBarSelection(paths).len() > 0