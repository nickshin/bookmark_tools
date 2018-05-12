#!/usr/bin/python
#
# Bookmark Tools - Scrubber
# written by Nick Shin - nick.shin@gmail.com
# created Oct 5 2010
#
# ==============================================================================
# Changelist:
#
# updated Mar 4 2017:
# + changed license to Unlicense
# + using "-- " at the beginning of "title:" to scrub item
#   o removing the [DO_NOT_EXPORT] scan in description field
# + split use of json objects vs custom json output (collapse new-line heavy json.dump)
# - removed flip option (seems to be fixed in firefox now...)
# - removed output to HTML
#   o existing bookmarks can be exported to HTML first
#   o import new JSON bookmarks and then re-import existing (HTML) bookmarks
# + added "Start root at [title] folder" option


import getopt				# getopt GetoptError
import sys					# exit stdin argv
import re					# compile search
import json					# loads


# these are not exported via Bookmark Organizer - so neither shall we
root_folders_to_scrub = ( "tagsFolder", "unfiledBookmarksFolder" ) #, "mobileFolder" )


# ================================================================================
# JSONBKMKS {{{
# ================================================================================

def jsonbkmks( jsonobj, root, scrub, scrubtitles ):
	if not root:
		return __jsonbkmks( jsonobj, scrub, scrubtitles )
	return __jsonbkmks_scan_for_root( jsonobj, root, scrub, scrubtitles )

def __jsonbkmks( jsonobj, scrub, scrubtitles, _depth = 0 ):
	title = ""
	if jsonobj.has_key('title'):
		title = jsonobj['title']
	if scrub and title.startswith('--'):
		return None

	_type = jsonobj['type']
	result = { 'title' : title, 'type' : _type }

	if _type == 'text/x-moz-place-container':
		# ----------------------------------------
		# check if folder is on the scrub list
		if scrub and (scrubtitles != None):
			for _ in scrubtitles:
				if _ in title:
					return None
		if jsonobj.has_key('root'):
			_root = jsonobj['root']
			if _root in root_folders_to_scrub:
				return None
			result['root'] = _root
			# assignment: add multiple --root found check here
		# ----------------------------------------
		# drill down children array
		if jsonobj.has_key('children') and (len( jsonobj['children'] ) > 0):
			_depth += 1
			children = []
			for _ in jsonobj['children']:
				child = __jsonbkmks( _, scrub, scrubtitles, _depth )
				if child != None:
					children.append(child)
			if len(children) > 0:
				result['children'] = children
			_depth -= 1
	else:
		if jsonobj.has_key('uri'): # _type == 'text/x-moz-place'
			result['uri'] = jsonobj['uri']
		# else _type == 'text/x-moz-place-separator'
	return result

def __jsonbkmks_scan_for_root( jsonobj, root, scrub, scrubtitles, _depth = 0 ):
	if jsonobj['type'] == 'text/x-moz-place-container' and \
			jsonobj.has_key('title') and jsonobj['title'] == root:
		return { "title" : "", "root" : "placesRoot", "type" : "text/x-moz-place-container",
				"children": [ __jsonbkmks( jsonobj, scrub, scrubtitles ) ] }
	# ----------------------------------------
	# drill down children array
	if jsonobj['type'] == 'text/x-moz-place-container' and \
			jsonobj.has_key('children') and (len( jsonobj['children'] ) > 0):
		_depth += 1
		for _ in jsonobj['children']:
			child = __jsonbkmks_scan_for_root( _, root, scrub, scrubtitles, _depth )
			if child != None:
				return child
		_depth -= 1
	# ----------------------------------------
	if _depth > 0:
		return None
	print 'root title: [' + root + '] not found - proceeding from top'
	return __jsonbkmks( jsonobj, scrub, scrubtitles )

# ================================================================================
# JSONBKMKS }}}
# COLLAPSE {{{
# ================================================================================

jsonescape = {	'\b': '\\b',
				'\t': '\\t',
				'\n': '\\n',
				'\f': '\\f',
				'\r': '\\r',
				'"' : '\\"',
				'\\': '\\\\' }

def jsonsafe( value ):
	# escape JSON compliant output

	if type( value ) is long or type( value ) is int:
		return str(value)

	results = ""
	for ch in value:
		try:
			results += jsonescape[ch]
		except:
			if ' ' <= ch <= '~':					#  i.e. 0x1f < ch < 0x7f
				results += ch
			elif type(ch) is unicode:				# python unicode
				results += ch.encode( 'ascii', 'ignore' )
			else:									# control character
				results += '\\u{0:04x}'.format( ch )
	return '"' + results + '"'

def collapse( jsonobj, _depth=0 ):
	# custom JSON dump printer
	title = ""
	if jsonobj.has_key('title'):
		title = jsonsafe(jsonobj['title'])
	indent = '\t' * _depth
	result = "" + indent + '{ "title" : ' + title + ', '
	if jsonobj.has_key('root'):
		result += '"root" : ' + jsonsafe(jsonobj['root']) + ', '
	if jsonobj.has_key('uri'):
		result += '"uri" : ' + jsonsafe(jsonobj['uri']) + ', '
	result += '"type" : "' + jsonobj['type'] + '"'

	if not jsonobj.has_key('children'):
		result += ' },\n'
	else:
		_depth += 1
		result += ',\n' + ('\t' * _depth) + '"children" : [\n'
		children = ""
		for _ in jsonobj['children']:
			children += collapse( _, _depth )
		result += children[:-2] # strip trailing comma
		result += '\n' + indent + '] },\n'
		_depth -= 1

	if _depth == 0:
		return result[:-2] # strip trailing comma
	return result

# ================================================================================
# COLLAPSE }}}
# MAIN {{{
# ================================================================================

def usage():
	print "Usage: " + sys.argv[0] + " [options]"
	print """
Options are:
	-h, --help
		This usage message.

	-i filename, --input=filename
		Read JSON data from [ filename ] or else, read data from [ stdin ].

	-o filename, --output=filename
		Output results to [ filename ] or else, output to [ stdout ].

	-r title, --root=title
		Start root at [title] folder.  Note: first match only!
	    No multiple match warnings will be given.

	-s, --scrub
		Scrub JSON entries with titles that start with -- (double dashes).

	-t title, --scrubtitles=title
		Additional FOLDERS (titles) to scrub out.
		This can be stacked: --scrubtitle=title1 --scrubtitle=title2 etc.
		(Scrubbing individual URLs is left as an exercise.)
"""


def main():
	# args ----------------------------------------
	try:
		opts, args = getopt.getopt( sys.argv[1:],
									"ho:i:r:st:",
									[ "help",
									  "output=", "input=",
									  "root",
									  "scrub", "scrubtitles="
									] )
	except getopt.GetoptError, err:
		print str(err)
		usage()
		sys.exit(2)

	datain  = None
	dataout = None
	scrub = False
	scrubtitles = []
	html = False
	root = None
	for o, a in opts:
		if o in ( "-h", "--help" ):
			usage()
			sys.exit()
		elif o in ( "-o", "--output" ):
			dataout = a
		elif o in ( "-i", "--input" ):
			datain = a
		elif o in ( "-r", "--root" ):
			root = a
		elif o in ( "-s", "--scrub" ):
			scrub = True
		elif o in ( "-t", "--scrubtitles" ):
			scrubtitles.append( "".join(a) )
		else:
			assert False, "unhandled option"

	# read and prep json text ----------------------------------------
	# json.loads() doesn't like newlines...
	data = ""
	if datain == None:
		for _ in sys.stdin:
			data += _.strip()
	else:
		f = open( datain, 'r' )
		if f:
			for _ in f:
				data += _.strip()
			f.close()
	
	# WORK ----------------------------------------
	objs = json.loads( data )
	results = jsonbkmks( objs, root, scrub, scrubtitles )

	# write out result ----------------------------------------
#	output = json.dumps(results)#, indent=4)
	output = collapse(results)
	if dataout == None:
		print output
	else:
		f = open( dataout, 'w' )
		if f:
			f.write( output )
			f.close()


if __name__ == "__main__":
	main()


# ================================================================================
# MAIN }}}
# ================================================================================
# vim:ts=4:noexpandtab
