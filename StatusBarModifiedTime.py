import sublime, sublime_plugin, time
from os.path import getmtime

s = {}

def plugin_loaded():
	global s
	s = sublime.load_settings('Side Bar.sublime-settings')

class StatusBarModifiedTime(sublime_plugin.EventListener):

	def on_activated_async(self, v):
		if s.get('statusbar_modified_time') and v.file_name():
			try:
				self.show(v, getmtime(v.file_name()))
			except:
				pass

	def on_post_save_async(self, v):
		if s.get('statusbar_modified_time') and v.file_name():
			try:
				self.show(v, getmtime(v.file_name()))
			except:
				pass

	def show(self, v, mtime):
		v.set_status('statusbar_modified_time',  time.strftime(s.get('statusbar_modified_time_format'), time.localtime(mtime)));