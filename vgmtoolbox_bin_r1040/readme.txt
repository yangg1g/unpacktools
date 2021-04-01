----------------
VGMToolbox r146
----------------
VGMToolbox (VGMT) is a tool for auditing your emulated music files.  It calculates the 
checksums over actual data avoiding tags and other bits that are not important.
Please see the source for actual algorithms, perhaps someday I'll document them.

The currently supported formats include:
GBR, GBS, KSS (KSCC), MDX, NSF, NSFE, S98 (v1, v3), SPC (v0.30), VGM, 
xSF (all formats that meet the PSF spec).

VGMT also offers a range of tools, some specialized and usable for one or two
people, some useful to many.

--------------------
So what does it do?
--------------------
- Datafile Creator
  The Datafile Creator generates an xml file with the checksums of the files in 
  the source folder.  You can share this file with friends to compare 
  collections or throw it into the Datafile Checker to check for dupes.
  
- Rebuilder
  The Rebuilder takes a datafile xml generated with the Datafile Creator and
  will rename an existing collection to match the names in the datafile.  This
  is a good way to compare your collection to the collection of the datafile
  creator and see if you miss anything.  
  
  "HAVE.txt" and "MISS.txt" files will be generated to tell you what you 
  have/miss.  A new xml file will be genrated, typically called a "fixdat" 
  (like clrMAMEPro) as well.  This xml file will contain the checksums of the 
  files you miss so the author of the datafile can rebuild them and share them 
  if needed.  
  
  A "cache.db" file will also be generated to store the results of your scan in 
  case you want to back up your collection to offline media, but want to retain 
  a list of the files you have. "cache.db" is simply an array or your 
  checksums, compressed with zlib and serialized to disk.   

- Datafile Checker
  The Datafile Checker scans a generated datafile for duplicate checksums.  This
  can help you save space and, obviously, avoid dupes.  This is a good thing
  since many emulated music files are the same rip, simply with different tags.
  I have plans to incorporate high ASCII detection into the checker as well,
  since these things can cause issues among different international users.

- Examine
  The Examine tool has two subtools, the Tag Viewer and an MDX explorer
  
  - Tag Viewer
    The Tag Viewer will display information from the tag data of a file and 
    other internal data specific to each format.  Simply drag files or folders
    onto the "Source Folder" text box and wait for the tree to build.  Browsing
    for folders is also availible for those that prefer it.
    
  - MDX Explorer (PDX Discovery)
    The MDX Explorer is very similar to the tag viewer, with one important 
    difference.  It will check for the needed PDX files for each MDX and see
    if they exist.  This is useful for those sets that just don't sound right
    or seem to be missing some drums.
    
- Tools
  These are various additional tools that are added as requested or needed.
  
  - Hoot > CSV Datafile
    This tool adds artist, company info, and more to a datafile generated for 
    the Hoot Archive.  Pretty specific and only used by the person who has this
    CSV.
    
  - Hoot > XML Builder
    This tool will generate skeleton .xml files for usage with the Hoot music
    player.  It will add all of the tracks from an NSF or GBS file, all you need
    to add is the romset name and game info.  
    
  - NSFE to .m3u
    This tools converts an NSFE to and NSF and .m3u file for use with the more
    frequently updated nezplug++ plugin.  The "Output additional .m3u per track"
    checkbox allows you to pick and choose single tracks to listen to from an
    NSF without skipping around.
    
  - GBS .m3u Builder
    This tool builds an .m3u file for GBS files for use with nezplug++.  It is
    useful for when you have multiple GBS files loaded and winamp's next track 
    function will normally go to the next GBS file, not the next track in the
    current GBS file.  The "Output additional .m3u per track" checkbox allows 
    you to pick and choose single tracks to listen to from a GBS without 
    skipping around.
    
  - xSF > xSF2EXE
    This tool decompresses the compressed data section of an xSF file. 
    
  - xSF > 2sf Ripper
    This tool automates the process of ripping 2sf files from NDS games.  It 
    is pretty self explanatory for those that have performed the process 
    manually.  Rips will be output in the "rips\2sf" subfolder underneath VGMT.
    
    More documentation to come...
    
  - xSF > 2sf Timer
    NOT YET FUNCTIONING, SEE 2SFTIMER ON SOURCEFORGE FOR CURRENT VERSION

  - NDS > SDAT Extractor
    Drag and Drop SDATs onto the box for simple extraction.  Output will be in
    the same folder as the original SDAT in a subdirectory with the same name.
    Currently only extracts the SSEQ and STRM data.  More will be added 
    eventually...

-------
Thanks
-------
Thanks go especially to those people who helped me test these things and work 
with me to find and hopefully fix the bugs (in alphebetical order):

DarkPulse
Knurek
manakoAT

Other thanks go to the format creators, rippers, ripkit makers, and the 
  countless others that contribute.

--------
History
--------
r146 - made readme, don't know the rest