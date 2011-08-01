Smuggler
=====

*Smuggler is currently in alpha release and should be treated as such. It may contain catastrophic errors and/or bugs that may make it unusable at any given point in time.*

Smuggler is an application that is designed with the goal of keeping your local image collection and the images on your SmugMug account in sync. Simply it is designed to make the process of keeping everything in sync much simpler and automate as much as possible. It is designed to has a web interface to allow you to run it either from your local system, or to install it on your system with the images and then manage it from another system. It should be fairly flexible.

Features Currently Implemented:

* Identifies images on local machine
* Identifies images on SmugMug
* Reporting features to identify potential sync issues such as:
	- Local Albums that are in different category or sub-category than found on SmugMug
	- Local Images that are identical to images on SmugMug, but have different filenames
	- Duplicate Images within a local album
	- Duplicate Images within a SmugMug album
* Reporting feature to identify albums that are found on SmugMug but not found locally 
* Reporting feature to identify albums that are found locally but not found on SmugMug
* Reporting feature to identify images that were found in a previous scan that were not found during the latest scan

You can see a the list of features planned to implemented by checking out the [milestones][milestones]. The short list is below:

* Web Interface
* Upload images missing from SmugMug (will create any needed albums)
* Download images missing from the local set of images

##
Other Projects

Smuggler makes use of the following projects:

* [ConfigObj 4][ConfigObj 4]
* [smugpy][smugpy]

## 
Dependencies

Smuggler has only been tested with Python 2.7 at this current stage, so that is what is recommended.

##
Bugs

If you find a bug please report it or it'll never get fixed. Verify that it hasn't [already been submitted][issues] and then [log a new bug][newissue]. Be sure to provide as much information as possible.

[milestones]: https://github.com/jkschoen/Smuggler/issues/milestones
[issues]: https://github.com/jkschoen/Smuggler/issues?milestone=&labels=
[newissue]: https://github.com/jkschoen/Smuggler/issues/new
[ConfigObj 4]: http://www.voidspace.org.uk/python/configobj.html
[smugpy]: https://github.com/chrishoffman/smugpy