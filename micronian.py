#!/usr/bin/env python3
import sys
import re

def load_file(_file):
	_buffer = ''
	chunk = 64 * 1024
	with open(_file, 'r') as f:
		for buf in iter(lambda: f.read(chunk), ''):
			_buffer += buf
	return _buffer

def build_table(prefix, regex, _buffer):
	table = {}
	table_len = 0
	for x in re.findall(regex, _buffer):
		key = '@!{}{}!@'.format(prefix, table_len)
		val = re.sub('[ \t\n]', '', x[1])
		table[key] = [escape(''.join(x)), val, ''.join((x[0], val, x[2]))]
		table_len += 1
	return table

def escape(val):
	v = val
	if '{' in v or '}' in v or '(' in v or ')' in v or  '|' in v or '*' in v or '.' in v:
		v = re.sub(r'\{', '\\{', re.sub(r'\}', '\\}', v))
		v = re.sub(r'\(', '\\(', re.sub(r'\)', '\\)', v))
		v = re.sub(r'\|', '\\|', re.sub(r'\*', '\\*', re.sub(r'\.', '\\.', v)))
	return v

def place_table(element, table, _buffer):
	buffer_copy = _buffer[:]
	for key, val in table.items():
		if element == 'keys':
			buffer_copy = re.sub(val[0], key, buffer_copy, count=1)
		else:
			buffer_copy = re.sub(key, val[2], buffer_copy, count=1)
	return buffer_copy

def remove_whitespace(_buffer):
	str_table = build_table('st', r'(["\'])(.*?)(["\'])', _buffer)
	buffer_copy0 = place_table('keys', str_table, _buffer)

	var_table = build_table('vt', r'(var )((?:.|[\r\n])*?)(;)', buffer_copy0)
	buffer_copy1 = place_table('keys', var_table, buffer_copy0)

	# Remove inlined comments /* ... */ and full line comments //...
	buffer_copy2 = re.sub(r'//.*', '', buffer_copy1)
	buffer_copy3 = re.sub(r'/\*(?:.|[\r\n])*?\*/', '', buffer_copy2)

	# Remove spaces (and tabs and newlines if you don't want to debug)
	#clean = re.sub(r' ', '', buffer_copy3)
	buffer_copy4 = re.sub(r'[ \t\n]', '', buffer_copy3)

	buffer_copy5 = place_table('vals', var_table, buffer_copy4)
	buffer_copy6 = place_table('vals', str_table, buffer_copy5)

	return buffer_copy6.replace('elseif', 'else if')

if __name__ == '__main__':
	if len(sys.argv) > 1 and sys.argv[1]:
		print(remove_whitespace(load_file(sys.argv[1])))
	else:
		print('{} <input.js>'.format(sys.argv[0]))
