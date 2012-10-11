AndyEdits
=========

Jump between edited regions - optional gutter icon

Can jump to next or previous edited-lines or use a 
quick-panel which shows the edited text and line number. 
(If the edited text is just whitespace then the panel 
will display the full line's text.)

A shortcut can toggle outlining of the edited lines. 
An optional icon can appear in the gutter - although 
this may interfere if you also use Bookmarks. You 
could use your own icon if you prefer! icon_scope 
determines the colour of the icon and outlining: 
"class" works well for me.

You can remove the edit history for a region using 
another shortcut, via a quick panel (although you 
cannot remove the most recent edit). If you highlight 
some text you can create/add it as an edit-region.

You can list, and jump to, edits across all open files.

Details for edited lines will persist if you close ST, 
but not if you close the file/view. This is the 
default persistence behaviour for ST.

My suggestions for your Key Bindings (User) are:
{ "keys": ["ctrl+alt+d"], "command": "delete_edit" },
{ "keys": ["ctrl+alt+h"], "command": "toggle_edits" },
{ "keys": ["ctrl+alt+j"], "command": "quick_edits" },
{ "keys": ["ctrl+alt+k"], "command": "prev_edit_line" },
{ "keys": ["ctrl+alt+l"], "command": "next_edit_line" },
{ "keys": ["ctrl+alt+m"], "command": "list_all_edits" },
{ "keys": ["ctrl+alt+c"], "command": "create_edit" }

CURRENT LIMITATIONS:
Pressing Undo repeatedly may leave an area as an edit-region, 
even though you have undone all edits to this region. Being 
able to create and remove edit regions can help with this issue.

Multi-select will only remember the first selection area.

It doesn't include automatically inserted tabs, matched brackets
or quotes within the current edit region. Therefore, the edit-region
may be split into several edits, and/or the region may end before it
should. What I'm doing is pressing Ctrl-Alt-H (or using my shortcut
menu) to toggle highlighting of the edits. Regardless of this
highlighting step, I can select the whole area and use Ctrl-Alt-C 
to define it as a single edit-region. I can do this at any time 
and it has the advantage that I can explicitly define the start 
and end points of the edit region.
