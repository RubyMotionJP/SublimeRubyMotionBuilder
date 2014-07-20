import os.path
import subprocess
import sublime
import sublime_plugin
import re
import glob

this_dir = os.path.split(os.path.abspath(__file__))[0]
env_path = os.environ["PATH"]

def SaveAllFiles():
    for window in sublime.windows():
        for view in window.views():
            if view.file_name():
                if view.is_dirty():
                    view.run_command("save")

def FindRubyMotionRakefile(dir_name):
    re_rubymotion = re.compile("Motion")
    while dir_name != "/":
        rakefile = os.path.join(dir_name, "Rakefile")
        if os.path.isfile(rakefile):
            for line in open(rakefile):
                if re_rubymotion.search(line):
                    return dir_name
            return None
        dir_name = os.path.dirname(dir_name)
    return None

def GetLanguageFilePath():
    path = os.path.join(this_dir, "RubyMotion.tmLanguage")
    if int(sublime.version()) // 1000 == 3:
        # Retuns file path like "Packages/RubyMotionBuild/RubyMotion.tmLanguage" for Sublime 3
        path = path.lstrip(os.path.normpath(os.path.join(sublime.packages_path(), "..")))
    return path

def RunRubyMotionBuildScript(self, build_target, cmd):
    view = self.window.active_view()
    if not view:
        return
    if view.settings().get("auto_save", True):
        SaveAllFiles()
    dir_name = FindRubyMotionRakefile(os.path.split(view.file_name())[0])
    if dir_name:
        sh_name = os.path.join(this_dir, "rubymotion_build.sh")
        if build_target and build_target != "all":
            cmd += ":" + build_target

        settings = sublime.load_settings("RubyMotion.sublime-settings")
        env_file = settings.get("rubymotion_build_env_file", "")

        file_regex = "^(...*?):([0-9]*):([0-9]*)"
        self.window.run_command("exec", {"cmd": ["sh", sh_name, env_path, cmd, env_file], "working_dir": dir_name, "file_regex": file_regex})


def RunRubyMotionRunScript(self, options):
    view = self.window.active_view()
    if not view:
        return
    if view.settings().get("auto_save", True):
        SaveAllFiles()
    dir_name = FindRubyMotionRakefile(os.path.split(view.file_name())[0])
    if dir_name:
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
        self.window.run_command("exec", {"cmd": ["sh", sh_name, env_path, terminal, activate_terminal, dir_name, options], "working_dir": dir_name, "file_regex": file_regex})
        # setting recovery
        settings.set("show_panel_on_build", show_panel_on_build)


class RubyMotionBuild(sublime_plugin.WindowCommand):
    def run(self, build_target=None):
        RunRubyMotionBuildScript(self, build_target, "rake build")


class RubyMotionClean(sublime_plugin.WindowCommand):
    def run(self):
        RunRubyMotionBuildScript(self, None, "rake clean")


class RubyMotionRun(sublime_plugin.WindowCommand):
    def run(self, options=""):
        RunRubyMotionRunScript(self, options)


class RubyMotionRunSpec(sublime_plugin.WindowCommand):
    def run(self, options=""):
        RunRubyMotionRunScript(self, "spec")


class RubyMotionDeploy(sublime_plugin.WindowCommand):
    def run(self):
        RunRubyMotionRunScript(self, "device")


class RubyMotionDoc(sublime_plugin.WindowCommand):
    def run(self):
        view = self.window.active_view()
        selection = view.sel()[0]
        word = view.substr(selection)
        subprocess.call(["open", "dash://%s" % word])


class GenerateRubyMotionCompletions(sublime_plugin.WindowCommand):
    def run(self):
        self.dirs = glob.glob('/Library/RubyMotion/data/ios/*/BridgeSupport/')
        self.dirs.extend(glob.glob('/Library/RubyMotion/data/osx/*/BridgeSupport/'))
        self.window.show_quick_panel(self.dirs, self.on_done)

    def on_done(self, picked):
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
