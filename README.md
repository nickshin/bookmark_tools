# Bookmark Tools

**bookmarks_scrubber** scrubs out (Firefox JSON) bookmark entries (URLs &amp; folders) with titles that begin with **--** (double dashes).  This also makes it easier to visually see them in the Bookmarks Organizers.

**bookmarks_jstree** will generate the data for the wonderful [jstree](https://www.jstree.com/) of my (Firefox JSON) bookmarks.

## Quick Start

**Backup** your (Firefox) bookmarks to JSON file.
  * Menu
  * Bookmarks
  * Show All Bookmarks (CTRL+Shift+O)
  * Import and Backup
  * Backup...
  * Save &lt;bookmarks-yyyy-mm-dd.json&gt; file

**Scrub** the bookmarks:
```sh
python bookmarks_scrubber.py -s -i bookmarks-yyyy-mm-dd.json -o bookmarks-scrubbed.json
```

**Generate** the jstree data json file:
```sh
python bookmarks_jstree.py -i bookmarks-scrubbed.json -o jstree-data.json
```

OR -- Pipe the scripts together:
```sh
cat bookmarks-yyyy-mm-dd.json | python bookmarks_scrubber.py -s | python bookmarks_jstree.py > jstree-data.json
```

Upload the **jstree-data.json** and **bookmarks_jstree.{php,html}** files up to your webserver.

#### PHP vs HTML

These two files are essentially the same.  The PHP version will inline the jstree data while the HTML version will fetch it separately.  Use whichever version suits your need.

## Docs

```
Usage:
    ./bookmarks_jstree.py [options]

Options are:
	-h, --help
		This usage message.

	-i filename, --input=filename
		Read JSON data from [ filename ] or else, read data from [ stdin ].

	-o filename, --output=filename
		Output results to [ filename ] or else, output to [ stdout ].

Special Note: Titles that start with *** (triple stars) will be displayed in BOLD.
```

```
Usage:
    ./bookmarks_scrubber.py [options]

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
```

### Example

Take a look at the following bookmark library example.

![bookmark library example](https://github.com/nickshin/bookmark_tools/raw/master/img/example_library.png)

By just glancing, you will be able to quickly tell which folders and files will be ~~scrubbed out~~ -- as well as which ones will be displayed in **bold**.

After running the commands shown in the [quick start](#quick-start) section, here is the result of this example.

![bookmarks online](https://github.com/nickshin/bookmark_tools/raw/master/img/example_live.png)

## Live Demo

View my latest [bookmarks online](https://nickshin.com/bookmark_tools/demo/index.html).

## FAQ

### How can I make this fully automatic with my latest bookmarks?

Use (for example) [lz4jsoncat](https://github.com/andikleen/lz4json) with these tools:

```sh
BKMRKS=~/.mozilla/firefox/*.default/bookmarkbackups; ./lz4jsoncat $BKMRKS/`ls -t $BKMRKS | head -1` | \
	python bookmarks_scrubber.py -s | python bookmarks_jstree.py > jstree-data.json
```

See the following [stackexchange post](https://unix.stackexchange.com/questions/326897/how-to-decompress-jsonlz4-files-firefox-bookmark-backups-using-the-command-lin/338880) for additional information on how to build lz4jsoncat.

## License

[Unlicense](http://unlicense.org/)

