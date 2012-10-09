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
another shortcut, via a quick panel.

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
{ "keys": ["ctrl+alt+m"], "command": "list_all_edits" }

Hint: If you highlight an area, press Space then Undo, 
the whole of this area will become a single edit-region!

CURRENT LIMITATIONS:
Undo can cause the previously edited region to be lost 
from the edit history.
Multi-select will only remember the first selection area.