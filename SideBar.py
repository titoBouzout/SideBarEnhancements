# coding=utf8
import sublime, sublime_plugin
import os

from SideBarItem import SideBarItem
from SideBarSelection import SideBarSelection
from SideBarProject import SideBarProject
from Utils import uniqueList

#NOTES
# A "directory" for this plugin is a "directory"
# A "directory" for a user is a "folder"

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
		SideBarProject.refresh();

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
		SideBarProject.refresh();

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
									"application": "C:\\\\Archivos de programa\\\\Adobe\\\\Adobe Photoshop CS4\\\\Photoshop.exe",
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
									"application": "C:\\\\Archivos de programa\\\\SeaMonkey\\\\seamonkey.exe",
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
		application	 		 = application.encode(sys.getfilesystemencoding())

		if extensions == '*':
			extensions = '.*'
		if extensions == '':
			items = SideBarSelection(paths).getSelectedItems()
		else:
			items = SideBarSelection(paths).getSelectedFilesWithExtension(extensions)

		import subprocess
		for item in items:
			if sys.platform == 'darwin':
				subprocess.Popen(['open', '-a', application, item.nameSystem()], cwd=item.dirnameSystem())
			elif sys.platform == 'win32':
				subprocess.Popen([application_name, item.pathSystem()], cwd=application_dir, shell=True)
			else:
				subprocess.Popen([application_name, item.nameSystem()], cwd=item.dirnameSystem())

	def is_enabled(self, paths = [], application = "", extensions = ""):
		if extensions == '*':
			extensions = '.*'
		if extensions == '':
			return len(paths) > 0
		else:
			return SideBarSelection(paths).hasFilesWithExtension(extensions)

class SideBarFindInSelectedCommand(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		items = []
		for item in SideBarSelection(paths).getSelectedItemsWithoutChildItems():
			items.append(item.path())
		self.window.run_command('hide_panel');
		if sublime.version() >= 2134:
			self.window.run_command("show_panel", {"panel": "find_in_files", "where":",".join(items) })
		else:
			self.window.run_command("show_panel", {"panel": "find_in_files", "location":",".join(items) })

	def is_enabled(self, paths = []):
		return len(paths) > 0

class SideBarFindInParentCommand(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		items = []
		for item in SideBarSelection(paths).getSelectedItems():
			items.append(item.dirname())
		items = uniqueList(items)
		self.window.run_command('hide_panel');
		if sublime.version() >= 2134:
			self.window.run_command("show_panel", {"panel": "find_in_files", "where":",".join(items) })
		else:
			self.window.run_command("show_panel", {"panel": "find_in_files", "location":",".join(items) })

	def is_enabled(self, paths = []):
		return len(paths) > 0

class SideBarFindInProjectFoldersCommand(sublime_plugin.WindowCommand):
	def run(self):
		self.window.run_command('hide_panel');
		if sublime.version() >= 2136:
			self.window.run_command("show_panel", {"panel": "find_in_files", "where":"<open folders>"})
		elif sublime.version() >= 2134:
			self.window.run_command("show_panel", {"panel": "find_in_files", "where":""})
		else:
			self.window.run_command("show_panel", {"panel": "find_in_files", "location":"<open folders>"})

class SideBarFindInProjectFolderCommand(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		items = []
		for item in SideBarSelection(paths).getSelectedItemsWithoutChildItems():
			items.append(SideBarProject().getDirectoryFromPath(item.path()))
		items = uniqueList(items)
		if items:
			self.window.run_command('hide_panel');
			self.window.run_command("show_panel", {"panel": "find_in_files", "where":",".join(items)})

class SideBarFindInFilesWithExtensionCommand(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		items = []
		for item in SideBarSelection(paths).getSelectedItems():
			items.append('*'+item.extension())
		items = uniqueList(items)
		self.window.run_command('hide_panel');
		if sublime.version() >= 2134:
			self.window.run_command("show_panel", {"panel": "find_in_files", "where":",".join(items) })
		else:
			self.window.run_command("show_panel", {"panel": "find_in_files", "location":",".join(items) })

	def is_enabled(self, paths = []):
		return SideBarSelection(paths).hasFiles()

	def description(self, paths = []):
		items = []
		for item in SideBarSelection(paths).getSelectedFiles():
			items.append('*'+item.extension())
		items = uniqueList(items)
		if len(items) > 1:
			return 'In Files With Extensions '+(",".join(items))+u'…'
		elif len(items) > 0:
			return 'In Files With Extension '+(",".join(items))+u'…'
		else:
			return u'In Files With Extension…'

class SideBarFindFilesPathContainingCommand(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		import functools
		self.window.run_command('hide_panel');
		self.window.show_input_panel("File Path Containing:", '', functools.partial(self.on_done, paths), None, None)

	def on_done(self, paths, searchTerm):
		self.searchTerm = searchTerm.strip()
		self.total = 0
		content = u''
		for item in SideBarSelection(paths).getSelectedDirectoriesOrDirnames():
			self.files = []
			self.num_files = 0
			self.find(item.path())
			content += '\nSearching '+str(self.num_files)+' files for "'+self.searchTerm+'" in \n"'+item.path()+'"\n\n'
			content += (':\n'.join(self.files))+':\n\n'
			lenght = len(self.files)
			if lenght > 1:
				content += str(lenght)+' matches\n'
			elif lenght > 0:
				content += '1 match\n'
			else:
				content += 'No match\n'
			self.total = self.total + lenght
		if self.total > 0:
			view = sublime.active_window().new_file()
			view.settings().set('word_wrap', False)
			view.set_name('Find Results')
			view.set_syntax_file('Packages/Default/Find Results.hidden-tmLanguage')
			view.set_scratch(True)
			edit = view.begin_edit()
			view.replace(edit, sublime.Region(0, view.size()), content.lstrip());
			view.sel().clear()
			view.sel().add(sublime.Region(0))
			view.end_edit(edit)
		else:
			sublime.status_message('No files containing "'+self.searchTerm+'"')

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
		return False if path.lower().find(self.searchTerm.lower())== -1 else True

class SideBarCutCommand(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		s = sublime.load_settings("SideBarEnhancements/Clipboard.sublime-settings")
		items = []
		for item in SideBarSelection(paths).getSelectedItemsWithoutChildItems():
			items.append(item.path())
		s.set('cut', "\n".join(items))
		s.set('copy', '')
		if len(items) > 1 :
			sublime.status_message("Items cut")
		else :
			sublime.status_message("Item cut")

	def is_enabled(self, paths = []):
		return len(paths) > 0 and SideBarSelection(paths).hasProjectDirectories() == False

class SideBarCopyCommand(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		s = sublime.load_settings("SideBarEnhancements/Clipboard.sublime-settings")
		items = []
		for item in SideBarSelection(paths).getSelectedItemsWithoutChildItems():
			items.append(item.path())
		s.set('cut', '')
		s.set('copy', "\n".join(items))
		if len(items) > 1 :
			sublime.status_message("Items copied")
		else :
			sublime.status_message("Item copied")

	def is_enabled(self, paths = []):
		return len(paths) > 0

class SideBarPasteCommand(sublime_plugin.WindowCommand):
	def run(self, paths = [], in_parent = 'False'):
		s = sublime.load_settings("SideBarEnhancements/Clipboard.sublime-settings")

		cut = s.get('cut', '')
		copy = s.get('copy', '')
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
					try:
						if not path.move(new):
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
					try:
						if not path.copy(new):
							sublime.error_message("Unable to copy and paste, destination exists.")
							return
					except:
						sublime.error_message("Unable to copy:\n\n"+path.path()+"\n\nto\n\n"+new)
						return

			cut = s.set('cut', '')
			SideBarProject.refresh();

	def is_enabled(self, paths = [], in_parent = False):
		s = sublime.load_settings("SideBarEnhancements/Clipboard.sublime-settings")
		return s.get('cut', '') + s.get('copy', '') != '' and len(SideBarSelection(paths).getSelectedDirectoriesOrDirnames()) == 1

class SideBarCopyNameCommand(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		to_copy = []
		for item in SideBarSelection(paths).getSelectedItems():
			to_copy.append(item.name())

		sublime.set_clipboard("\n".join(to_copy));
		if len(to_copy) > 1 :
			sublime.status_message("Items copied")
		else :
			sublime.status_message("Item copied")

	def is_enabled(self, paths = []):
		return len(paths) > 0

class SideBarCopyNameEncodedCommand(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		to_copy = []
		for item in SideBarSelection(paths).getSelectedItems():
			to_copy.append(item.nameEncoded())

		sublime.set_clipboard("\n".join(to_copy));
		if len(to_copy) > 1 :
			sublime.status_message("Items copied")
		else :
			sublime.status_message("Item copied")

	def is_enabled(self, paths = []):
		return len(paths) > 0

class SideBarCopyPathCommand(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		to_copy = []
		for item in SideBarSelection(paths).getSelectedItems():
			to_copy.append(item.path())

		sublime.set_clipboard("\n".join(to_copy));
		if len(to_copy) > 1 :
			sublime.status_message("Items copied")
		else :
			sublime.status_message("Item copied")

	def is_enabled(self, paths = []):
		return len(paths) > 0

class SideBarCopyPathEncodedCommand(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		to_copy = []
		for item in SideBarSelection(paths).getSelectedItems():
			to_copy.append(item.uri())

		sublime.set_clipboard("\n".join(to_copy));
		if len(to_copy) > 1 :
			sublime.status_message("Items copied")
		else :
			sublime.status_message("Item copied")

	def is_enabled(self, paths = []):
		return len(paths) > 0

class SideBarCopyPathRelativeFromProjectCommand(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		to_copy = []
		for item in SideBarSelection(paths).getSelectedItems():
			to_copy.append(item.pathRelativeFromProject())

		sublime.set_clipboard("\n".join(to_copy));
		if len(to_copy) > 1 :
			sublime.status_message("Items copied")
		else :
			sublime.status_message("Item copied")

	def is_enabled(self, paths = []):
		return len(paths) > 0

class SideBarCopyPathRelativeFromProjectEncodedCommand(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		to_copy = []
		for item in SideBarSelection(paths).getSelectedItems():
			to_copy.append(item.pathRelativeFromProjectEncoded())

		sublime.set_clipboard("\n".join(to_copy));
		if len(to_copy) > 1 :
			sublime.status_message("Items copied")
		else :
			sublime.status_message("Item copied")

	def is_enabled(self, paths = []):
		return len(paths) > 0

class SideBarCopyPathRelativeFromViewCommand(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		to_copy = []
		for item in SideBarSelection(paths).getSelectedItems():
			to_copy.append(item.pathRelativeFromView())

		sublime.set_clipboard("\n".join(to_copy));
		if len(to_copy) > 1 :
			sublime.status_message("Items copied")
		else :
			sublime.status_message("Item copied")

	def is_enabled(self, paths = []):
		return len(paths) > 0

class SideBarCopyPathRelativeFromViewEncodedCommand(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		to_copy = []
		for item in SideBarSelection(paths).getSelectedItems():
			to_copy.append(item.pathRelativeFromViewEncoded())

		sublime.set_clipboard("\n".join(to_copy));
		if len(to_copy) > 1 :
			sublime.status_message("Items copied")
		else :
			sublime.status_message("Item copied")

	def is_enabled(self, paths = []):
		return len(paths) > 0

class SideBarCopyPathAbsoluteFromProjectCommand(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		to_copy = []
		for item in SideBarSelection(paths).getSelectedItems():
			to_copy.append(item.pathAbsoluteFromProject())

		sublime.set_clipboard("\n".join(to_copy));
		if len(to_copy) > 1 :
			sublime.status_message("Items copied")
		else :
			sublime.status_message("Item copied")

	def is_enabled(self, paths = []):
		return len(paths) > 0

class SideBarCopyPathAbsoluteFromProjectEncodedCommand(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		to_copy = []
		for item in SideBarSelection(paths).getSelectedItems():
			to_copy.append(item.pathAbsoluteFromProjectEncoded())

		sublime.set_clipboard("\n".join(to_copy));
		if len(to_copy) > 1 :
			sublime.status_message("Items copied")
		else :
			sublime.status_message("Item copied")

	def is_enabled(self, paths = []):
		return len(paths) > 0

class SideBarCopyTagAhrefCommand(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		to_copy = []
		for item in SideBarSelection(paths).getSelectedItems():
			to_copy.append('<a href="'+item.pathAbsoluteFromProjectEncoded()+'">'+item.namePretty()+'</a>')

		sublime.set_clipboard("\n".join(to_copy));
		if len(to_copy) > 1 :
			sublime.status_message("Items copied")
		else :
			sublime.status_message("Item copied")

	def is_enabled(self, paths = []):
		return len(paths) > 0

class SideBarCopyTagImgCommand(sublime_plugin.WindowCommand):

	def run(self, paths = []):
		to_copy = []
		for item in SideBarSelection(paths).getSelectedImages():
			try:
				image_type, width, height = self.getImageInfo(item.contentBinary())
				to_copy.append('<img src="'+item.pathAbsoluteFromProjectEncoded()+'" width="'+str(width)+'" height="'+str(height)+'" border="0"/>')
			except:
				to_copy.append('<img src="'+item.pathAbsoluteFromProjectEncoded()+'" border="0"/>')

		sublime.set_clipboard("\n".join(to_copy));
		if len(to_copy) > 1 :
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
		to_copy = []
		for item in SideBarSelection(paths).getSelectedFilesWithExtension('css'):
			to_copy.append('<link rel="stylesheet" type="text/css" href="'+item.pathAbsoluteFromProjectEncoded()+'"/>')

		sublime.set_clipboard("\n".join(to_copy));
		if len(to_copy) > 1 :
			sublime.status_message("Items copied")
		else :
			sublime.status_message("Item copied")

	def is_enabled(self, paths = []):
		return SideBarSelection(paths).hasFilesWithExtension('css')

class SideBarCopyTagScriptCommand(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		to_copy = []
		for item in SideBarSelection(paths).getSelectedFilesWithExtension('js'):
			to_copy.append('<script type="text/javascript" src="'+item.pathAbsoluteFromProjectEncoded()+'"></script>')

		sublime.set_clipboard("\n".join(to_copy));
		if len(to_copy) > 1 :
			sublime.status_message("Items copied")
		else :
			sublime.status_message("Item copied")

	def is_enabled(self, paths = []):
		return SideBarSelection(paths).hasFilesWithExtension('js')

class SideBarCopyProjectDirectoriesCommand(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		to_copy = []
		for directory in SideBarProject().getDirectories():
			to_copy.append(directory)

		sublime.set_clipboard("\n".join(to_copy));
		if len(to_copy) > 1 :
			sublime.status_message("Items copied")
		else :
			sublime.status_message("Item copied")

	def is_enabled(self, paths = []):
		return True

class SideBarCopyContentUtf8Command(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		to_copy = []
		for item in SideBarSelection(paths).getSelectedFiles():
			to_copy.append(item.contentUTF8())

		sublime.set_clipboard("\n".join(to_copy));
		if len(paths) > 1 :
			sublime.status_message("Items content copied")
		else :
			sublime.status_message("Item content copied")

	def is_enabled(self, paths = []):
		return SideBarSelection(paths).hasFiles()

class SideBarCopyContentBase64Command(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		to_copy = []
		for item in SideBarSelection(paths).getSelectedFiles():
			to_copy.append(item.contentBase64())

		sublime.set_clipboard("\n".join(to_copy));
		if len(paths) > 1 :
			sublime.status_message("Items content copied")
		else :
			sublime.status_message("Item content copied")

	def is_enabled(self, paths = []):
		return SideBarSelection(paths).hasFiles()

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
			sublime.error_message("Unable to move:\n\n"+old+"\n\nto\n\n"+new)
			self.run([old], new)
			return
		SideBarProject.refresh();

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
		SideBarProject.refresh();

	def is_enabled(self, paths = []):
		return SideBarSelection(paths).len() == 1 and SideBarSelection(paths).hasProjectDirectories() == False

class SideBarMoveCommand(sublime_plugin.WindowCommand):
	def run(self, paths = [], new = False):
		import functools
		self.window.run_command('hide_panel');
		self.window.show_input_panel("New Location:", new or paths[0], functools.partial(self.on_done, paths[0]), None, None)

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
		SideBarProject.refresh();

	def is_enabled(self, paths = []):
		return len(paths) == 1 and SideBarSelection(paths).hasProjectDirectories() == False

class SideBarDeleteCommand(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		import sys
		if sys.platform == 'darwin':
			import functools
			self.window.run_command('hide_panel');
			self.window.show_input_panel("Permanently Delete:", paths[0], functools.partial(self.on_done, paths[0]), None, None)
		else:
			try:
				sys.path.append(os.path.join(sublime.packages_path(), 'SideBarEnhancements'))
				import send2trash
				for item in SideBarSelection(paths).getSelectedItemsWithoutChildItems():
					send2trash.send2trash(item.path())
			except:
				import functools
				self.window.run_command('hide_panel');
				self.window.show_input_panel("Permanently Delete:", paths[0], functools.partial(self.on_done, paths[0]), None, None)

	def on_done(self, old, new):
		self.remove(new)
		SideBarProject.refresh();

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

	def is_enabled(self, paths = []):
		return len(paths) > 0 and SideBarSelection(paths).hasProjectDirectories() == False

class SideBarRevealCommand(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		for item in SideBarSelection(paths).getSelectedItems():
			item.reveal()

	def is_enabled(self, paths = []):
		return len(paths) > 0

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
			view = SideBarItem(project.getProjectFile(), False).edit();
			sublime.active_window().focus_view(view)
			sublime.set_timeout(lambda: sublime.active_window().run_command('save'), 250)
			sublime.set_timeout(lambda: sublime.active_window().run_command('close'), 400)

	def is_enabled(self, paths = []):
		return False #SideBarSelection(paths).hasDirectories()

class SideBarProjectItemExcludeCommand(sublime_plugin.WindowCommand):
	def run(self, paths = []):
		project = SideBarProject()
		if project.hasOpenedProject():
			file = project.getProjectFile()
			for item in SideBarSelection(paths).getSelectedItems():
				if item.isDirectory():
					project.excludeDirectory(item.path())
				else:
					project.excludeFile(item.path())
			view = SideBarItem(file, False).edit();
			sublime.active_window().focus_view(view)
			sublime.set_timeout(lambda: sublime.active_window().run_command('save'), 250)
			sublime.set_timeout(lambda: sublime.active_window().run_command('close'), 400)

	def is_enabled(self, paths = []):
		return False #len(paths) > 0