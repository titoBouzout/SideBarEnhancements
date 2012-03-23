# coding=utf8
import sublime
import os
import re

from SideBarProject import SideBarProject
from SideBarItem import SideBarItem

class SideBarSelection:

	def __init__(self, paths = []):

		if len(paths) < 1:
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
		if path == None or path == '' or path == '.' or path == '..' or path == './' or path == '/' or path == '//' or path == '\\' or path == '\\\\' or path == '\\\\\\\\':
			return True
		else:
			return False
