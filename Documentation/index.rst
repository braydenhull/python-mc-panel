.. PMCP master file, created 04/06/2014 9:53 PM

Welcome! This is Python MC Panel's Documentation
================================================

Python MC Panel is a Minecraft control panel written in Python.

Features
--------

- Support for Bukkit and Vanilla Minecraft

- Full provisioning of the server

- Process management which can keep the Minecraft instances up, even in the event of a web panel crash (courtesy of .. _Supervisor: http://supervisord.org/

- Built in backup feature, which supports Tar compression (defaults to gzip) and Zip compression

- Support for multiple Minecraft instances in the one panel

- Console support, utilising websockets so that it is more responsive and less bandwidth intensive

- Player management including bans, kicks and setting operators (supports old-style one name per line, pipe separated and the fancy JSON format)

To Do
-----

- JSON API utilising an API key for majority of functionality available, documented on this here Sphinx installation

- Upgrading/downgrading memory allocations, etc. at the moment it is not possible to do this without modifying the database and Supervisor config files

- Complete backup support for possibility of remote backups, etc.

- Possibly ACLs or at least some basic permissions system

- Plugin installation/remove and possibly management

- Troubleshooting actions to assist users when seeking help (for instance auto clearing log, rebooting server and then uploading captured results to Pastebin)

- Completing backup support

- Investigating Windows support (unlikely)

- Possible WHMCS module for use by GSPs


.. toctree::
    :maxdepth 2

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
