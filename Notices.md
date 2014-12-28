A short essay on my thoughts when starting this attempt at data recovery.
====

I have a recording that I HOPE have some nice footage. Alas the Hubsan X4s camera wont write the file to the SD-card unless you press the start/stop button prior to disconnecting the power, and I made a way to hard\*1 landing resulting in the camera module glitching out and deffinetley not feeling like writing the file.


I don't think all data is lost how ever!
During normal operation it takes less than a second from that you press
"stop recording" until the red "working...light" goes out. So apart from the
fact that it wouldn't make economical sense to have enough RAM in the
camera-module to buffer a 10 minute recording it would also be impossible to
write the data to the card in less a few minutes so (much) of the data
should already have been saved to the card.

Before I plug the card into a Windows computer I take a disk-dump from my
Slackware,this is usually a good first-step.
Slackware is user-unfriendly (though not hostile) in many ways, the most
prominent probably being that it doesn't do _anything_ automatically. Luckily the tings it usually wont do without being explicitly told are "auto mounting-USB-file-systems and fixing errors".

When browsing the file-system on windows it looks like the file PICT0003.AVI is just 4kB, damaged and contains no data, but what does the pre-built Linux tools have to say about The State Of The Disk?
We ask the file-system-checker ``` fsck``` to look but not touch: /sbin/fsck.vfat -n sdcard.dd

```
0x41: Dirty bit is set. Fs was not properly unmounted and some data may be corrupt.
 Automatically removing dirty bit.
/DCIM/100DSCIM/PICT0003.AVI
  File size is 2048 bytes, cluster chain length is > 32768 bytes.
  Truncating file to 2048 bytes.
Reclaimed 3995 unused clusters (130908160 bytes).
Free cluster summary wrong (485931 vs. really 485749)
  Auto-correcting.
Leaving filesystem unchanged.

```

The interesting part here is *File size is 2048 bytes, cluster chain length is > 32768 bytes.* and *Reclaimed 3995 (130908160 bytes).*

What this tells us is that the catalog info says that the file is just 2[KiB](http://en.wikipedia.org/wiki/Kibibyte), but that there is "more than 32768 bytes associated with it".
The part about *Reclaimed 130 908 160 bytes* is a mixed blessing, it tells us that there is about a 124[MiB](http://en.wikipedia.org/wiki/MebibytE) that the file system tells uss is unneccesary. A back-of-the-envelope calculation tells me that this is about minute of recording, which is less than I hoped for, but there is at least __something__ to be salvage.

I start by firing up [HxD](http://mh-nexus.de/en/hxd/) on the raw-device, I have done similar things before... on 1.44 floppies. It turns out that it is not quite so convenient to manually calculate addresses and browse file-allocation tables for disks which are more than a million times as big. So I guess that we need a programmatic solution.

ONWARDS, to Python and greater glory!

___
\*1
To hard as in flying stupidly high, losing control, hitting emergency shutdown and impacting the asphalt with [terminal-velocity](http://en.wikipedia.org/wiki/Terminal_velocity) kind of landing. __All__ the little impact absorbing snaps sprung, but the quad does seem to be OK after resetting them. As much as the Hubsan X4 feels a bit cheap with its not-ever-quite-perfect-trim and its plasticly look there is no denying that the no-frills approach helps keep the weight, and thus the terminal velocity down and the plastic is surprisingly durable.
