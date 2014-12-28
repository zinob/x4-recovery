x4-recovery
===========
**As of yet this is just a very crude read-only FAT32 module in python created via explorative programing.**

The goal of this program is to be able to recover films from memory card disk-dumps of the Hubsan X4 HD.

The Hubsan X4 HD have an aggravating bug of just creating a 4KiB AVI file with no useful content if
the power to the quad is cut before the user presses the "stop recording button" on the quad. This might either happen if the user forgets to press the button prior to disconnecting power or in the event of a hard landing.

This is touted as a feature in the manual, so go figure.

This is an attempt at seeing if it is possible to reconstruct the file by re-pointing the FAT
and possibly re-creating the AVI (RIFF)-header

Sources:
-----
* [Paul Stoffregen - Understanding FAT32 Filesystems](https://www.pjrc.com/tech/8051/ide/fat32.html)
* [Microsoft - FAT: General Overview of On-Disk Format](http://staff.washington.edu/dittrich/misc/fatgen103.pdf)
* https://github.com/mk-fg/fgtk/blob/master/desktop/vfat_shuffler
* [Microsoft - AVI RIFF File Reference](http://msdn.microsoft.com/en-us/library/ms779636.aspx)