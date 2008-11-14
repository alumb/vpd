from pyinotify import WatchManager, Notifier,  ProcessEvent, IN_CREATE
import signal
import conf


wm = WatchManager()  # Watch Manager

class PActions(ProcessEvent):
	def process_IN_CREATE(self, event):
		print "Creating:", event.pathname

notifier = Notifier(wm, PActions())
wdd = wm.add_watch(conf.conf["transcodeDirectory"], IN_CREATE)


print "watching ", conf.conf["transcodeDirectory"]
notifier.loop()

#notifier.stop()


