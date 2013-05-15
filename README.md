nscmd
=====
A command-line personal organizer based on python. Meant to be portable and keep
data under a truecrypt volume.

This code is still under development.

### Usage
Type ``?`` to show the list of available commands. Type ``? keyword`` to print
out help on a certain topic.

### Features
  * **truecrypt** Mount a truecrypt volume at start-up and dismount it on exit.
  * **plugins** Commands are loaded dynamically through a plugin mechanism.
  * **almost-multiplatform** Meant for linux, functional under windows.

### Example: On a removable media under windows

Set a directory with the executables you want to make available (e.g., a
portable truecrypt executable). Clone the repository on that folder and call

    python nscmd --volume "%cd:~0,3%\volumes\data.tc" --vol "X:\" --path "%CD%"

The truecrypt file under your removable media ``volumes\data.tc`` will be
mounted on ``X:\`` with the executables on the caller folder available during
execution.

## Command line arguments
Some settings can be overwritten only for a certain run passing them as a
command-line arguments.

    nscmd [-h] [--volume VOLUME] [--vol VOL] [--path PATH [PATH ...]]

  * **VOLUME** Truecrypt volume file.
  * **VOL** Mount point for the volume file.
  * **PATH** Path that will be added to your system ``PATH`` during execution.

## Settings
Settings files follow ``json`` syntax supporting ``//``-like comments. It will
import every file with the extension ``.ns-settings`` found in
``${root}/settings``, with the exception of ``linux.ns-settings`` and  ``windows
.ns-settings`` that will be loaded only on their corresponding  platform.

### Variables
The following variables are available on the settings file.

<table>
<tr>
<td>${home}</td><td>Your home directory.</td>
</tr><tr>
<td>${root}</td><td>Root folder of the app.</td>
</tr><tr>
<td>${vol}</td><td>Mount point of the volume.</td>
</tr><tr>
<td>${data_dir}</td><td>Default folder for data files.</td>
</tr>
</table>

## Plugins
At start-up the application will search for plugins in ``${root}/plugins``
folder. It will try to add every class that inherits from `nsplugin.AppCommand`
found recursively in any ``.py`` or ``.pyc`` file. Plugins are instantiated at
start-up or when `reload_plugins` is called.

A class name in camel case generates a command in underscore case (e.g.,
`DoSomethingCommand` will result in `do_something`).

The following functions are recognized:

  * `run(self[, argv])`
  * `help(self)`
  * `complete_list(self)`
  * `complete(self, text, line, start_index, end_index)`

### Available modules
Apart from every module under `${root}`, two special modules created at run time
are available when the plugins are called.

#### nscmd
<table><tr>
<td>APPNAME</td><td>string</td><td>Name of the application.</td>
</tr><tr>
<td>PLATFORM</td><td>string</td><td>Current platform.</td>
</tr><tr>
<td>ROOT</td><td>string</td><td>Root folder of the app.</td>
</tr><tr>
<td>filter(obj)</td><td>function</td><td>Replace every occurrence of a system variable in obj by its value.</td>
</tr><tr>
<td>get_plugins()</td><td>function</td><td>Return the data loaded from the setting files.</td>
</tr></table>

#### nsplugin
<table><tr>
<td>AppCommand</td><td>class</td><td>Base class for plugin classes.</td>
</tr></table>

## License

nscmd is licensed under the GPL license.

Copyright (C) 2013 N. Subiron

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>
