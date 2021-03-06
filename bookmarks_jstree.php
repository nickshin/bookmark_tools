<!DOCTYPE html>
<html>
<head>
	<title>My Bookmarks</title>
	<link rel="stylesheet" href="//static.jstree.com/3.3.3/assets/bootstrap/css/bootstrap.min.css" />
	<link rel="stylesheet" href="//static.jstree.com/3.3.3/assets/dist/themes/default/style.min.css" />
	<link rel="stylesheet" href="//static.jstree.com/3.3.3/assets/docs.css" />

<style>
.demo {
	background:white;
	border:3px solid gray;
	float: left;
	width: 200px
}
</style>
</head>
<body style="height:90%">

<h2>My Bookmarks</h2>
<div id="jt_everything" style="display:none"></div>
<div id="leftside">
	<div id="jt_folders" class="demo" style="position:absolute; left:20px; height:75vh">
		<span style="margin-top:36px; display:block; text-align:center;">Loading...</span>
	</div>
</div>
<div id="rightside">
	<div class="demo" style="position:absolute; left:250px; height:75vh; width:70%">
		<div id="breadcrumb"></div>
		<div id="content" style=" font-family:Verdana !important; font-size:12px !important; ">
		This page was created using the wonderful <a href="http://jstree.com/">jsTree</a> library.
		<p>
		You can find it at <a href="https://jstree.com/">https://jstree.com/</a>.
		<p>
		Enjoy! ^_^
		<p>
		<hr>
		<p>
		Just in case anyone is interested in knowing how to streamline their JSON bookmarks
		to be used with the jsTree library, please visit my
		<a href="https://github.com/nickshin/bookmark_tools">Bookmark Tools</a> on github.
		(and of course, view source)
		</div>
	</div>
</div>
<div id="bottom" class="demo" style="position:absolute; left:250px; bottom:5px; width:70%; height:55px">
These are the bookmarks from <a href="/">Nick Shin</a>.  I hope you may find something interesting while you are here.<br>
Bookmarks last updated at:
<?php
echo date( "F d, Y", filemtime( "jstree-data.json" ) );
?>
</div>

<script src="//cdnjs.cloudflare.com/ajax/libs/jquery/3.1.1/jquery.min.js"></script>
<script src="//cdnjs.cloudflare.com/ajax/libs/jstree/3.3.3/jstree.min.js"></script>
<script>
	var $jt_everything = null;
	var $jt_folders = null;
	var $breadcrumb = $("#breadcrumb");
	var $content = null;
	// ----------------------------------------
	var jstree_data = <? include("jstree-data.json"); ?>;
	// ----------------------------------------
	$("#jt_everything").jstree(
		{"core":{"data": jstree_data },
		"types":{
			"file":{"icon":"glyphicon glyphicon-leaf"},
			"line":{"icon":"none"}
		},
		"plugins":["themes","types"]
	}).on("ready.jstree", function() {
		$jt_everything = $.jstree.reference("#jt_everything");
	});
	// ----------------------------------------
	function reset_content(data) {
		if ( $content )
			$content.destroy();
		$("#content").jstree({"core":{"data":
			data
		}}).on("ready.jstree", function() {
			$content = $.jstree.reference("#content");
			$content.open_all();
		}).on("changed.jstree", function( e, data ) {
			var href = data.node.a_attr.href;
			if ( href == '#' ) { // folder
				$jt_folders.open_node(("" + data.selected).replace(/_\d+$/,""));
				$jt_folders.deselect_all();
				$jt_folders.select_node(data.selected);
			} else { // link
				window.open(href, "window_" + data.selected);
			}
		});
	}
	// ----------------------------------------
	var folders = [];
	jstree_data.forEach(function(e) {
		if ( e.type == "folder" )
			folders.push(e);
	});
    $("#jt_folders").jstree({"core":{"data": folders}})
	.on("ready.jstree", function() {
		$jt_folders = $.jstree.reference("#jt_folders");
		$jt_folders.open_all();
	}).on("changed.jstree", function( e, data ) {
		if ( ! data.selected.length )
			return; // deselect_all
		// ....................
		$breadcrumb.html('<h3>' + $jt_folders.get_path(data.selected, ' -> ') + '</h3><p>' );
		// ....................
		var j = $jt_everything.get_json(data.selected);
		j.children.forEach(function(e) {
			e.children.length = 0;
		});
		reset_content(j.children);
	});
	// ----------------------------------------
</script>
</body>
</html>
