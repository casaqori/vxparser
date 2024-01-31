"""
appconfig
=========

Module for handling app configuration

Copyright (c) 2020 Tom Arn, www.t-arn.com

For suggestions and questions:
<sw@t-arn.com>

This file is distributed under the terms of the MIT license
"""

import json


def read_config (config_dir, config_default):
	"""
	Reads the app config from the json file config.json.

	When the file does not exist, it is created using the config_default

	When config_default contains attributes that do not exist in the json file or when the json file
	contains attributes that do not exist in config_default, write_config() is called to update the
	json file.

	:param str config_dir: the directory containing the config.json file
	:param dict config_default: the default config
	:returns: the config dict
	:rtype: dict
	"""
	new_config = config_default.copy()
	# read from file
	try:
		with open(config_dir + '/config.json') as json_file:
			old_config = json.load(json_file)
	except:
		old_config = {}
	_added = False
	_keys = new_config.keys()
	for _key in _keys:
		_value = old_config.get(_key)
		if _value is None:
			_added = True
		else:
			new_config.update({_key: _value})
	if _added or len(_keys) < len(old_config.keys()):
		write_config(config_dir, new_config)
	return new_config
# read_config


def write_config (config_dir, config):
	"""
	Write the app config to the json file config.json.

	:param str config_dir: the directory containing the config.json file
	:param dict config: the config dict
	"""
	print('writing config to file')
	with open(config_dir + '/config.json', 'w') as json_file:
		json.dump(config, json_file, indent=2)
# write_config
