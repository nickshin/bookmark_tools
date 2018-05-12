#!/usr/bin/python
#
# Bookmark Tools - JsTree
# written by Nick Shin - nick.shin@gmail.com
# created Feb 9 2011
#
# ==============================================================================
# Changelist:
#
# updated Mar 4 2017:
# + changed license to Unlicense
# + upgraded to jstree 3.3.3 (which is single page load friendly)


import getopt				# getopt GetoptError
import sys					# exit stdin argv
import json					# loads


# ================================================================================
# JSON_BKMKS_NODES {{{
# ================================================================================

def jstree_nodes( jsonobj, jstree, _depth = "node_0" ):
	if not jsonobj.has_key('children') or len( jsonobj['children'] ) <= 0:
		return ""
	# ----------------------------------------
	i = 0;
	for child in jsonobj['children']:
		nodeid = _depth + '_' + str(i)
		i += 1
		title = child['title'] if child.has_key('title') and len( child['title'] ) > 0 else "UN-NAMED"
		if title.startswith('***'):
			title = '<b>' + title.replace( '***', '' ) + '</b>'

		parentMarker = "#" if _depth == "node_0" else _depth # special case
		if child['type'] == "text/x-moz-place-container":
			jstree.append({
					"id" : nodeid,
					"parent" : parentMarker,
					"text" : title,
					"type" : "folder" })

		elif child['type'] == "text/x-moz-place":
			jstree.append({
					"id" : nodeid,
					"parent" : parentMarker,
					"text" : title,
					"a_attr" : { "href" : child['uri'] },
					"type" : "file" })

		else:
			jstree.append({
					"id" : nodeid,
					"parent" : parentMarker,
					"text" : "----------------------------------------------------------------------------------------------------",
					"type" : "line" })
	# ----------------------------------------
	# drill down children array
	j = 0;
	for child in jsonobj['children']:
		nodeid = _depth + "_" + str(j)
		j += 1
		if child['type'] == "text/x-moz-place-container":
			jstree_nodes( child, jstree, nodeid )


# ================================================================================
# JSON_BKMKS_NODES }}}
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

Special Note: Titles that start with *** (triple stars) will be displayed in BOLD.
"""


def main():
	# args ----------------------------------------
	try:
		opts, args = getopt.getopt( sys.argv[1:],
									"ho:i:",
									[ "help",
									"output=", "input="
									] )
	except getopt.GetoptError, err:
		print str(err)
		usage()
		sys.exit(2)

	datain  = None
	dataout = None
	for o, a in opts:
		if o in ( "-h", "--help" ):
			usage()
			sys.exit()
		elif o in ( "-o", "--output" ):
			dataout = a
		elif o in ( "-i", "--input" ):
			datain = a
		else:
			assert False, "unhandled option"

	# read and prep json text ----------------------------------------
	# json.loads() doesn't like newlines...
	data = ""
	if datain == None:
		for _ in sys.stdin:
			data += _.strip()
	else:
		with open( datain, 'r' ) as f:
			for _ in f:
				data += _.strip()
			f.close()
	
	# WORK ----------------------------------------
	objs = json.loads( data )

	jstree = []
	jstree_nodes( objs, jstree )

	# write out result ----------------------------------------
	dump = json.dumps(jstree)
	if dataout == None:
		print dump
	else:
		with open( dataout, 'w' ) as f:
			f.write( dump )
			f.close()


if __name__ == "__main__":
	main()


# ================================================================================
# MAIN }}}
# ================================================================================
# vim:ts=4:noexpandtab
