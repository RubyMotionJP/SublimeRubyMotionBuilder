RubyMotionBuilder for Sublime Text 2 and 3
==========================================

This plugin provides some features that simplify RubyMotion developing in Sublime Text 2 and 3.

* RubyMotion syntax

	It will work with RubyMotion project related \*.rb and Rakefile.
	Code completion and Build system don't work in pure Ruby editing.

* Code completion

	It is same as [RubyMotionSublimeCompletions](https://github.com/diemer/RubyMotionSublimeCompletions).
	The only difference is syntax scope.

* Build system (only work with RubyMotion)

	Provides build system for RubyMotion. Supports four commands, `Build`, `Clean`, `Run` and `Deploy`.
	`Run` kick Terminal.app automatically.

Package Control Installation
----------------------------

**note:** This step requires [Package Control](http://wbond.net/sublime_packages/package_control/installation).

1. Open the Command Palette using [`command` + `shift` + `p`] and enter "install package".
2. Select `Package Control: Install Package` from the popup menu and press [`enter` / `return`]
3. Enter "RubyMotionBuilder" and press [`enter` / `return`]

Manual Installation
------------

Put this package into your Sublime Text 2 or 3 packages folder:

### Mac OS X

* Sublime Text 2
```
% git clone https://github.com/RubyMotionJP/SublimeRubyMotionBuilder.git ~/Library/Application\ Support/Sublime\ Text\ 2/Packages/RubyMotionBuild
```

* Sublime Text 3
```
% git clone https://github.com/RubyMotionJP/SublimeRubyMotionBuilder.git ~/Library/Application\ Support/Sublime\ Text\ 3/Packages/RubyMotionBuild
```


Usage
-----

### RubyMotion syntax

1. Open \*.rb or Rakefile in your RubyMotion project
2. You can see the "RubyMotion" on status bar in right bottom corner. Otherwise, it's not working. If Sublime Text cache keep syntax as "Ruby", please close and open the file.

**note:** RubyMotion detection rule is projtect's Rakefile contains "Motion", or not.

### Code completion

1. Inside your RubyMotion project just start typing the name of a method and the autocomplete window will pop up.
2. Press `enter` / `return` to trigger the completion.

### Build

1. Open \*.rb or Rakefile in your RubyMotion project and press [`command` + `b`].
2. Wait for the console to notify you the message "[Finished]".
3. If you get a error, you can jump to it with press [`F4`]

**note:** Default target is Simulator. If you want to change the target, please edit "RubyMotion.sublime-build".

### Clean

1. Open the Command Palette using [`command` + `shift` + `p`] and press "clean".
2. Select `RubyMotionBuilder: Clean` from the popup menu and press [`enter` / `return`].
3. Wait for the console to notify you the message "[Finished]".

### Run

1. Open \*.rb or Rakefile in your RubyMotion project and press [`command` + `r`]. If you want to enable retina, please press [`shift` + `command` + `r`].
2. Wait for the Terminal.app will kick Simulator.
3. If you want to modify code and to try again, just re-press [`command` + `r`].
Then, automatically post "quit" to Terminal.app and re-execute "rake".

**note:** `Goto symbol` was assigned to [`control` + `r`]

### Run Spec

1. Open \*.rb or Rakefile in your RubyMotion project and press [`command` + `option` + `r`].
2. Wait for the Terminal.app will kick Simulator.
3. If you want to modify code and to try again, just re-press [`command` + `option` + `r`].
Then, automatically post "quit" to Terminal.app and re-execute "rake spec".

### Deploy

1. Open \*.rb or Rakefile in your RubyMotion project and press [`command` + `option` + `b`].
2. Wait for the console to notify you the message "[Finished]".

### Show reference documents using Dash app

1. Open \*.rb or Rakefile in your RubyMotion project.
2. Select a word (like method) and press [`control` + `option` + `d`].

### Syntax/Completions generator

These two commands also supported in Command Pallet.

* `RubyMotionBuilder: Generate syntax` will generate syntax and snippets from Ruby syntax.
* `RubyMotionBuilder: Generate completions` will generate completions from BridgeSupport files of RubyMotion.


Configuration
-----

### Switch Terminal

1. Open \*.rb or Rakefile in your RubyMotion project
2. Open [Sublime Text]->[Preferences]->[Settings - More]->[Syntax Specific - User] in Sublime Text menu.
3. Configure "terminal" setting to switch terminal application to build app. The following settings switch terminal to "iTerm" (By default, "Terminal").

```json
{
	"terminal": "iTerm"
}
```

### Disable to activate Terminal

1. Open \*.rb or Rakefile in your RubyMotion project
2. Open [Sublime Text]->[Preferences]->[Settings - More]->[Syntax Specific - User] in Sublime Text menu.
3. Configure "activate_terminal" setting to disable terminal activation. The following settings disable terminal activation (By default, true).

```json
{
	"activate_terminal": false
}
```
