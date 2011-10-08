import sublime, sublime_plugin
import os
import functools
import shutil

class SideBarFilesNewFileCommand(sublime_plugin.WindowCommand):
	def run(self, paths):
		for path in paths:
			view = self.window.new_file()
			if os.path.isdir(path):
				view.settings().set('default_dir', path)
			else:
				view.settings().set('default_dir', os.path.dirname(path))
			view.run_command('save')

	def is_enabled(self, paths):
		return len(paths) > 0

class SideBarFilesNewFolderCommand(sublime_plugin.WindowCommand):
	def run(self, paths):
		self.window.run_command('hide_panel');
		self.window.show_input_panel("Folder Name:", "", functools.partial(self.on_done, paths), None, None)

	def on_done(self, paths, name):
		for path in paths:
			if os.path.isdir(path):
				try:
					os.makedirs(os.path.join(path, name))
				except:
					sublime.error_message("Unable to create directory:\n\n"+os.path.join(path, name))
			else:
				try:
					os.makedirs(os.path.join(os.path.dirname(path), name))
				except:
					sublime.error_message("Unable to create directory:\n\n"+os.path.join(os.path.dirname(path), name))

	def is_enabled(self, paths):
		return len(paths) > 0

class SideBarFilesFindInSelectedCommand(sublime_plugin.WindowCommand):
	def run(self, paths):
		self.window.run_command('hide_panel');
		self.window.run_command("show_panel", {"panel": "find_in_files",
				"location": ",".join(paths)})

	def is_enabled(self, paths):
		return len(paths) > 0
			
class SideBarFilesFindInParentCommand(sublime_plugin.WindowCommand):
	def run(self, paths):
		paths[0] = os.path.dirname(paths[0])
		self.window.run_command('hide_panel');
		self.window.run_command("show_panel", {"panel": "find_in_files",
				"location": ",".join(paths)})

	def is_enabled(self, paths):
		return len(paths) > 0

class SideBarFilesFindInProjectCommand(sublime_plugin.WindowCommand):
	def run(self):
		self.window.run_command('hide_panel');
		self.window.run_command('show_panel', {"panel": "find_in_files", "location": "<open folders>" });


class SideBarFilesCutCommand(sublime_plugin.WindowCommand):
	def run(self, paths):
		s = sublime.load_settings("SideBar Files.sublime-settings")
		s.set('cut', paths)
		s.set('copy', [])
		if len(paths) > 1 :
			sublime.status_message("Cutted paths")
		else :
			sublime.status_message("Cutted path")

	def is_enabled(self, paths):
		return len(paths) > 0

class SideBarFilesCopyCommand(sublime_plugin.WindowCommand):
	def run(self, paths):
		s = sublime.load_settings("SideBar Files.sublime-settings")
		s.set('cut', [])
		s.set('copy', paths)
		if len(paths) > 1 :
			sublime.status_message("Copied paths")
		else :
			sublime.status_message("Copied path")

	def is_enabled(self, paths):
		return len(paths) > 0

class SideBarFilesPasteCommand(sublime_plugin.WindowCommand):
	def run(self, paths):
		s = sublime.load_settings("SideBar Files.sublime-settings")
		
		cut = s.get('cut', [])
		copy = s.get('copy', [])

		dst = paths[0]
		if os.path.isdir(dst) == False:
			dst = os.path.dirname(dst)

		for path in cut:
			branch, leaf = os.path.split(path)
			new = os.path.join(dst, leaf)
			if os.path.isdir(new) or os.path.isfile(new):
				sublime.error_message("Unable to cut and paste, destination exists.")
			else:
				try:
					try:
						os.makedirs(os.path.dirname(new))
						os.rename(path, new)
					except:
						os.rename(path, new)
				except:
					sublime.error_message("Unable to move:\n\n"+path+"\n\nto\n\n"+new)

		for path in copy:
			branch, leaf = os.path.split(path)
			new = os.path.join(dst, leaf)
			if os.path.isdir(new) or os.path.isfile(new):
				sublime.error_message("Unable to copy and paste, destination exists.")
			else:
				if os.path.isdir(path):
					try:
						shutil.copytree(path, new);
					except:
						sublime.error_message("Unable to copy:\n\n"+path+"\n\nto\n\n"+new)
				else:
					try:
						shutil.copy(path, new);
					except:
						sublime.error_message("Unable to copy:\n\n"+path+"\n\nto\n\n"+new)

		cut = s.set('cut', [])

	def is_enabled(self, paths):
		s = sublime.load_settings("SideBar Files.sublime-settings")
		return (len(s.get('cut', [])) + len(s.get('copy', []))) > 0

class SideBarFilesPathsCopyCommand(sublime_plugin.WindowCommand):
	def run(self, paths):
		sublime.set_clipboard("\n".join(paths));
		if len(paths) > 1 :
			sublime.status_message("Copied paths")
		else :
			sublime.status_message("Copied path")

	def is_enabled(self, paths):
		return len(paths) > 0

class SideBarFilesDuplicateCommand(sublime_plugin.WindowCommand):
	def run(self, paths):
		self.window.run_command('hide_panel');
		self.window.show_input_panel("Duplicate As:", paths[0], functools.partial(self.on_done, paths[0]), None, None)

	def on_done(self, src, dst):
		if os.path.isdir(dst) or os.path.isfile(dst):
			sublime.error_message("Unable to duplicate, destination exists.")
		else :
			if os.path.isdir(src):
				try:
					shutil.copytree(src, dst);
				except:
					sublime.error_message("Unable to duplicate directory:\n\n"+src+"\n\nto\n\n"+dst)
			else:
				try:
					shutil.copy(src, dst);
				except:
					sublime.error_message("Unable to duplicate file:\n\n"+src+"\n\nto\n\n"+dst)

	def is_enabled(self, paths):
		return len(paths) == 1

class SideBarFilesRenameCommand(sublime_plugin.WindowCommand):
	def run(self, paths):
		branch, leaf = os.path.split(paths[0])
		self.window.run_command('hide_panel');
		self.window.show_input_panel("New Name:", leaf, functools.partial(self.on_done, paths[0], branch), None, None)

	def on_done(self, old, branch, leaf):
		new = os.path.join(branch, leaf)
		try:
			if os.path.isdir(new) or os.path.isfile(new):
				sublime.error_message("Unable to rename, destination exists.")
			else:
				os.rename(old, new)
		except:
			sublime.error_message("Unable to rename:\n\n"+old+"\n\nto\n\n"+new)

	def is_enabled(self, paths):
		return len(paths) == 1
	
class SideBarFilesMoveCommand(sublime_plugin.WindowCommand):
	def run(self, paths):
		self.window.run_command('hide_panel');
		self.window.show_input_panel("New Location:", paths[0], functools.partial(self.on_done, paths[0]), None, None)

	def on_done(self, old, new):
		if os.path.isdir(new) or os.path.isfile(new):
			sublime.error_message("Unable to move, destination exists.")
		else:
			try:
				try:
					os.makedirs(os.path.dirname(new))
					os.rename(old, new)
				except:
					os.rename(old, new)
			except:
				sublime.error_message("Unable to move:\n\n"+old+"\n\nto\n\n"+new)

	def is_enabled(self, paths):
		return len(paths) == 1

class SideBarFilesDeleteCommand(sublime_plugin.WindowCommand):
	def run(self, paths):
		self.window.run_command('hide_panel');
		self.window.show_input_panel("Delete:", paths[0], functools.partial(self.on_done, paths[0]), None, None)

	def on_done(self, old, new):
		self.remove(new)
		
	def remove(self, path):
		if os.path.isdir(path):
			for content in os.listdir(path):
				file = os.path.join(path, content)
				if os.path.isfile(file) or os.path.islink(file):
					self.remove_safe_file(file)
				else:
					self.remove(file)
			self.remove_safe_dir(path)
		else:
			self.remove_safe_file(path)
	
	def remove_safe_file(self, path):
		if path != '' and path != '/' and path != '//' and path != '\\' and path != '\\\\':
			try:
				os.remove(path)
			except:
				sublime.error_message("Unable to remove file:\n\n"+path)

	def remove_safe_dir(self, path):
		if path != '' and path != '/' and path != '//' and path != '\\' and path != '\\\\':
			try:
				os.rmdir(path)
			except:
				sublime.error_message("Unable to remove directory:\n\n"+path)

	def is_enabled(self, paths):
		return len(paths) == 1


class SideBarFilesRevealCommand(sublime_plugin.WindowCommand):
	def run(self, paths):
		for path in paths:
			branch, leaf = os.path.split(path)
			self.window.run_command("open_dir", {"dir": branch, "file": leaf} )

	def is_enabled(self, paths):
		return len(paths) > 0