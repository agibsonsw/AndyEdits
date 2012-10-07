AndyEdits
=========

Jump between edited lines - optional gutter icon

Can jump to next or previous edited-lines or use a 
quick-panel which shows the edited text and line number. 
(If the editing text is just whitespace then the panel 
will display the full line's text.)

A shortcut can toggle outlining of the edited lines. 
An optional icon can appear in the gutter - although 
this may interfere if you also use Bookmarks. You 
could use your own icon if you prefer!

Details for edited lines will persist if you close ST, 
but not if you close the file/view. This is the 
default persistence behaviour for ST.

My suggestions for your Key Bindings (User) are:

{ "keys": ["ctrl+alt+h"], "command": "toggle_edits" },
{ "keys": ["ctrl+alt+j"], "command": "quick_edits" },
{ "keys": ["ctrl+alt+k"], "command": "prev_edit_line" },
{ "keys": ["ctrl+alt+l"], "command": "next_edit_line" }