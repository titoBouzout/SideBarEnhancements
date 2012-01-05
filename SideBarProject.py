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
		import json
		data = json.loads(file(os.path.normpath(os.path.join(sublime.packages_path(), '..', 'Settings', 'Session.sublime_session')), 'r').read())
		projects = data['workspaces']['recent_workspaces']
		for project_file in projects:
			project_file = re.sub(r'^/([^/])/', '\\1:/', project_file);
			folders = json.loads(file(project_file, 'r').read())['folders']
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

	def excludeDirectory(self, path):
		import json
		project_file = self.getProjectFile();
		project = json.loads(file(project_file, 'r').read())

		path = re.sub(r'^([^/])\:/', '/\\1/', path.replace('\\', '/'))

		for folder in project['folders']:
			if path.find(folder['path']) == 0:
				try:
					folder['folder_exclude_patterns'].append(re.sub(r'/+$', '', path.replace(folder['path']+'/', '', 1)))
				except:
					folder['folder_exclude_patterns'] = [re.sub(r'/+$', '', path.replace(folder['path']+'/', '', 1))]
				file(project_file, 'w+').write(json.dumps(project, indent=1))
				return

	def excludeFile(self, path):
		import json
		project_file = self.getProjectFile();
		project = json.loads(file(project_file, 'r').read())

		path = re.sub(r'^([^/])\:/', '/\\1/', path.replace('\\', '/'))

		for folder in project['folders']:
			if path.find(folder['path']) == 0:
				try:
					folder['file_exclude_patterns'].append(path.replace(folder['path']+'/', '', 1))
				except:
					folder['file_exclude_patterns'] = [path.replace(folder['path']+'/', '', 1)]
				file(project_file, 'w+').write(json.dumps(project, indent=1))
				return

	def rootAdd(self, path):
		import json
		project_file = self.getProjectFile();
		project = json.loads(file(project_file, 'r').read())

		path = re.sub(r'^([^/])\:/', '/\\1/', path.replace('\\', '/'))
		project['folders'].append({'path':path});

		file(project_file, 'w+').write(json.dumps(project, indent=1))

	def refresh(self):
		try:
			sublime.set_timeout(lambda:sublime.active_window().run_command('refresh_folder_list'), 200);
			sublime.set_timeout(lambda:sublime.active_window().run_command('refresh_folder_list'), 1300);
			sublime.set_timeout(lambda:sublime.active_window().run_command('refresh_folder_list'), 2300);
		except:
			pass