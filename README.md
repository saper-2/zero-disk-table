# ZDT - Zero Disk Table
This script has been created for purpouse of wiping MBR/GPT partition table from disk.

With MBR it's easy, just erase few first sectors of disk and you're ready to go. 

But GPT is a more pain. GPT partition table is located at the beggining of disk and a copy of it at the end too, so wiping only begin of disk won't work. 
So, there comes this script, it calculating sectors for dd to erase, and run dd in one go (for begin and end of disk). 
You just need after running the script, create new partition table (and partitions).

## Usage
Script require to be run from **root** account.
Just run ```./zdt.py``` to get all possible parameters.

## Requirments
Script written for Python3.
It require to work ```parted``` .

Tested on
```
root@deb:~# python3 --version
Python 3.5.3
root@deb:~# parted --version
parted (GNU parted) 3.2
Copyright (C) 2014 Free Software Foundation, Inc.
License GPLv3+: GNU GPL version 3 or later <http://gnu.org/licenses/gpl.html>.
This is free software: you are free to change and redistribute it.
There is NO WARRANTY, to the extent permitted by law.

Written by <http://git.debian.org/?p=parted/parted.git;a=blob_plain;f=AUTHORS>.
root@deb:~# cat /etc/debian_version
9.8
```

## License
Free for all for all usage (comercial/private) :smile: