import sublime
import re
import os

class SideBarProject:

	def getDirectories(self):
		return sublime.active_window().folders()

	def hasOpenedProject(self):
		return self.getProjectFile() != None

	def getDirectoryFromPath(self, path):
		for directory in self.getDirectories():
			maybe_path = path.replace(directory, '', 1)
			if maybe_path != path:
				return directory

	def getProjectFile(self):
		if not self.getDirectories():
			return None
		import json
		data = open(os.path.normpath(os.path.join(sublime.packages_path(), '..', 'Settings', 'Session.sublime_session')), 'r').read()
		data = data.replace('\t', ' ')
		data = json.loads(data, strict=False)
		projects = data['workspaces']['recent_workspaces']

		if os.path.lexists(os.path.join(sublime.packages_path(), '..', 'Settings', 'Auto Save Session.sublime_session')):
			data = open(os.path.normpath(os.path.join(sublime.packages_path(), '..', 'Settings', 'Auto Save Session.sublime_session')), 'r').read()
			data = data.replace('\t', ' ')
			data = json.loads(data, strict=False)
			if 'workspaces' in data and 'recent_workspaces' in data['workspaces'] and data['workspaces']['recent_workspaces']:
				projects += data['workspaces']['recent_workspaces']
			projects = list(set(projects))
		for project_file in projects:
			project_file = re.sub(r'^/([^/])/', '\\1:/', project_file);
			project_json = json.loads(open(project_file, 'r').read(), strict=False)
			if 'folders' in project_json:
				folders = project_json['folders']
				found_all = True
				for directory in self.getDirectories():
					found = False
					for folder in folders:
						folder_path = re.sub(r'^/([^/])/', '\\1:/', folder['path']);
						if folder_path == directory.replace('\\', '/'):
							found = True
							break;
					if found == False:
						found_all = False
						break;
			if found_all:
				return project_file
		return None

	def getProjectJson(self):
		if not self.hasOpenedProject():
			return None
		import json
		return json.loads(open(self.getProjectFile(), 'r').read(), strict=False)

	def excludeDirectory(self, path):
		import json
		project_file = self.getProjectFile();
		project = self.getProjectJson()

		path = re.sub(r'^([^/])\:/', '/\\1/', path.replace('\\', '/'))

		for folder in project['folders']:
			if path.find(folder['path']) == 0:
				try:
					folder['folder_exclude_patterns'].append(re.sub(r'/+$', '', path.replace(folder['path']+'/', '', 1)))
				except:
					folder['folder_exclude_patterns'] = [re.sub(r'/+$', '', path.replace(folder['path']+'/', '', 1))]
				open(project_file, 'w+').write(json.dumps(project, indent=1))
				return

	def excludeFile(self, path):
		import json
		project_file = self.getProjectFile();
		project = self.getProjectJson()

		path = re.sub(r'^([^/])\:/', '/\\1/', path.replace('\\', '/'))

		for folder in project['folders']:
			if path.find(folder['path']) == 0:
				try:
					folder['file_exclude_patterns'].append(path.replace(folder['path']+'/', '', 1))
				except:
					folder['file_exclude_patterns'] = [path.replace(folder['path']+'/', '', 1)]
				open(project_file, 'w+').write(json.dumps(project, indent=1))
				return

	def rootAdd(self, path):
		import json
		project_file = self.getProjectFile();
		project = self.getProjectJson()

		path = re.sub(r'^([^/])\:/', '/\\1/', path.replace('\\', '/'))
		project['folders'].append({'path':path});

		open(project_file, 'w+').write(json.dumps(project, indent=1))

	def refresh(self):
		try:
			sublime.set_timeout(lambda:sublime.active_window().run_command('refresh_folder_list'), 200);
			sublime.set_timeout(lambda:sublime.active_window().run_command('refresh_folder_list'), 600);
			sublime.set_timeout(lambda:sublime.active_window().run_command('refresh_folder_list'), 1300);
			sublime.set_timeout(lambda:sublime.active_window().run_command('refresh_folder_list'), 2300);
		except:
			pass

	def getPreference(self, name):
		if not self.hasOpenedProject():
			return None
		project = self.getProjectJson()
		try:
			return project[name]
		except:
			return None
