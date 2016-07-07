# coding=utf8
import sublime
import os
import re
import shutil

class Object():
	pass

def expandVars(path):
	for k, v in list(os.environ.items()):
		path = path.replace('%'+k+'%', v).replace('%'+k.lower()+'%', v)
	return path

def escapeCMDWindows(string):
	return string.replace('^', '^^')

BINARY = re.compile('\.(psd|ai|cdr|ico|cache|sublime-package|eot|svgz|ttf|woff|zip|tar|gz|rar|bz2|jar|xpi|mov|mpeg|avi|mpg|flv|wmv|mp3|wav|aif|aiff|snd|wma|asf|asx|pcm|pdf|doc|docx|xls|xlsx|ppt|pptx|rtf|sqlite|sqlitedb|fla|swf|exe)$', re.I)

class SideBarSelection:

	def __init__(self, paths = []):

		if not paths or len(paths) < 1:
			try:
				path = sublime.active_window().active_view().file_name()
				if self.isNone(path):
					paths = []
				else:
					paths = [path]
			except:
				paths = []
		self._paths = paths
		self._paths.sort()
		self._obtained_selection_information_basic = False
		self._obtained_selection_information_extended = False

	def len(self):
		return len(self._paths)

	def hasDirectories(self):
		self._obtainSelectionInformationBasic()
		return self._has_directories

	def hasFiles(self):
		self._obtainSelectionInformationBasic()
		return self._has_files

	def hasOnlyDirectories(self):
		self._obtainSelectionInformationBasic()
		return self._only_directories

	def hasOnlyFiles(self):
		self._obtainSelectionInformationBasic()
		return self._only_files

	def hasProjectDirectories(self):
		if self.hasDirectories():
			project_directories = SideBarProject().getDirectories()
			for item in self.getSelectedDirectories():
				if item.path() in project_directories:
					return True
			return False
		else:
			return False

	def hasItemsUnderProject(self):
		for item in self.getSelectedItems():
			if item.isUnderCurrentProject():
				return True
		return False

	def hasImages(self):
		return self.hasFilesWithExtension('gif|jpg|jpeg|png')

	def hasFilesWithExtension(self, extensions):
		extensions = re.compile('('+extensions+')$', re.I);
		for item in self.getSelectedFiles():
			if extensions.search(item.path()):
				return True;
		return False

	def getSelectedItems(self):
		self._obtainSelectionInformationExtended()
		return self._files + self._directories;

	def getSelectedItemsWithoutChildItems(self):
		self._obtainSelectionInformationExtended()
		items = []
		for item in self._items_without_containing_child_items:
			items.append(SideBarItem(item, os.path.isdir(item)))
		return items

	def getSelectedDirectories(self):
		self._obtainSelectionInformationExtended()
		return self._directories;

	def getSelectedFiles(self):
		self._obtainSelectionInformationExtended()
		return self._files;

	def getSelectedDirectoriesOrDirnames(self):
		self._obtainSelectionInformationExtended()
		return self._directories_or_dirnames;

	def getSelectedImages(self):
		return self.getSelectedFilesWithExtension('gif|jpg|jpeg|png')

	def getSelectedFilesWithExtension(self, extensions):
		items = []
		extensions = re.compile('('+extensions+')$', re.I);
		for item in self.getSelectedFiles():
			if extensions.search(item.path()):
				items.append(item)
		return items

	def _obtainSelectionInformationBasic(self):
		if not self._obtained_selection_information_basic:
			self._obtained_selection_information_basic = True

			self._has_directories = False
			self._has_files = False
			self._only_directories = False
			self._only_files = False

			for path in self._paths:
				if self._has_directories == False and os.path.isdir(path):
					self._has_directories = True
				if self._has_files == False and os.path.isdir(path) == False:
					self._has_files = True
				if self._has_files and self._has_directories:
					break

			if self._has_files and self._has_directories:
				self._only_directories = False
				self._only_files 	= False
			elif self._has_files:
				self._only_files 	= True
			elif self._has_directories:
				self._only_directories = True

	def _obtainSelectionInformationExtended(self):
		if not self._obtained_selection_information_extended:
			self._obtained_selection_information_extended = True

			self._directories = []
			self._files = []
			self._directories_or_dirnames = []
			self._items_without_containing_child_items = []

			_directories = []
			_files = []
			_directories_or_dirnames = []
			_items_without_containing_child_items = []

			for path in self._paths:
				if os.path.isdir(path):
					item = SideBarItem(path, True)
					if item.path() not in _directories:
						_directories.append(item.path())
						self._directories.append(item)
					if item.path() not in _directories_or_dirnames:
						_directories_or_dirnames.append(item.path())
						self._directories_or_dirnames.append(item)
					_items_without_containing_child_items = self._itemsWithoutContainingChildItems(_items_without_containing_child_items, item.path())
				else:
					item = SideBarItem(path, False)
					if item.path() not in _files:
						_files.append(item.path())
						self._files.append(item)
					_items_without_containing_child_items = self._itemsWithoutContainingChildItems(_items_without_containing_child_items, item.path())
					item = SideBarItem(os.path.dirname(path), True)
					if item.path() not in _directories_or_dirnames:
						_directories_or_dirnames.append(item.path())
						self._directories_or_dirnames.append(item)

			self._items_without_containing_child_items = _items_without_containing_child_items

	def _itemsWithoutContainingChildItems(self, items, item):
		new_list = []
		add = True
		for i in items:
			if i.find(item+'\\') == 0 or i.find(item+'/') == 0:
				continue
			else:
				new_list.append(i)
			if (item+'\\').find(i+'\\') == 0 or (item+'/').find(i+'/') == 0:
				add = False
		if add:
			new_list.append(item)
		return new_list

	def isNone(self, path):
		if path == None or path == '' or path == '.' or path == '..' or path == './' or path == '../' or path == '/' or path == '//' or path == '\\' or path == '\\\\' or path == '\\\\\\\\' or path == '\\\\?\\' or path == '\\\\?' or path == '\\\\\\\\?\\\\':
			return True
		else:
			return False

class SideBarProject:

	def getDirectories(self):
		return sublime.active_window().folders()

	def hasDirectories(self):
		return len(self.getDirectories()) > 0

	def hasOpenedProject(self):
		return self.getProjectFile() != None

	def getDirectoryFromPath(self, path):
		for directory in self.getDirectories():
			maybe_path = path.replace(directory, '', 1)
			if maybe_path != path:
				return directory

	def getProjectFile(self):
		return sublime.active_window().project_file_name()

	def getProjectJson(self):
		return sublime.active_window().project_data()

	def setProjectJson(self, data):
		return sublime.active_window().set_project_data(data)

	def excludeDirectory(self, path, exclude):
		data = self.getProjectJson()
		for folder in data['folders']:
			project_folder = folder['path']
			if project_folder == '.':
				project_folder = SideBarItem(self.getProjectFile(), False).dirname();
			if path.find(project_folder) == 0:
				try:
					folder['folder_exclude_patterns'].append(exclude)
				except:
					folder['folder_exclude_patterns'] = [exclude]
		self.setProjectJson(data);

	def excludeFile(self, path, exclude):
		data = self.getProjectJson()
		for folder in data['folders']:
			project_folder = folder['path']
			if project_folder == '.':
				project_folder = SideBarItem(self.getProjectFile(), False).dirname();
			if path.find(project_folder) == 0:
				try:
					folder['file_exclude_patterns'].append(exclude)
				except:
					folder['file_exclude_patterns'] = [exclude]
		self.setProjectJson(data);

	def add(self, path):
		data = self.getProjectJson()
		if data:
			data['folders'].append({'follow_symlinks':True, 'path':path});
		else:
			data = {'folders': [{'follow_symlinks': True, 'path':path}]}
		self.setProjectJson(data);

	def refresh(self):
		sublime.active_window().run_command('refresh_folder_list')

class SideBarItem:

	def __init__(self, path, is_directory):
		self._path = path
		self._is_directory = is_directory

	def path(self, path = ''):
		if path == '':
			return self._path
		else:
			self._path = path
			self._is_directory = os.path.isdir(path)
			return path

	def pathWithoutProject(self):
		path = self.path()
		for directory in SideBarProject().getDirectories():
			path = path.replace(directory, '', 1)
		return path.replace('\\', '/')

	def pathProject(self):
		path = self.path()
		for directory in SideBarProject().getDirectories():
			path2 = path.replace(directory, '', 1)
			if path2 != path:
				return directory
		return False

	def url(self, type):

		filenames = []

		# scans a la htaccess
		item = SideBarItem(self.path(), self.isDirectory())
		while not os.path.exists(item.join('.sublime/SideBarEnhancements.json')):
			if item.dirname() == item.path():
				break;
			item.path(item.dirname())
		item  = SideBarItem(item.join('.sublime/SideBarEnhancements.json'), False);
		if item.exists():
			filenames.append(item.path())

		filenames.append(os.path.dirname(sublime.packages_path())+'/Settings/SideBarEnhancements.json')

		import collections
		for filename in filenames:
			if os.path.lexists(filename):
				import json
				data = open(filename, 'r').read()
				data = data.replace('\t', ' ').replace('\\', '/').replace('\\', '/').replace('//', '/').replace('//', '/').replace('http:/', 'http://').replace('https:/', 'https://')
				data = json.loads(data, strict=False, object_pairs_hook=collections.OrderedDict)
				for key in list(data.keys()):
					#	print('-------------------------------------------------------')
					#	print(key);
					if filename == filenames[len(filenames)-1]:
						base = expandVars(key)
					else:
						base = os.path.normpath(expandVars(os.path.dirname(os.path.dirname(filename))+'/'+key))
					base = base.replace('\\', '/').replace('\\', '/').replace('//', '/').replace('//', '/')
					#	print(base)
					current = self.path().replace('\\', '/').replace('\\', '/').replace('//', '/').replace('//', '/')
					#	print(current)
					url_path = re.sub(re.compile("^"+re.escape(base), re.IGNORECASE), '', current);
					#	print(url_path)
					if url_path != current:
						url = data[key][type]
						if url:
							if url[-1:] != '/':
								url = url+'/'
						import urllib.request, urllib.parse, urllib.error
						return url+(re.sub("^/", '', urllib.parse.quote(url_path)));
		return False

	def isUnderCurrentProject(self):
		path = self.path()
		path2 = self.path()
		for directory in SideBarProject().getDirectories():
			path2 = path2.replace(directory, '', 1)
		return path != path2

	def pathRelativeFromProject(self):
		return re.sub('^/+', '', self.pathWithoutProject())

	def pathRelativeFromProjectEncoded(self):
		import urllib.request, urllib.parse, urllib.error
		return urllib.parse.quote(self.pathRelativeFromProject())

	def pathRelativeFromView(self):
		return os.path.relpath(self.path(), os.path.dirname(sublime.active_window().active_view().file_name())).replace('\\', '/')

	def pathRelativeFromViewEncoded(self):
		import urllib.request, urllib.parse, urllib.error
		return urllib.parse.quote(os.path.relpath(self.path(), os.path.dirname(sublime.active_window().active_view().file_name())).replace('\\', '/'))

	def pathAbsoluteFromProject(self):
		return self.pathWithoutProject()

	def pathAbsoluteFromProjectEncoded(self):
		import urllib.request, urllib.parse, urllib.error
		return urllib.parse.quote(self.pathAbsoluteFromProject())

	def uri(self):
		uri = 'file:'+(self.path().replace('\\', '/').replace('//', '/'));
		return uri

	def join(self, name):
		return os.path.join(self.path(), name)

	def dirname(self):
		branch, leaf = os.path.split(self.path())
		return branch;

	def forCwdSystemPath(self):
		if self.isDirectory():
			return self.path()
		else:
			return self.dirname()

	def forCwdSystemName(self):
		if self.isDirectory():
			return '.'
		else:
			path = self.path()
			branch = self.dirname()
			leaf = path.replace(branch, '', 1).replace('\\', '').replace('/', '')
			return leaf

	def forCwdSystemPathRelativeFrom(self, relativeFrom):
		relative = SideBarItem(relativeFrom, os.path.isdir(relativeFrom))
		path = self.path().replace(relative.path(), '', 1).replace('\\', '/')
		if path == '':
			return '.'
		else:
			return re.sub('^/+', '', path)

	def forCwdSystemPathRelativeFromRecursive(self, relativeFrom):
		relative = SideBarItem(relativeFrom, os.path.isdir(relativeFrom))
		path = self.path().replace(relative.path(), '', 1).replace('\\', '/')
		if path == '':
			return '.'
		else:
			if self.isDirectory():
				return re.sub('^/+', '', path)+'/'
			else:
				return re.sub('^/+', '', path)

	def dirnameCreate(self):
		try:
			self._makedirs(self.dirname())
		except:
			pass

	def name(self):
		branch, leaf = os.path.split(self.path())
		return leaf;

	def nameEncoded(self):
		import urllib.request, urllib.parse, urllib.error
		return urllib.parse.quote(self.name());

	def namePretty(self):
		return self.name().replace(self.extension(), '').replace('-', ' ').replace('_', ' ').strip();

	def open(self, use_powershell = True):
		if self.isDirectory():
			import subprocess
			if sublime.platform() == 'osx':
				subprocess.Popen(['/Applications/Utilities/Terminal.app/Contents/MacOS/Terminal', '.'], cwd=self.forCwdSystemPath())
			elif sublime.platform() == 'windows':
				if use_powershell:
					try:
						subprocess.Popen(['start', 'powershell'], cwd=self.forCwdSystemPath(), shell=True)
					except:
						subprocess.Popen(['start', 'cmd', '.'], cwd=self.forCwdSystemPath(), shell=True)
				else:
					subprocess.Popen(['start', 'cmd', '.'], cwd=self.forCwdSystemPath(), shell=True)
			elif sublime.platform() == 'linux':
				subprocess.Popen(['gnome-terminal', '.'], cwd=self.forCwdSystemPath())
		else:
			if sublime.platform() == 'osx':
				import subprocess
				subprocess.Popen(['open', self.name()], cwd=self.dirname())
			elif sublime.platform() == 'windows':
				import subprocess
				subprocess.Popen(['start',  '', escapeCMDWindows(self.path())], cwd=self.dirname(), shell=True)
			else:
				from . import desktop
				desktop.open(self.path())
				print('using desktop')

	def edit(self):
		if BINARY.search(self.path()):
			return None
		else:
			view = sublime.active_window().open_file(self.path())
			view.settings().set('open_with_edit', True);
			return view

	def isDirectory(self):
		return self._is_directory

	def isFile(self):
		return self.isDirectory() == False

	def contentUTF8(self):
		return open(self.path(), 'r', newline='', encoding='utf-8').read()

	def contentBinary(self):
		return open(self.path(), "rb").read()

	def contentBase64(self):
		import base64
		base64text = base64.b64encode(self.contentBinary()).decode('utf-8')
		return 'data:'+self.mime()+';charset=utf-8;base64,'+(base64text.replace('\n', ''))

	def reveal(self):
		if sublime.platform() == 'windows':
			import subprocess
			if self.isDirectory():
				subprocess.Popen(["explorer", escapeCMDWindows(self.path())])
			else:
				subprocess.Popen(["explorer", '/select,', escapeCMDWindows(self.path())])
		else:
			sublime.active_window().run_command("open_dir", {"dir": self.dirname(), "file": self.name()} )

	def write(self, content):
		with open(self.path(), 'w+', encoding='utf8', newline='') as f:
			f.write(str(content))

		if 3000 <= int(sublime.version()) < 3088:
			# Fixes as best as possible a new file permissions issue
			# See https://github.com/titoBouzout/SideBarEnhancements/issues/203
			# See https://github.com/SublimeTextIssues/Core/issues/239
			oldmask = os.umask(0o000)
			if oldmask == 0:
				os.chmod(self.path(), 0o644)
			os.umask(oldmask)

	def mime(self):
		import mimetypes
		return mimetypes.guess_type(self.path())[0] or 'application/octet-stream'

	def extension(self):
		try:
			return re.compile('(\.[^\.]+(\.[^\.]{2,4})?)$').findall('name'+self.name())[0][0].lower()
		except:
			return os.path.splitext('name'+self.name())[1].lower()

	def exists(self):
		return os.path.isdir(self.path()) or os.path.isfile(self.path())

	def overwrite(self):
		overwrite = sublime.ok_cancel_dialog("Destination exists", "Delete, and overwrite")
		if overwrite:
			from SideBarEnhancements.send2trash import send2trash
			send2trash(self.path())
			return True
		else:
			return False

	def create(self):
		if self.isDirectory():
			self.dirnameCreate()
			self._makedirs(self.path())
		else:
			self.dirnameCreate()
			self.write('')

	def _makedirs(self, path):
		if 3000 <= int(sublime.version()) < 3088:
			# Fixes as best as possible a new directory permissions issue
			# See https://github.com/titoBouzout/SideBarEnhancements/issues/203
			# See https://github.com/SublimeTextIssues/Core/issues/239
			oldmask = os.umask(0o000)
			if oldmask == 0:
				os.makedirs(path, 0o755);
			else:
				os.makedirs(path);
			os.umask(oldmask)
		else:
			os.makedirs(path)

	def copy(self, location, replace = False):
		location = SideBarItem(location, os.path.isdir(location));
		if location.exists() and replace == False:
			return False
		elif location.exists() and location.isFile():
			os.remove(location.path())

		location.dirnameCreate();
		if self.isDirectory():
			if location.exists():
				self.copyRecursive(self.path(), location.path())
			else:
				shutil.copytree(self.path(), location.path())
		else:
			shutil.copy2(self.path(), location.path())
		return True

	def copyRecursive(self, _from, _to):

		if os.path.isfile(_from) or os.path.islink(_from):
			try:
				self._makedirs(os.path.dirname(_to));
			except:
				pass
			if os.path.exists(_to):
				os.remove(_to)
			shutil.copy2(_from, _to)
		else:
			try:
				self._makedirs(_to);
			except:
				pass
			for content in os.listdir(_from):
				__from = os.path.join(_from, content)
				__to = os.path.join(_to, content)
				self.copyRecursive(__from, __to)

	def move(self, location, replace = False):
		location = SideBarItem(location, os.path.isdir(location));
		if location.exists() and replace == False:
			if self.path().lower() == location.path().lower():
				pass
			else:
				return False
		elif location.exists() and location.isFile():
			os.remove(location.path())

		if self.path().lower() == location.path().lower():
			location.dirnameCreate();
			os.rename(self.path(), location.path()+'.sublime-temp')
			os.rename(location.path()+'.sublime-temp', location.path())
			self._moveMoveViews(self.path(), location.path())
		else:
			location.dirnameCreate();
			if location.exists():
				self.moveRecursive(self.path(), location.path())
			else:
				os.rename(self.path(), location.path())
			self._moveMoveViews(self.path(), location.path())
		return True

	def moveRecursive(self, _from, _to):
		if os.path.isfile(_from) or os.path.islink(_from):
			try:
				self._makedirs(os.path.dirname(_to));
			except:
				pass
			if os.path.exists(_to):
				os.remove(_to)
			os.rename(_from, _to)
		else:
			try:
				self._makedirs(_to);
			except:
				pass
			for content in os.listdir(_from):
				__from = os.path.join(_from, content)
				__to = os.path.join(_to, content)
				self.moveRecursive(__from, __to)
			os.rmdir(_from)

	def _moveMoveViews(self, old, location):
		for window in sublime.windows():
			active_view = window.active_view()
			views = []
			for view in window.views():
				if view.file_name():
					views.append(view)
			views.reverse();
			for view in views:
				if old == view.file_name():
					active_view = self._moveMoveView(window, view, location, active_view)
				elif view.file_name().find(old+'\\') == 0:
					active_view = self._moveMoveView(window, view, view.file_name().replace(old+'\\', location+'\\', 1), active_view)
				elif view.file_name().find(old+'/') == 0:
					active_view = self._moveMoveView(window, view, view.file_name().replace(old+'/', location+'/', 1), active_view)

	def _moveMoveView(self, window, view, location, active_view):
		view.retarget(location)

	def closeViews(self):
		path = self.path()
		closed_items = []
		for window in sublime.windows():
			active_view = window.active_view()
			views = []
			for view in window.views():
				if view.file_name():
					views.append(view)
			views.reverse();
			for view in views:
				if path == view.file_name() or view.file_name().find(path+'\\') == 0 or view.file_name().find(path+'/') == 0:
					if view.window():
						closed_items.append([view.file_name(), view.window(), view.window().get_view_index(view)])
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
		return closed_items
