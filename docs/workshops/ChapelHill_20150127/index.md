# RHESSys Workshop - January 27-28, 2015


For this workshop, we will be using [RHESSysWorkflows](https://github.com/selimnairb/RHESSysWorkflows) to build a RHESSys model for the [Baisman Run](http://waterdata.usgs.gov/md/nwis/uv/?site_no=01583580) watershed, a forested and suburban watershed near Baltimore Maryland, and is one of the [study watersheds](http://www.umbc.edu/cuere/BaltimoreWTB/data.html) of the Baltimore Ecosystem Study Long-Term Ecological Research site ([BES LTER](http://www.beslter.org)).

We will discuss applications of RHESSys to urban and forested watersheds.  The [agenda](#agenda) includes time for discussion and small group/individual work.  Please come prepared to ask questions relevant to your study site.  Also, there will be some time to work on your own model, so bring along any data you might need to build a RHESSys model for your study site.  Please refer to the RHESSysWorkflows [tutorial](https://github.com/selimnairb/RHESSysWorkflows#using-rhessysworkflows---introduction) or the RHESSys [wiki](https://github.com/RHESSys/RHESSys/wiki) for more information on data requirements.

## Logistics

#### Where
The workshop will be held at the offices of the Institute for the Environment at the University of North Carolina at Chapel Hill.  These offices are located in the Europa Center, the address of which is:
 
100 Europa Drive, Suite 490  
Chapel Hill, NC 27517

#### When
Tuesday January 27th and Wednesday January 28, 2015 from 9:00 AM to 5:00 PM

#### Food
This is a free workshop therefore breakfast and lunch will not be provided, however light snacks and coffee will be provided during our afternoon breaks.  There is a restaurant in the Europa Center that is open for lunch and serves high-quality southern fare.  There are grocery stores, coffee, and bagel shops within a short drive of the Europa Center.

## Table of contents
- [Before you arrive](#before-you-arrive)
- [Agenda](#agenda)

### Before you arrive
We will be using some basic Unix commands as part of this workshop.  To make this go more smoothly, we recommend that novice Unix users review lessons 1-3 of the Software Carpentry [Unix Shell lessons](http://software-carpentry.org/v5/novice/shell/index.html).

Before taking part in this workshop, you will need to use the following instructions to download and install a virtual machine that has RHESSysWorkflows pre-installed.

#### Install VirtualBox
To run the RHESSysWorkflows virtual machine, you will need to first download and install VirtualBox version 4.3.20 or later from:

Before you can install the RHESSysWorkflows virtual machine under a Windows host operating system, you must install a utility that can open the archive format used to compress the virtual machine (this compression is necessary to save cloud storage space and to reduce download times).  We suggest you install 7-Zip, which you can find here:

[http://www.7-zip.org/](http://www.7-zip.org/)
Download the compressed virtual machine acrhive here:

[http://goo.gl/qkSxuv](http://goo.gl/qkSxuv)

The compressed file is about 2 GB, so we recommend you download via a fast network or when you have a lot of time.  When the download completes, move the archive, named “RHESSysWorkflows-VM-201501.tbz” to your “VirtualBox VMs” directory (this will be in your home directory under OS X).

#### Uncompress RHESSysWorkflows virtual machine

Un-archive the virtual machine using tar:




