import os.path
import subprocess
import sublime
import sublime_plugin
import codecs
import re
import time
import glob

this_dir = os.path.split(os.path.abspath(__file__))[0]

def SaveAllFiles():
    for window in sublime.windows():
        for view in window.views():
            if view.file_name() and view.is_dirty():
                view.run_command("save")

def FindRubyMotionRakefile(dir_name):
    re_rubymotion = re.compile("Motion")
    while dir_name != "/":
        rakefile = os.path.join(dir_name, "Rakefile")
        if os.path.isfile(rakefile):
            for line in codecs.open(rakefile, "r", "utf-8"):
                if re_rubymotion.search(line):
                    return dir_name
            return None
        dir_name = os.path.dirname(dir_name)
    return None

def GetProjectRootDirectory():
    dir_name = FindRubyMotionRakefile(os.path.split(sublime.active_window().active_view().file_name())[0])
    if dir_name:
        return dir_name
    for view in sublime.active_window().views():
        if view.settings().get('syntax').endswith('RubyMotion.tmLanguage'):
            if view.file_name():
                dir_name = FindRubyMotionRakefile(os.path.split(view.file_name())[0])
                if dir_name:
                    return dir_name
    return None

def GetLanguageFilePath():
    path = os.path.join(this_dir, "RubyMotion.tmLanguage")
    if sublime.version() >= '3000':
        # Retuns file path like "Packages/RubyMotionBuild/RubyMotion.tmLanguage" for Sublime 3
        path = path.lstrip(os.path.normpath(os.path.join(sublime.packages_path(), "..")))
    return path

def GetTaskListWithRake(root_dir):
    cmd = "rake -T"
    if os.path.isfile(os.path.join(root_dir, "Gemfile")):
        cmd = "bundle exec rake -T"
    p = subprocess.Popen(cmd, shell=True, cwd=root_dir,
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=None,
        close_fds=True)
    output = p.stdout.read()
    tmp = output.decode("utf-8").split("\n")
    list = []
    for item in tmp:
        if item.startswith("rake"):
            list.append(item)
    return list

def GetTaskListFromCache(cache_path):
    return open(cache_path).readlines()

def SaveTaskListToCache(data, cache_path):
    f = open(cache_path, 'w')
    for item in data:
        f.write(item + "\n")
    f.close()

def GetTaskList(root_dir):
    cache_path = os.path.join(root_dir, ".sublime_cache_tasklist")
    rakefile_path = os.path.join(root_dir, "Rakefile")
    gemfile_path = os.path.join(root_dir, "Gemfile")
    time_rakefile = time_gemfile = time_cachefile = 0

    if os.path.isfile(cache_path):
        time_cachefile = os.stat(cache_path).st_mtime
    if os.path.isfile(rakefile_path):
        time_rakefile = os.stat(rakefile_path).st_mtime
    if os.path.isfile(gemfile_path):
        time_gemfile = os.stat(gemfile_path).st_mtime

    if (time_cachefile < time_rakefile) or (time_cachefile < time_gemfile):
        list = GetTaskListWithRake(root_dir)
        SaveTaskListToCache(list, cache_path)
    else:
        list = GetTaskListFromCache(cache_path)

    return list

def RunRubyMotionBuildScript(self, cmd):
    dir_name = GetProjectRootDirectory()
    if not dir_name:
        return
    view = self.window.active_view()
    if view.settings().get("auto_save", True):
        SaveAllFiles()
    sh_name = os.path.join(this_dir, "rubymotion_build.sh")
    settings = sublime.load_settings("RubyMotion.sublime-settings")
    file_regex = "^(...*?):([0-9]*):([0-9]*)"
    self.window.run_command("exec", {"cmd": ["sh", sh_name, cmd], "working_dir": dir_name, "file_regex": file_regex})

def RunRubyMotionRunScript(self, options):
    dir_name = GetProjectRootDirectory()
    if not dir_name:
        return
    view = self.window.active_view()
    if view.settings().get("auto_save", True):
        SaveAllFiles()
    sh_name = os.path.join(this_dir, "rubymotion_run.sh")
    file_regex = "^(...*?):([0-9]*):([0-9]*)"
    # build console is not required for Run
    self.window.run_command("hide_panel", {"panel": "output.exec"})
    settings = sublime.load_settings("Preferences.sublime-settings")
    show_panel_on_build = settings.get("show_panel_on_build", True)
    if show_panel_on_build:
        # temporary setting to keep console visibility
        settings.set("show_panel_on_build", False)
    terminal = view.settings().get("terminal", "Terminal")
    activate_terminal = view.settings().get("activate_terminal", True)
    activate_terminal = "true" if activate_terminal else "false"
    self.window.run_command("exec", {"cmd": ["sh", sh_name, terminal, activate_terminal, dir_name, options], "working_dir": dir_name, "file_regex": file_regex})
    # setting recovery
    settings.set("show_panel_on_build", show_panel_on_build)


class RubyMotionBuild(sublime_plugin.WindowCommand):
    def run(self):
        RunRubyMotionBuildScript(self, "rake build")


class RubyMotionClean(sublime_plugin.WindowCommand):
    def run(self):
        RunRubyMotionBuildScript(self, "rake clean")


class RubyMotionRun(sublime_plugin.WindowCommand):
    def run(self, options=""):
        RunRubyMotionRunScript(self, options)


class RubyMotionRunSpec(sublime_plugin.WindowCommand):
    def run(self, options=""):
        RunRubyMotionRunScript(self, "spec")


class RubyMotionDeploy(sublime_plugin.WindowCommand):
    def run(self):
        RunRubyMotionRunScript(self, "device")


class RubyMotionRunCommandFromList(sublime_plugin.WindowCommand):
    def run(self):
        dir_name = GetProjectRootDirectory()
        if not dir_name:
            return
        self.task_list = GetTaskList(dir_name)
        self.window.show_quick_panel(self.task_list, self.on_done, sublime.MONOSPACE_FONT)

    def on_done(self, picked):
        if picked < 0:
            return
        pickup_task = re.compile('rake ([\w:]+)')
        task = pickup_task.match(self.task_list[picked]).group(1) 
        RunRubyMotionRunScript(self, task)


class RubyMotionSetBreakpoint(sublime_plugin.WindowCommand):
    def run(self):
        view = self.window.active_view()
        view_file_name = view.file_name()
        if not view_file_name:
            return
        line, _ = view.rowcol(view.sel()[0].begin())
        line = line + 1
        dir_name, file_name = os.path.split(view_file_name)
        dir_name = FindRubyMotionRakefile(dir_name)
        breakpoint = "b %s:%d\n" % (file_name, line)
        io = open("%s/debugger_cmds" % dir_name, 'a')
        io.write(breakpoint)
        io.close()
        sublime.message_dialog("Set Breakpoint in debugger_cmds:\n\n  " + breakpoint)


class RubyMotionDoc(sublime_plugin.WindowCommand):
    def run(self):
        view = self.window.active_view()
        selection = view.sel()[0]
        word = view.substr(selection)
        subprocess.call(["open", "dash://%s" % word])


class GenerateRubyMotionCompletions(sublime_plugin.WindowCommand):
    def run(self):
        self.dirs = glob.glob('/Library/RubyMotion/data/ios/*/BridgeSupport/')
        self.dirs.extend(glob.glob('/Library/RubyMotion/data/tvos/*/BridgeSupport/'))
        self.dirs.extend(glob.glob('/Library/RubyMotion/data/watchos/*/BridgeSupport/'))
        self.dirs.extend(glob.glob('/Library/RubyMotion/data/osx/*/BridgeSupport/'))
        self.dirs.extend(glob.glob('/Library/RubyMotionPre/data/android/*/BridgeSupport/'))
        self.window.show_quick_panel(self.dirs, self.on_done)

    def on_done(self, picked):
        if picked < 0:
            return
        rb_name = os.path.join(this_dir, "rubymotion_completion_generator.rb")
        bridge_support_dir = self.dirs[picked]
        self.window.run_command("exec", {"cmd": ["ruby", rb_name, bridge_support_dir], "working_dir": this_dir})


class SetRubyMotionSyntax(sublime_plugin.EventListener):
    def set_rubymotion_syntax(self, view):
        view_file_name = view.file_name()
        if view_file_name:
            dir_name, file_name = os.path.split(view_file_name)
            ext = os.path.splitext(file_name)[1]
            if ext == ".rb" or file_name == "Rakefile":
                if FindRubyMotionRakefile(dir_name):
                    view.set_syntax_file(GetLanguageFilePath())

    def on_load(self, view):
        self.set_rubymotion_syntax(view)

    def on_pre_save(self, view):
        self.set_rubymotion_syntax(view)


#####################################################
# https://github.com/alienhard/SublimeAllAutocomplete
#####################################################
# limits to prevent bogging down the system
MIN_WORD_SIZE = 3
MAX_WORD_SIZE = 50

MAX_VIEWS = 20
MAX_WORDS_PER_VIEW = 100
MAX_FIX_TIME_SECS_PER_VIEW = 0.01

class RubyMotionAutocomplete(sublime_plugin.EventListener):

    def on_query_completions(self, view, prefix, locations):
        if not view.settings().get('syntax').endswith('RubyMotion.tmLanguage'):
            return

        words = []
        # Limit number of views but always include the active view. This
        # view goes first to prioritize matches close to cursor position.
        other_views = [v for v in sublime.active_window().views() if v.id != view.id]
        views = [view] + other_views
        views = views[0:MAX_VIEWS]

        for v in views:
            if len(locations) > 0 and v.id == view.id:
                view_words = v.extract_completions(prefix, locations[0])
            else:
                view_words = v.extract_completions(prefix)
            view_words = filter_words(view_words)
            view_words = fix_truncation(v, view_words)
            words += view_words

        words = without_duplicates(words)
        matches = [(w, w.replace('$', '\\$')) for w in words]
        return matches

def filter_words(words):
    words = words[0:MAX_WORDS_PER_VIEW]
    return [w for w in words if MIN_WORD_SIZE <= len(w) <= MAX_WORD_SIZE]

# keeps first instance of every word and retains the original order
# (n^2 but should not be a problem as len(words) <= MAX_VIEWS*MAX_WORDS_PER_VIEW)
def without_duplicates(words):
    result = []
    for w in words:
        if w not in result:
            result.append(w)
    return result


# Ugly workaround for truncation bug in Sublime when using view.extract_completions()
# in some types of files.
def fix_truncation(view, words):
    fixed_words = []
    start_time = time.time()

    for i, w in enumerate(words):
        #The word is truncated if and only if it cannot be found with a word boundary before and after

        # this fails to match strings with trailing non-alpha chars, like
        # 'foo?' or 'bar!', which are common for instance in Ruby.
        match = view.find(r'\b' + re.escape(w) + r'\b', 0)
        truncated = is_empty_match(match)
        if truncated:
            #Truncation is always by a single character, so we extend the word by one word character before a word boundary
            extended_words = []
            view.find_all(r'\b' + re.escape(w) + r'\w\b', 0, "$0", extended_words)
            if len(extended_words) > 0:
                fixed_words += extended_words
            else:
                # to compensate for the missing match problem mentioned above, just
                # use the old word if we didn't find any extended matches
                fixed_words.append(w)
        else:
            #Pass through non-truncated words
            fixed_words.append(w)

        # if too much time is spent in here, bail out,
        # and don't bother fixing the remaining words
        if time.time() - start_time > MAX_FIX_TIME_SECS_PER_VIEW:
            return fixed_words + words[i+1:]

    return fixed_words

if sublime.version() >= '3000':
  def is_empty_match(match):
    return match.empty()
else:
  def is_empty_match(match):
    return match is None