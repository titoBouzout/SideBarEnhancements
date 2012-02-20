# coding=utf8
import sublime
import os
import re
import shutil

from SideBarProject import SideBarProject
from Utils import Object

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

	def pathSystem(self):
		import sys
		return self.path().encode(sys.getfilesystemencoding())

	def pathWithoutProject(self):
		path = self.path()
		for directory in SideBarProject().getDirectories():
			path = path.replace(directory, '', 1)
		return path.replace('\\', '/')

	def pathRelativeFromProject(self):
		return re.sub('^/+', '', self.pathWithoutProject())

	def pathRelativeFromProjectEncoded(self):
		import urllib
		return urllib.quote(self.pathRelativeFromProject().encode('utf-8'))

	def pathRelativeFromView(self):
		return os.path.relpath(self.path(), os.path.dirname(sublime.active_window().active_view().file_name())).replace('\\', '/')

	def pathRelativeFromViewEncoded(self):
		import urllib
		return urllib.quote(os.path.relpath(self.path(), os.path.dirname(sublime.active_window().active_view().file_name())).replace('\\', '/').encode('utf-8'))

	def pathAbsoluteFromProject(self):
		return self.pathWithoutProject()

	def pathAbsoluteFromProjectEncoded(self):
		import urllib
		return urllib.quote(self.pathAbsoluteFromProject().encode('utf-8'))

	def uri(self):
		import urllib
		return 'file:'+urllib.pathname2url(self.path().encode('utf-8'));

	def join(self, name):
		return os.path.join(self.path(), name)

	def dirname(self):
		branch, leaf = os.path.split(self.path())
		return branch;

	def forCwdSystemPath(self):
		if self.isDirectory():
			return self.pathSystem()
		else:
			return self.dirnameSystem()

	def forCwdSystemName(self):
		if self.isDirectory():
			return './'
		else:
			path = self.pathSystem()
			branch = self.dirnameSystem()
			leaf = path.replace(branch, '', 1).replace('\\', '').replace('/', '')
			return leaf

	def forCwdSystemPathRelativeFrom(self, relativeFrom):
		relative = SideBarItem(relativeFrom, os.path.isdir(relativeFrom))
		path = self.pathSystem().replace(relative.pathSystem(), '', 1).replace('\\', '/')
		if path == '':
			return './'
		else:
			return './'+re.sub('^/+', '', path)

	def forCwdSystemPathRelativeFromRecursive(self, relativeFrom):
		relative = SideBarItem(relativeFrom, os.path.isdir(relativeFrom))
		path = self.pathSystem().replace(relative.pathSystem(), '', 1).replace('\\', '/')
		if path == '':
			return './'
		else:
			if self.isDirectory():
				return './'+re.sub('^/+', '', path)+'/'
			else:
				return './'+re.sub('^/+', '', path)

	def dirnameSystem(self):
		import sys
		return self.dirname().encode(sys.getfilesystemencoding())

	def dirnameCreate(self):
		try:
			os.makedirs(self.dirname())
		except:
			pass

	def name(self):
		branch, leaf = os.path.split(self.path())
		return leaf;

	def nameSystem(self):
		import sys
		return self.name().encode(sys.getfilesystemencoding())

	def nameEncoded(self):
		import urllib
		return urllib.quote(self.name().encode('utf-8'));

	def namePretty(self):
		return self.name().replace(self.extension(), '').replace('-', ' ').replace('_', ' ').strip();

	def open(self):
		import sys
		if sys.platform == 'darwin':
			import subprocess
			subprocess.Popen(['open', '-a', self.nameSystem()], cwd=self.dirnameSystem())
		elif sys.platform == 'win32':
			import subprocess
			subprocess.Popen([self.nameSystem()], cwd=self.dirnameSystem(), shell=True)
		else:
			path = os.path.join(sublime.packages_path(), 'SideBarEnhancements')
			if path not in sys.path:
				sys.path.append(path)
			import desktop
			desktop.open(self.path())

	def edit(self):
		return sublime.active_window().open_file(self.path())

	def isDirectory(self):
		return self._is_directory

	def isFile(self):
		return self.isDirectory() == False

	def contentUTF8(self):
		import codecs
		return codecs.open(self.path(), 'r', 'utf-8').read()

	def contentBinary(self):
		return file(self.path(), "rb").read()

	def contentBase64(self):
		return 'data:'+self.mime()+';base64,'+(file(self.path(), "rb").read().encode("base64").replace('\n', ''))

	def reveal(self):
		sublime.active_window().run_command("open_dir", {"dir": self.dirname(), "file": self.name()} )

	def write(self, content):
		file(self.path(), 'w+').write(content)

	def mime(self):
		import mimetypes
		return mimetypes.guess_type(self.path())[0] or 'application/octet-stream'

	def extension(self):
		return os.path.splitext('name'+self.name())[1].lower()

	def exists(self):
		return os.path.isdir(self.path()) or os.path.isfile(self.path())

	def create(self):
		if self.isDirectory():
			self.dirnameCreate()
			os.makedirs(self.path())
		else:
			self.dirnameCreate()
			self.write('')

	def copy(self, location, replace = False):
		location = SideBarItem(location, os.path.isdir(location));
		if location.exists() and replace == False:
			return False
		elif location.exists() and location.isFile():
			os.remove(location.path())

		location.dirnameCreate();
		if self.isDirectory():
			if location.exists():
				self.copy_recursive(self.path(), location.path())
			else:
				shutil.copytree(self.path(), location.path())
		else:
			shutil.copy2(self.path(), location.path())
		return True

	def copy_recursive(self, _from, _to):

		if os.path.isfile(_from) or os.path.islink(_from):
			try:
				os.makedirs(os.path.dirname(_to));
			except:
				pass
			if os.path.exists(_to):
				os.remove(_to)
			shutil.copy2(_from, _to)
		else:
			try:
				os.makedirs(_to);
			except:
				pass
			for content in os.listdir(_from):
				__from = os.path.join(_from, content)
				__to = os.path.join(_to, content)
				self.copy_recursive(__from, __to)

	def move(self, location, replace = False):
		location = SideBarItem(location, os.path.isdir(location));
		if location.exists() and replace == False:
			return False
		elif location.exists() and location.isFile():
			os.remove(location.path())

		if self.path().lower() == location.path().lower():
			location.dirnameCreate();
			os.rename(self.path(), location.path()+'.sublime-temp')
			os.rename(location.path()+'.sublime-temp', location.path())
			self._move_moveViews(self.path(), location.path())
		else:
			location.dirnameCreate();
			if location.exists():
				self.move_recursive(self.path(), location.path())
			else:
				os.rename(self.path(), location.path())
			self._move_moveViews(self.path(), location.path())
		return True

	def move_recursive(self, _from, _to):
		if os.path.isfile(_from) or os.path.islink(_from):
			try:
				os.makedirs(os.path.dirname(_to));
			except:
				pass
			if os.path.exists(_to):
				os.remove(_to)
			os.rename(_from, _to)
		else:
			try:
				os.makedirs(_to);
			except:
				pass
			for content in os.listdir(_from):
				__from = os.path.join(_from, content)
				__to = os.path.join(_to, content)
				self.move_recursive(__from, __to)
			os.rmdir(_from)

	def _move_moveViews(self, old, location):
		for window in sublime.windows():
			active_view = window.active_view()
			views = []
			for view in window.views():
				if view.file_name():
					views.append(view)
			views.reverse();
			for view in views:
				if old == view.file_name():
					active_view = self._move_moveView(window, view, location, active_view)
				elif view.file_name().find(old+'\\') == 0:
					active_view = self._move_moveView(window, view, view.file_name().replace(old+'\\', location+'\\', 1), active_view)
				elif view.file_name().find(old+'/') == 0:
					active_view = self._move_moveView(window, view, view.file_name().replace(old+'/', location+'/', 1), active_view)

	def _move_moveView(self, window, view, location, active_view):
		if active_view == view:
			is_active_view = True
		else:
			is_active_view = False

		options = Object()

		options.scroll = view.viewport_position()

		options.selections = []
		for sel in view.sel():
			line_s, col_s = view.rowcol(sel.a); line_e, col_e = view.rowcol(sel.b)
			options.selections.append([view.text_point(line_s, col_s), view.text_point(line_e, col_e)])

		options.marks = []
		for sel in view.get_regions("mark"):
			line_s, col_s = view.rowcol(sel.a); line_e, col_e = view.rowcol(sel.b)
			options.marks.append([view.text_point(line_s, col_s), view.text_point(line_e, col_e)])

		options.bookmarks = []
		for sel in view.get_regions("bookmarks"):
			line_s, col_s = view.rowcol(sel.a); line_e, col_e = view.rowcol(sel.b)
			options.bookmarks.append([view.text_point(line_s, col_s), view.text_point(line_e, col_e)])

		options.folds = []
		if int(sublime.version()) >= 2167:
			for sel in view.folded_regions():
				line_s, col_s = view.rowcol(sel.a); line_e, col_e = view.rowcol(sel.b)
				options.folds.append([view.text_point(line_s, col_s), view.text_point(line_e, col_e)])
		else:
			for sel in view.unfold(sublime.Region(0, view.size())):
				line_s, col_s = view.rowcol(sel.a); line_e, col_e = view.rowcol(sel.b)
				options.folds.append([view.text_point(line_s, col_s), view.text_point(line_e, col_e)])

		window.focus_view(view)
		if view.is_dirty():
			options.content = view.substr(sublime.Region(0, view.size()))
			view.window().run_command('revert')
		else:
			options.content = False
		window.run_command('close')

		view = window.open_file(location)
		sublime.set_timeout(lambda: self._move_restoreView(view, options), 200)

		if is_active_view:
			window.focus_view(view)
			return view
		else:
			window.focus_view(active_view)
			return active_view

	def _move_restoreView(self, view, options):
		if view.is_loading():
			sublime.set_timeout(lambda: self._move_restoreView(view, options), 100)
		else:
			if options.content != False:
				edit = view.begin_edit()
				view.replace(edit, sublime.Region(0, view.size()), options.content);
				view.sel().clear()
				view.sel().add(sublime.Region(0))
				view.end_edit(edit)

			for r in options.folds:
				view.fold(sublime.Region(r[0], r[1]))

			view.sel().clear()
			for r in options.selections:
				view.sel().add(sublime.Region(r[0], r[1]))

			rs = []
			for r in options.marks:
				rs.append(sublime.Region(r[0], r[1]))
			if len(rs):
				view.add_regions("mark", rs, "mark", "dot", sublime.HIDDEN | sublime.PERSISTENT)

			rs = []
			for r in options.bookmarks:
				rs.append(sublime.Region(r[0], r[1]))
			if len(rs):
				view.add_regions("bookmarks", rs, "bookmarks", "bookmark", sublime.HIDDEN | sublime.PERSISTENT)

			view.set_viewport_position(options.scroll, False)