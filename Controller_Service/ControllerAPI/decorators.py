import time
from .exceptions import APICallException
from django.http import HttpResponse
from rest_framework import status
import json



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
					print(f'trial {i} failed. waiting to retry...')
					time.sleep(wait)
					pass
				else:
					return res
			raise APICallException
		return wrapper
	return decorator


def supported_methods(methods=[]):
	def decorator(function):
		def wrapper(*args, **kwargs):
			method = args[0].method
			if method not in methods:
				return HttpResponse(status=status.HTTP_405_METHOD_NOT_ALLOWED)
			return function(*args, **kwargs)
		return wrapper
	return decorator


def body_check(keys=[]):
	'''----make sure the given keys exist in request body keys----
	'''
	def decorator(function):
		def wrapper(*args, **kwargs):
			request = args[0]
			try:
				req_str = request.body.decode("utf-8", errors="strict")
				req_dict = json.loads(req_str)
				req_keys = list(req_dict.keys())
				for key in keys:
					if key not in req_keys:
						return HttpResponse(f'missing key {key}', status=status.HTTP_400_BAD_REQUEST)
			except Exception as e:
				print(e)
				return HttpResponse(e, status=status.HTTP_400_BAD_REQUEST)
			return function(*args, **kwargs)
		return wrapper
	return decorator
