import sublime, sublime_plugin, time
from os.path import getmtime

s = sublime.load_settings('Side Bar.sublime-settings')

class StatusBarModifiedTime(sublime_plugin.EventListener):

	def on_load(self, v):
		if s.get('statusbar_modified_time') and v.file_name():
			self.show(v, getmtime(v.file_name()))
		
	def on_post_save(self, v):
		if s.get('statusbar_modified_time') and v.file_name():
			self.show(v, getmtime(v.file_name()))

	def show(self, v, mtime):
		v.set_status('statusbar_modified_time',  time.strftime(s.get('statusbar_modified_time_format'), time.localtime(mtime)));

		