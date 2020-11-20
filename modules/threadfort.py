import threading

class ThreadFort:
	def __init__(self):
		self.threads   = []

		self.stop_lock    = threading.Lock()
		self.stop_threads = False

		self.print_lock = threading.Lock()

	def tprint(self, pstring):
		try:
			self.print_lock.acquire()
			print(f"{pstring}")
		
		finally:
			self.print_lock.release()

	def stop(self):
		try:
			self.stop_lock.acquire()
			stop = self.stop_threads
		
		finally:
			self.stop_lock.release()
		
		return stop

	def shutdown(self):
		try:
			self.stop_lock.acquire()
			self.stop_threads = True
		
		finally:
			self.stop_lock.release()
