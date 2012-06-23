RubyMotionBuilder for Sublime Text 2
==========================================

This plugin provides some features that simplify RubyMotion developing in Sublime Text 2.

* RubyMotion syntax

	It will work with RubyMotion project related *.rb and Rakefile.
	Code completion and Build system don't work in pure Ruby editing.

* Code completion

	It is same as [RubyMotionSublimeCompletions](https://github.com/diemer/RubyMotionSublimeCompletions).
	The only difference is syntax scope.

* Build system (only work with RubyMotion)

	Provides build system for RubyMotion. Supports three commands, `Build`, `Clean`, `Run` and `Deploy`.
	`Run` kick Terminal.app automatically.

Package Control Installation
----------------------------

**note:** This step requires [Package Control](http://wbond.net/sublime_packages/package_control/installation).

1. Open the Command Palette using **[command + shift + p]** and enter "add repository".
2. Select `Package Control: Add Repository` from the popup menu and press **[return]**
3. Enter "https://github.com/haraken3/SublimeRubyMotionBuilder" to the URL field. 
4. Open the Command Palette using **[command + shift + p]** and enter "install package".
5. Select `Package Control: Install Package` from the popup menu and press **[return]**
6. Enter "SublimeRubyMotionBuilder" and press **[return]**

Manual Installation
------------

Put this package into your Sublime Text 2 packages folder:

* Mac OS X
	
	 ~/Library/Application Support/Sublime Text 2/Packages

* Linux
	
	~/.Sublime Text 2/Packages/

* Windows

	%APPDATA%/Sublime Text 2/Packages/

Usage
-----

### RubyMotion syntax

1. Open *.rb or Rakefile in your RubyMotion project
2. You can see the "RubyMotion" on status bar in right bottom corner. Otherwise, it's not working.

**note:** RubyMotion detection rule is projtect's Rakefile contains "Motion", or not.

### Code completion

1. Inside your RubyMotion project just start typing the name of a method and the autocomplete window will pop up.
2. Press enter/return to trigger the completion.

### Build

1. Open *.rb or Rakefile in your RubyMotion project and enter **[command + b]**.
2. Wait for the console to notify you the message "[Finished]".
3. If you get a error, you can jump to it with press **[F4]**

**note:** Default target is Simulator. If you want to change the target, please edit "RubyMotion.sublime-build".

### Clean

1. Open the Command Palette using **[command + shift + p]** and enter "clean".
2. Select `RubyMotionBuilder: Clean` from the popup menu and press **[return]**
3. Wait for the console to notify you the message "[Finished]".

### Run

1. Open *.rb or Rakefile in your RubyMotion project and enter **[command + r]**.
2. Wait for the Terminal.app will kick Simulator.
3. If you want to modify code and to try again, just re-enter **[command + r]**.
Then, automatically post "quit" to Terminal.app and re-execute "rake".

**note:** `Goto symbol` was assigned to **[control + r]**

### Deploy

1. Open *.rb or Rakefile in your RubyMotion project and enter **[command + option + b]**.
2. Wait for the console to notify you the message "[Finished]".

### Syntax/Completions generator

* `RubyMotionBuilder: Generate syntax` will generate syntax and snippets from Ruby syntax.
* `RubyMotionBuilder: Generate completions` will generate completions from BridgeSupport files of RubyMotion.