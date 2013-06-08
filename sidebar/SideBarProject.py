import sublime

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
			if path.find(folder['path']) == 0:
				try:
					folder['folder_exclude_patterns'].append(exclude)
				except:
					folder['folder_exclude_patterns'] = [exclude]
				self.setProjectJson(data);
				return

	def excludeFile(self, path, exclude):
		data = self.getProjectJson()
		for folder in data['folders']:
			if path.find(folder['path']) == 0:
				try:
					folder['file_exclude_patterns'].append(exclude)
				except:
					folder['file_exclude_patterns'] = [exclude]
				self.setProjectJson(data);
				return

	def add(self, path):
		data = self.getProjectJson()
		data['folders'].append({'follow_symlinks':True, 'path':path});
		self.setProjectJson(data);

	def refresh(self):
		try:
			sublime.set_timeout(lambda:sublime.active_window().run_command('refresh_folder_list'), 200);
			sublime.set_timeout(lambda:sublime.active_window().run_command('refresh_folder_list'), 1300);
		except:
			pass