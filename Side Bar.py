import sublime, sublime_plugin
import os
import functools
import shutil
import subprocess
import urllib
import re

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

class SideBarFilesEditCommand(sublime_plugin.WindowCommand):
	def run(self, paths):
		for path in paths:
			self.window.open_file(path)

	def is_enabled(self, paths):
		return len(paths) > 0

class SideBarFilesOpenCommand(sublime_plugin.WindowCommand):
	def run(self, paths):
		for path in paths:
			subprocess.Popen(r''+path, shell=True)

	def is_enabled(self, paths):
		return len(paths) > 0

class SideBarFilesOpenWithCommand(sublime_plugin.WindowCommand):
	def run(self, paths):
		for path in paths:
			subprocess.Popen(r''+path, shell=True)

	def is_enabled(self, paths):
		return False

class SideBarFilesFindInSelectedCommand(sublime_plugin.WindowCommand):
	def run(self, paths):
		self.window.run_command('hide_panel');
		self.window.run_command("show_panel", {"panel": "find_in_files", "location": ",".join(paths)})

	def is_enabled(self, paths):
		return len(paths) > 0
			
class SideBarFilesFindInParentCommand(sublime_plugin.WindowCommand):
	def run(self, paths):
		paths[0] = os.path.dirname(paths[0])
		self.window.run_command('hide_panel');
		self.window.run_command("show_panel", {"panel": "find_in_files", "location": ",".join(paths)})

	def is_enabled(self, paths):
		return len(paths) > 0

class SideBarFilesFindInProjectCommand(sublime_plugin.WindowCommand):
	def run(self):
		self.window.run_command('hide_panel');
		self.window.run_command('show_panel', {"panel": "find_in_files", "location": "<open folders>"});

class SideBarFilesCutCommand(sublime_plugin.WindowCommand):
	def run(self, paths):
		s = sublime.load_settings("SideBar Files.sublime-settings")
		s.set('cut', paths)
		s.set('copy', [])
		if len(paths) > 1 :
			sublime.status_message("Items cut")
		else :
			sublime.status_message("Item cut")

	def is_enabled(self, paths):
		return len(paths) > 0

class SideBarFilesCopyCommand(sublime_plugin.WindowCommand):
	def run(self, paths):
		s = sublime.load_settings("SideBar Files.sublime-settings")
		s.set('cut', [])
		s.set('copy', paths)
		if len(paths) > 1 :
			sublime.status_message("Items copied")
		else :
			sublime.status_message("Item copied")

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

class SideBarFilesCopyNameCommand(sublime_plugin.WindowCommand):
	def run(self, paths):
		to_copy = []
		for path in paths:
			branch, leaf = os.path.split(path)
			to_copy.append(leaf)
		sublime.set_clipboard("\n".join(to_copy));
		if len(to_copy) > 1 :
			sublime.status_message("Items copied")
		else :
			sublime.status_message("Item copied")

	def is_enabled(self, paths):
		return len(paths) > 0

class SideBarFilesCopyNameEncodedCommand(sublime_plugin.WindowCommand):
	def run(self, paths):
		to_copy = []
		for path in paths:
			branch, leaf = os.path.split(path)
			to_copy.append(urllib.quote(leaf.encode('utf-8')))
		sublime.set_clipboard("\n".join(to_copy));
		if len(to_copy) > 1 :
			sublime.status_message("Items copied")
		else :
			sublime.status_message("Item copied")

	def is_enabled(self, paths):
		return len(paths) > 0

class SideBarFilesCopyPathCommand(sublime_plugin.WindowCommand):
	def run(self, paths):
		to_copy = []
		for path in paths:
			to_copy.append(path)
		sublime.set_clipboard("\n".join(to_copy));
		if len(to_copy) > 1 :
			sublime.status_message("Items copied")
		else :
			sublime.status_message("Item copied")

	def is_enabled(self, paths):
		return len(paths) > 0

class SideBarFilesCopyPathEncodedCommand(sublime_plugin.WindowCommand):
	def run(self, paths):
		to_copy = []
		for path in paths:
			to_copy.append('file:'+urllib.pathname2url(path.encode('utf-8')))
		sublime.set_clipboard("\n".join(to_copy));
		if len(to_copy) > 1 :
			sublime.status_message("Items copied")
		else :
			sublime.status_message("Item copied")

	def is_enabled(self, paths):
		return len(paths) > 0

class SideBarFilesCopyPathRelativeCommand(sublime_plugin.WindowCommand):
	def run(self, paths):
		to_copy = []
		for path in paths:
			for folder in sublime.active_window().folders():
				path = re.sub('^'+re.escape(folder), '', path)
			to_copy.append(re.sub('^/', '', path.replace('\\', '/')))
		sublime.set_clipboard("\n".join(to_copy));
		if len(to_copy) > 1 :
			sublime.status_message("Items copied")
		else :
			sublime.status_message("Item copied")

	def is_enabled(self, paths):
		return len(paths) > 0

class SideBarFilesCopyPathRelativeEncodedCommand(sublime_plugin.WindowCommand):
	def run(self, paths):
		to_copy = []
		for path in paths:
			for folder in sublime.active_window().folders():
				path = re.sub('^'+re.escape(folder), '', path)
			to_copy.append(re.sub('^/', '', urllib.quote(path.replace('\\', '/').encode('utf-8'))))

		sublime.set_clipboard("\n".join(to_copy));
		if len(to_copy) > 1 :
			sublime.status_message("Items copied")
		else :
			sublime.status_message("Item copied")

	def is_enabled(self, paths):
		return len(paths) > 0

class SideBarFilesCopyPathAbsoluteCommand(sublime_plugin.WindowCommand):
	def run(self, paths):
		to_copy = []
		for path in paths:
			for folder in sublime.active_window().folders():
				path = re.sub('^'+re.escape(folder), '', path)
			to_copy.append(path.replace('\\', '/'))
		sublime.set_clipboard("\n".join(to_copy));
		if len(to_copy) > 1 :
			sublime.status_message("Items copied")
		else :
			sublime.status_message("Item copied")

	def is_enabled(self, paths):
		return len(paths) > 0

class SideBarFilesCopyPathAbsoluteEncodedCommand(sublime_plugin.WindowCommand):
	def run(self, paths):
		to_copy = []
		for path in paths:
			for folder in sublime.active_window().folders():
				path = re.sub('^'+re.escape(folder), '', path)
			to_copy.append(urllib.quote(path.replace('\\', '/').encode('utf-8')))

		sublime.set_clipboard("\n".join(to_copy));
		if len(to_copy) > 1 :
			sublime.status_message("Items copied")
		else :
			sublime.status_message("Item copied")

	def is_enabled(self, paths):
		return len(paths) > 0

class SideBarFilesCopyTagAhrefCommand(sublime_plugin.WindowCommand):
	def run(self, paths):
		to_copy = []
		for path in paths:
			branch, leaf = os.path.split(path)
			for folder in sublime.active_window().folders():
				path = re.sub('^'+re.escape(folder), '', path)
			to_copy.append('<a href="'+urllib.quote(path.replace('\\', '/').encode('utf-8'))+'">'+leaf+'</a>')

		sublime.set_clipboard("\n".join(to_copy));
		if len(to_copy) > 1 :
			sublime.status_message("Items copied")
		else :
			sublime.status_message("Item copied")

	def is_enabled(self, paths):
		return len(paths) > 0

class SideBarFilesCopyTagImgCommand(sublime_plugin.WindowCommand):
	def run(self, paths):
		to_copy = []
		for path in paths:
			for folder in sublime.active_window().folders():
				path = re.sub('^'+re.escape(folder), '', path)
			to_copy.append('<img src="'+urllib.quote(path.replace('\\', '/').encode('utf-8'))+'"/>')

		sublime.set_clipboard("\n".join(to_copy));
		if len(to_copy) > 1 :
			sublime.status_message("Items copied")
		else :
			sublime.status_message("Item copied")

	def is_enabled(self, paths):
		return len(paths) > 0

class SideBarFilesCopyTagStyleCommand(sublime_plugin.WindowCommand):
	def run(self, paths):
		to_copy = []
		for path in paths:
			for folder in sublime.active_window().folders():
				path = re.sub('^'+re.escape(folder), '', path)
			to_copy.append('<link rel="stylesheet" type="text/css" href="'+urllib.quote(path.replace('\\', '/').encode('utf-8'))+'"/>')

		sublime.set_clipboard("\n".join(to_copy));
		if len(to_copy) > 1 :
			sublime.status_message("Items copied")
		else :
			sublime.status_message("Item copied")

	def is_enabled(self, paths):
		return len(paths) > 0

class SideBarFilesCopyTagScriptCommand(sublime_plugin.WindowCommand):
	def run(self, paths):
		to_copy = []
		for path in paths:
			for folder in sublime.active_window().folders():
				path = re.sub('^'+re.escape(folder), '', path)
			to_copy.append('<script type="text/javascript" src="'+urllib.quote(path.replace('\\', '/').encode('utf-8'))+'"></script>')

		sublime.set_clipboard("\n".join(to_copy));
		if len(to_copy) > 1 :
			sublime.status_message("Items copied")
		else :
			sublime.status_message("Item copied")

	def is_enabled(self, paths):
		return len(paths) > 0

class SideBarFilesCopyProjectFoldersCommand(sublime_plugin.WindowCommand):
	def run(self, paths):
		to_copy = []
		for folder in sublime.active_window().folders():
			to_copy.append(folder)

		sublime.set_clipboard("\n".join(to_copy));
		if len(to_copy) > 1 :
			sublime.status_message("Items copied")
		else :
			sublime.status_message("Item copied")

	def is_enabled(self, paths):
		return True

class SideBarFilesCopyContentUtf8Command(sublime_plugin.WindowCommand):
	def run(self, paths):
		to_copy = []
		for path in paths:
			if(os.path.isdir(path)):
				continue
			data = file(path, "r").read();
			try:
				to_copy.append(unicode(data, "utf-8"))
			except:
				to_copy.append(data)

		sublime.set_clipboard("\n".join(to_copy));
		if len(paths) > 1 :
			sublime.status_message("Items content copied")
		else :
			sublime.status_message("Item content copied")

	def is_enabled(self, paths):
		return len(paths) > 0

class SideBarFilesCopyContentBase64Command(sublime_plugin.WindowCommand):
	def run(self, paths):
		to_copy = []
		import mimetypes
		for path in paths:
			if(os.path.isdir(path)):
				continue
			mime = mimetypes.guess_type(path)[0] or 'text/plain'
			to_copy.append('data:'+mime+';base64,'+(file(path, "rb").read().encode("base64").replace('\n', '')))

		sublime.set_clipboard("\n".join(to_copy));
		if len(paths) > 1 :
			sublime.status_message("Items content copied")
		else :
			sublime.status_message("Item content copied")

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
					self.window.open_file(dst);
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
				print ("Unable to remove file:\n\n"+path)

	def remove_safe_dir(self, path):
		if path != '' and path != '/' and path != '//' and path != '\\' and path != '\\\\':
			try:
				os.rmdir(path)
			except:
				print ("Unable to remove directory:\n\n"+path)

	def is_enabled(self, paths):
		return len(paths) == 1


class SideBarFilesRevealCommand(sublime_plugin.WindowCommand):
	def run(self, paths):
		for path in paths:
			branch, leaf = os.path.split(path)
			self.window.run_command("open_dir", {"dir": branch, "file": leaf} )

	def is_enabled(self, paths):
		return len(paths) > 0