import sublime
import sublime_plugin
import os.path
import re

this_dir = os.path.split(os.path.abspath(__file__))[0]


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
    # Retuns file path like "Packages/RubyMotionBuild/RubyMotion.tmLanguage"
    path = os.path.join(this_dir, "RubyMotion.tmLanguage")
    path = path.lstrip(os.path.normpath(os.path.join(sublime.packages_path(), "..")))
    return path


class RubyMotionBuild(sublime_plugin.WindowCommand):
    def run(self, build_target=None):
        view = self.window.active_view()
        if not view:
            return
        dir_name = FindRubyMotionRakefile(os.path.split(view.file_name())[0])
        if dir_name:
            sh_name = os.path.join(this_dir, "rubymotion_build.sh")
            cmd = "rake build"
            if build_target and build_target != "all":
                cmd += ":" + build_target

            settings = sublime.load_settings("RubyMotion.sublime-settings")
            env_file = settings.get("rubymotion_build_env_file", "")

            file_regex = "^(...*?):([0-9]*):([0-9]*)"
            self.window.run_command("exec", {"cmd": ["sh", sh_name, cmd, env_file], "working_dir": dir_name, "file_regex": file_regex})


class RubyMotionClean(sublime_plugin.WindowCommand):
    def run(self):
        view = self.window.active_view()
        if not view:
            return
        dir_name = FindRubyMotionRakefile(os.path.split(view.file_name())[0])
        if dir_name:
            sh_name = os.path.join(this_dir, "rubymotion_build.sh")
            cmd = "rake clean"

            settings = sublime.load_settings("RubyMotion.sublime-settings")
            env_file = settings.get("rubymotion_build_env_file", "")

            file_regex = "^(...*?):([0-9]*):([0-9]*)"
            self.window.run_command("exec", {"cmd": ["sh", sh_name, cmd, env_file], "working_dir": dir_name, "file_regex": file_regex})


class RubyMotionRun(sublime_plugin.WindowCommand):
    def run(self, options=""):
        view = self.window.active_view()
        if not view:
            return
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
            self.window.run_command("exec", {"cmd": ["sh", sh_name, dir_name, options], "working_dir": dir_name, "file_regex": file_regex})
            # setting recovery
            settings.set("show_panel_on_build", show_panel_on_build)


class RubyMotionDeploy(sublime_plugin.WindowCommand):
    def run(self):
        view = self.window.active_view()
        if not view:
            return
        dir_name = FindRubyMotionRakefile(os.path.split(view.file_name())[0])
        if dir_name:
            sh_name = os.path.join(this_dir, "rubymotion_build.sh")
            cmd = "rake device"

            settings = sublime.load_settings("RubyMotion.sublime-settings")
            env_file = settings.get("rubymotion_build_env_file", "")

            file_regex = "^(...*?):([0-9]*):([0-9]*)"
            self.window.run_command("exec", {"cmd": ["sh", sh_name, cmd, env_file], "working_dir": dir_name, "file_regex": file_regex})


class GenerateRubyMotionSyntax(sublime_plugin.WindowCommand):
    def run(self):
        rb_name = os.path.join(this_dir, "rubymotion_syntax_generator.rb")
        self.window.run_command("exec", {"cmd": ["ruby", rb_name], "working_dir": this_dir})


class GenerateRubyMotionCompletions(sublime_plugin.WindowCommand):
    def run(self):
        rb_name = os.path.join(this_dir, "rubymotion_completion_generator.rb")
        bridge_support_dir = "/Library/RubyMotion/data/ios/7.0/BridgeSupport/"
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
