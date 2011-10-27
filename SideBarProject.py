import sublime

class SideBarProject:

	def getDirectories(self):
		return sublime.active_window().folders()

	#def getProjectFile():