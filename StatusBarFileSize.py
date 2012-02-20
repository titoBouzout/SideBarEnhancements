import sublime, sublime_plugin
from hurry.filesize import size
from os.path import getsize

s = sublime.load_settings('Side Bar.sublime-settings')

class StatusBarFileSize(sublime_plugin.EventListener):

	def on_load(self, v):
		if s.get('statusbar_file_size') and v.file_name():
			try:
				self.show(v, size(getsize(v.file_name())))
			except:
				pass

	def on_post_save(self, v):
		if s.get('statusbar_file_size') and v.file_name():
			try:
				self.show(v, size(getsize(v.file_name())))
			except:
				pass

	def show(self, v, size):
		v.set_status('statusbar_file_size', size);