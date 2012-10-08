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

def adjustEdits(view):
    # Add recently edited line to all previous edits, 
    # also joins consecutive edit lines together.
    # Returns: the edited regions or False if there are none.
    edited = view.get_regions("edited_rgns") or []
    edited_last = view.get_regions("edited_rgn") or []
    if not edited and not edited_last:
        return False
    new_edits = []
    edited.extend(edited_last)
    for i, r in enumerate(edited):
        if i > 0 and r.begin() == prev_end:
            new_edits.append(sublime.Region(prev_begin, r.end()))
        else:
            new_edits.append(r)
        prev_begin, prev_end = (r.begin(), r.end())

    view.add_regions("edited_rgns", new_edits, ICONSCOPE, ICON, \
        sublime.HIDDEN | sublime.PERSISTENT)
    view.erase_regions("edited_rgn")
    return view.get_regions("edited_rgns") or []

def showRegion(view, reg):
    view.sel().clear()
    view.show(reg)
    view.sel().add(reg)

class ToggleEditsCommand(sublime_plugin.TextCommand):
    # Toggles outlining of edited lines.
    def run(self, edit):
        window = sublime.active_window()
        view = window.active_view() if window != None else None
        if view is None or view.id() != self.view.id():
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
        window = sublime.active_window()
        view = window.active_view() if window != None else None
        if view is None or view.id() != self.view.id():
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
        window = sublime.active_window()
        view = window.active_view() if window != None else None
        if view is None or view.id() != self.view.id():
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
        window = sublime.active_window()
        view = window.active_view() if window != None else None
        if view is None or view.id() != self.view.id():
            sublime.status_message('Click into the view/tab first.')
            return
        self.vid = self.view.id()
        edited = adjustEdits(self.view)
        if not edited:
            sublime.status_message('No edits to list.')
            return
        the_edits = []
        for i, r in enumerate(edited):
            curr_line, _ = self.view.rowcol(r.begin())
            curr_text = self.view.substr(r).strip()[:40]
            if not len(curr_text):
                curr_text = self.view.substr(self.view.line(r)).strip()[:40] \
                    + " (line)"
            the_edits.append("Line: %03d %s" % ( curr_line + 1, curr_text ))
        window.show_quick_panel(the_edits, self.on_chosen)

    def on_chosen(self, index):
        if index == -1: return
        window = sublime.active_window()
        view = window.active_view() if window != None else None
        if view is None or view.id() != self.vid:
            sublime.status_message('You are in a different view.')
            return
        edited = self.view.get_regions("edited_rgns") or []
        for reg in [r for i, r in enumerate(edited) if i == index]:
            showRegion(self.view, reg)
            break

class CaptureEditing(sublime_plugin.EventListener):
    def on_modified(self, view):
        # Create hidden regions that mirror the edited regions.
        # Maintains a single edit region for the current line.
        window = sublime.active_window()
        curr_view = window.active_view() if window != None else None
        if curr_view is None or curr_view.id() != view.id():
            return
        sel = view.sel()[0]
        currA, currB = (sel.begin(), sel.end())
        self.curr_line, _ = view.rowcol(currA)
        if not hasattr(self, 'prev_line'):
            # on first run
            self.prev_line = self.curr_line
            if currA > 0 and sel.empty():
                same_line, _ = view.rowcol(currA - 1)
                if self.curr_line == same_line:
                    # don't include the newline character from 
                    # the previous line
                    currA -= 1
            self.lastx, self.lasty = (currA, currB)
            self.curr_edit = sublime.Region(self.lastx, self.lasty)
            view.add_regions("edited_rgn",[self.curr_edit], ICONSCOPE, \
                ICON, sublime.HIDDEN | sublime.PERSISTENT)
        elif self.curr_line == self.prev_line:
            # still on the same line
            self.lastx = min(currA, self.lastx)
            self.lasty = max(currB, self.lasty)
            self.curr_edit = sublime.Region(self.lastx, self.lasty)
            view.add_regions("edited_rgn",[self.curr_edit], ICONSCOPE, \
                ICON, sublime.HIDDEN | sublime.PERSISTENT)
        else:
            self.prev_line = self.curr_line
            # moving to a different line
            if currA > 0 and sel.empty():
                same_line, _ = view.rowcol(currA - 1)
                if self.curr_line == same_line:
                    # don't include the newline character from 
                    # the previous line
                    currA -= 1
            self.lastx, self.lasty = (currA, currB)
            _ = adjustEdits(view)