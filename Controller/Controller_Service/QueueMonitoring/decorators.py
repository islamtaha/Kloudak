#!/usr/bin/python3.6
import time


def retry(retries=1, wait=0):
	'''----decorator to retry executing API calls in case of failures(exceptions)----
		-raises APICallException
	'''
	def decorator(function):
		def wrapper(*args, **kwargs):
			for i in range(0, retries):
				try:
					res = function(*args, **kwargs)
				except:
					time.sleep(wait)
					pass
				else:
					return res
			raise Exception("request timedout")
		return wrapper
	return decorator