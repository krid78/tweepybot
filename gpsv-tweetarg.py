#!/bin/env python -d -t
# -*- encoding: utf-8 -*-
"""
Package       :  tweetarg
Author(s)     :  Daniel Kriesten
Email         :  krid@tu-chemnitz.eu
Creation Date :  Fr 17 Sep 2010 22:24:11 #u

Send the first command line argument to a twitter account.
The accounts information is read from a configuration file.

Dependencies:
	* python 2.5.X
	* tweepy 1.7.1

TODO:
	* use username as section for access tokens -> then one rc-file works for several users
	* enhance command line parser
"""

import sys
import ConfigParser
import tweepy

class api_auth_factory:
	"""
	Create an authenticated api object, using the information in the .rc-file.
	If no .rc-file is found, create one with basic information.
	"""

	def __call__(self, config_file_name = ['.gpsvtweetargrc']):
		return self._get_configdata(config_file_name)

	def _get_configdata(self, file_name):
		"""
		Try to read config file, or ceate one.
		The information for the basic account are left blank!!
		"""
		config = ConfigParser.RawConfigParser()
		config.read(file_name)
		# configuration data with default values
		config_data = {
				'consumer_key': '',
				'consumer_secret': '',
				'username': ''
				}
		# try to read config file or create onr from defaults
		try:
			config_data['consumer_key'] = config.get('LoginData', 'consumer_key')
			config_data['consumer_secret'] = config.get('LoginData', 'consumer_secret')
			config_data['username'] = config.get('LoginData', 'username')
		except (ConfigParser.NoSectionError, ConfigParser.NoOptionError, ConfigParser.ParsingError), e:
			print 'Error reading configuration file:', e
			print 'Creating default one.'
			config.add_section('LoginData')
			config.set('LoginData', 'consumer_key', config_data['consumer_key'])
			config.set('LoginData', 'consumer_secret', config_data['consumer_secret'])
			config.set('LoginData', 'username', config_data['username'])

		# try to read oauth data or start oauth authentication
		try:
			config_data['access_key'] = config.get('LoginData', 'access_key')
			config_data['access_secret'] = config.get('LoginData', 'access_secret')
		except (ConfigParser.NoSectionError, ConfigParser.NoOptionError, ConfigParser.ParsingError), e:
			print 'Not registered, yet: %s' %e
			print 'Starting initial authentication.'
			api = self._initial_authentication(config, config_data)
			config_file = open (file_name[0], 'w')
			config.write(config_file)
			config_file.close()
		else:
			api = self._reuse_authentication(config_data)
		return api

	def _initial_authentication(self, config, data):
		"""
		Do the full initial oauth authentication.
		
		As a command line client we assume no browser or graphical backend. So the user only gets the request url.
		"""
		print 'Initial authentication'
		auth = tweepy.OAuthHandler(data['consumer_key'], data['consumer_secret'])
		try:
			print 'getting request url'
			redirect_url = auth.get_authorization_url()
		except tweepy.TweepError:
			print 'Error! Failed to get request token.'
			tweepy.debug()
			raise SystemExit(0)
		#user interaction needed!!
		print "Pleas copy th following url to a browser."
		print redirect_url
		print "Identify with the twitter account provided for this application"
		print "and allow the requested access."
		print "Return to this shell and enter the verifyer, offered by twitter."
		verifier = raw_input('Verifier: ')
		try:
			auth.get_access_token(verifier)
		except tweepy.TweepError:
			print 'Error! Failed to get access token.'
			tweepy.debug()
			raise SystemExit(0)
		else:
			config.set('LoginData', 'access_key', auth.access_token.key)
			config.set('LoginData', 'access_secret', auth.access_token.secret)
		# successful registered!
		return tweepy.API(auth)

	def _reuse_authentication(self, data):
		"""
		Create an api object using known authentication data.
		"""
		auth = tweepy.OAuthHandler(data['consumer_key'], data['consumer_secret'])
		auth.set_access_token(data['access_key'], data['access_secret'])
		return tweepy.API(auth)

if __name__ == '__main__':
	api = api_auth_factory().__call__(['.gpsvtweetargrc','/etc/gpsvtweetargrc'])

	print "****************************************"
	print "API() created for", api.me().name, "(", api.me().screen_name, api.me().id, ")"
	print "****************************************"

	if len(sys.argv) > 1:
		api.update_status(sys.argv[1])

# vim: ts=2:sw=2:sts=2:fileformat=unix
# vim: comments& comments+=b\:# formatoptions& formatoptions+=or
