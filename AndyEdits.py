import sublime, sublime_plugin
from os import path

PACKAGE_SETTINGS = "AndyEdits.sublime-settings"
if sublime.platform() == "linux":
    # Try and load Linux Python2.6 lib.  Default path is for Ubuntu.
    linux_lib = sublime.load_settings(PACKAGE_SETTINGS).get("linux_python2.6_lib",
        "/usr/lib/python2.6/lib-dynload")
    if not linux_lib in sys.path and path.exists(linux_lib):
        sys.path.append(linux_lib)

ICON = path.pardir + '/AndyEdits/icon' if \
    sublime.load_settings(PACKAGE_SETTINGS).get("use_icon", True) else ""
# a small icon to appear in the gutter - defaults to true
# (may interfere with ST-bookmarks)
ICONSCOPE = sublime.load_settings(PACKAGE_SETTINGS).get("icon_scope", "comment")
# affects the colour of the gutter icon and outlining

def showRegion(view, reg):
    view.sel().clear()
    view.show(reg)
    view.sel().add(reg)

def sameView(view_id):
    if not view_id: return False
    window = sublime.active_window()
    view = window.active_view() if window != None else None
    return (view is not None and view.id() == view_id)

def adjustEdits(view):
    # Add recently edited line to all previous edits, 
    # also joins consecutive edit lines together.
    # Returns: the edited regions or False if there are none.
    edited = view.get_regions("edited_rgns") or []
    edited_last = view.get_regions("edited_rgn") or []
    if not edited and not edited_last:
        return False
    new_edits = []
    if edited_last:
        edited.extend(edited_last)
    for i, r in enumerate(edited):
        if i > 0 and r.begin() == prev_end + 1:
            # collapse adjoining regions
            new_edits.append(sublime.Region(prev_begin, r.end()))
        else:
            new_edits.append(r)
        prev_begin, prev_end = (r.begin(), r.end())

    view.add_regions("edited_rgns", new_edits, ICONSCOPE, ICON, \
        sublime.HIDDEN | sublime.PERSISTENT)
    # view.erase_regions("edited_rgn")
    return view.get_regions("edited_rgns") or []

def getEditList(view, edited):
    the_edits = []
    for i, r in enumerate(edited):
        curr_line, _ = view.rowcol(r.begin())
        curr_text = view.substr(r).strip()[:40]
        if not len(curr_text):
            curr_text = view.substr(view.line(r)).strip()[:40] + " (line)"
        the_edits.append("Line: %03d %s" % ( curr_line + 1, curr_text ))
    return the_edits

def getFullEditList(view, edited):
    the_edits = []
    locations = []
    for i, r in enumerate(edited):
        curr_line, _ = view.rowcol(r.begin())
        curr_text = view.substr(r).strip()[:40]
        if not len(curr_text):
            curr_text = view.substr(view.line(r)).strip()[:40] + " (line)"
        the_edits.append("    Line: %03d %s" % ( curr_line + 1, curr_text ))
        locations.append((view, r))
    return the_edits, locations

class ListAllEdits(sublime_plugin.WindowCommand):
    def run(self):
        adjustEdits(self.window.active_view())
        full_list = []
        self.locations = []
        for vw in self.window.views():
            edited = vw.get_regions("edited_rgns") or []
            if edited:
                the_edits, locs = getFullEditList(vw, edited)
                if the_edits:
                    the_edits.insert(0, "%s" % (vw.file_name() or "No filename"))
                    locs.insert(0, (vw, sublime.Region(0, 0)))
                    full_list += the_edits
                    self.locations += locs
        if full_list:
            self.window.show_quick_panel(full_list, self.on_chosen)
        else:
            sublime.status_message('No edits to list.')

    def on_chosen(self, index):
        if index == -1: return
        vw, reg = self.locations[index]
        sublime.active_window().focus_view(vw)
        showRegion(vw, reg)

class ToggleEditsCommand(sublime_plugin.TextCommand):
    # Toggles outlining of edited lines.
    def run(self, edit):
        if not sameView(self.view.id()):
            sublime.status_message('Click into the view/tab first.')
            return
        edited = adjustEdits(self.view)
        if not edited:
            sublime.status_message('No edits to show or hide.')
            return
        toggled = self.view.get_regions("toggled_edits") or []
        if toggled:
            self.view.erase_regions("toggled_edits")
        else:
            self.view.add_regions("toggled_edits", edited, ICONSCOPE, \
                ICON, sublime.DRAW_OUTLINED)

class PrevEditLineCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        if not sameView(self.view.id()):
            sublime.status_message('Click into the view/tab first.')
            return
        currA = self.view.sel()[0].begin()
        edited = adjustEdits(self.view)
        if not edited:
            sublime.status_message('No edits to go to.')
            return
        for reg in [r for r in reversed(edited) if r.begin() < currA]:
            showRegion(self.view, reg)
            break
        else:
            sublime.status_message('No edits further up.')

class NextEditLineCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        if not sameView(self.view.id()):
            sublime.status_message('Click into the view/tab first.')
            return
        currA = self.view.sel()[0].begin()
        edited = adjustEdits(self.view)
        if not edited:
            sublime.status_message('No edits to go to.')
            return
        for reg in [r for r in edited if r.begin() > currA]:
            showRegion(self.view, reg)
            break
        else:
            sublime.status_message('No edits further down.')

class QuickEditsCommand(sublime_plugin.TextCommand):
    # Shows a quick panel to jump to edit lines.
    def run(self, edit):
        self.vid = self.view.id()
        if not sameView(self.vid):
            sublime.status_message('Click into the view/tab first.')
            return
        edited = adjustEdits(self.view)
        if not edited:
            sublime.status_message('No edits to list.')
            return
        the_edits = getEditList(self.view, edited)
        if the_edits:
            sublime.active_window().show_quick_panel(the_edits, self.on_chosen)

    def on_chosen(self, index):
        if index == -1: return
        if not sameView(self.vid):
            sublime.status_message('You are in a different view.')
            return
        edited = self.view.get_regions("edited_rgns") or []
        for reg in [r for i, r in enumerate(edited) if i == index]:
            showRegion(self.view, reg)
            break

class DeleteEditCommand(sublime_plugin.TextCommand):
    # Shows a quick panel to remove edit history for a region.
    def run(self, edit):
        self.vid = self.view.id()
        if not sameView(self.vid):
            sublime.status_message('Click into the view/tab first.')
            return
        edited = adjustEdits(self.view)
        if not edited:
            sublime.status_message('No edit history to delete.')
            return
        the_edits = getEditList(self.view, edited)
        if the_edits:
            sublime.active_window().show_quick_panel(the_edits, self.on_chosen)

    def removeTempHighlight(self, old_line):
        self.view.erase_regions("temp_del")
        sublime.status_message("Edit history removed from line %d." % old_line)

    def on_chosen(self, index):
        if index == -1: return
        if not sameView(self.vid):
            sublime.status_message('You are in a different view.')
            return
        edited = self.view.get_regions("edited_rgns") or []
        reg = edited[index]
        del edited[index]
        self.view.add_regions("edited_rgns", edited, ICONSCOPE, ICON, \
            sublime.HIDDEN | sublime.PERSISTENT)
        is_toggled = self.view.get_regions("toggled_edits") or []
        if is_toggled:
            self.view.erase_regions("toggled_edits")
            sublime.active_window().run_command("toggle_edits")
        old_line, _ = self.view.rowcol(reg.begin())
        self.view.add_regions("temp_del", [reg], "invalid", sublime.DRAW_OUTLINED)
        sublime.set_timeout(lambda: self.removeTempHighlight(old_line + 1), 500)

class CaptureEditing(sublime_plugin.EventListener):
    def on_modified(self, view):
        # Create hidden regions that mirror the edited regions.
        # Maintains a single edit region for the current line.
        if not sameView(view.id()):
            # maybe using Find? etc.
            window = sublime.active_window()
            edit_view = window.active_view() if window != None else None
            _ = adjustEdits(edit_view)
            return
        sel = view.sel()[0]
        currA, currB = (sel.begin(), sel.end())
        self.curr_line, _ = view.rowcol(currA)
        if not hasattr(self, 'prev_line'):
            # on first run
            self.prev_line = self.curr_line
            if currA > 0 and sel.empty():
                # include the first character?
                same_line, _ = view.rowcol(currA - 1)
                if self.curr_line == same_line:
                    currA -= 1
            self.lastx, self.lasty = (currA, currB)
        elif self.curr_line == self.prev_line:
            # still on the same line
            self.lastx = min(currA, self.lastx)
            # don't go beyond end of current line..
            self.lasty = max(currB, min(self.lasty, view.line(sel).end()))
        else:
            # moving to a different line
            self.prev_line = self.curr_line
            if currA > 0 and sel.empty():
                # include the first character?
                same_line, _ = view.rowcol(currA - 1)
                if self.curr_line == same_line:
                    currA -= 1
            self.lastx, self.lasty = (currA, currB)
            _ = adjustEdits(view)
        curr_edit = sublime.Region(self.lastx, self.lasty)
        view.add_regions("edited_rgn", [curr_edit], ICONSCOPE, \
            ICON, sublime.HIDDEN | sublime.PERSISTENT)

    def on_selection_modified(self, view):
        if hasattr(self, 'prev_line'):
            curr_line, _ = view.rowcol(view.sel()[0].begin())
            if self.prev_line != curr_line:
                found_line = False
                edited = view.get_regions('edited_rgns') or []
                for i, r in enumerate(edited):
                    the_line, _ = view.rowcol(r.begin())
                    last_line, _ = view.rowcol(r.end())
                    if the_line <= self.prev_line <= last_line:
                        found_line = True
                        break
                if not found_line:
                    start = end = view.text_point(self.prev_line, 0)
                    edited.append(sublime.Region(start, end))
                    view.add_regions("edited_rgns", edited, ICONSCOPE, \
                        ICON, sublime.HIDDEN | sublime.PERSISTENT)

