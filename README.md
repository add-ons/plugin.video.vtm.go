[![GitHub release](https://img.shields.io/github/release/michaelarnauts/plugin.video.vtm.go.svg)](https://github.com/michaelarnauts/plugin.video.vtm.go/releases)
[![Build Status](https://travis-ci.com/michaelarnauts/plugin.video.vtm.go.svg?branch=master)](https://travis-ci.com/michaelarnauts/plugin.video.vtm.go)
[![Codecov status](https://img.shields.io/codecov/c/github/michaelarnauts/plugin.video.vtm.go/master)](https://codecov.io/gh/michaelarnauts/plugin.video.vtm.go/branch/master)
[![License: GPLv3](https://img.shields.io/badge/License-GPLv3-yellow.svg)](https://opensource.org/licenses/GPL-3.0)
[![Contributors](https://img.shields.io/github/contributors/michaelarnauts/plugin.video.vtm.go.svg)](https://github.com/michaelarnauts/plugin.video.vtm.go/graphs/contributors)

# VTM GO Kodi add-on

**This add-on is currently under development and isn't ready for use yet. The [Release 1.0](https://github.com/michaelarnauts/plugin.video.vtm.go/issues?q=is%3Aopen+is%3Aissue+milestone%3A%22Release+1.0%22) milestone indicates what issues I think are blocking the general use of this add-on.**

*plugin.video.vtm.go* is a Kodi add-on for watching all live video streams and all video-on-demand content available on the VTM GO platform. 
This add-on will also play the ads that are added to the streams by VTM GO.

The following features are supported:
* Watch live TV (VTM, Q2, Vitaya, CAZ, VTM Kids, VTM Kids Jr & QMusic)
* Watch on-demand content (movies and series)
* Browse the VTM GO recommendations and "My List"
* Browse a TV Guide
* Search the catalogue
* Browse the Kids zone
* Watch YouTube content from some of the DPG Media channels

## Installation

You can download the [latest release](https://github.com/michaelarnauts/plugin.video.vtm.go/releases) or download a [development zip](https://github.com/michaelarnauts/plugin.video.vtm.go/archive/master.zip) from Github.

## Inputstream Adaptive

VTM GO uses MPEG-DASH with Periods for the advertisements, and this is not supported in the current version of Inputstream Adaptive on Kodi 18. You need to have an unreleased inputstream.adaptive installed for this plugin to work fine. 

> Note that these builds claim to be version 2.4.0, while they are not. They might even be overridden by an older version with a higher version. A new release of inputstream.adaptive for Kodi 18 will fix this.

* Download a compiled build the [inputstream.adaptive jenkins server](https://jenkins.kodi.tv/blue/organizations/jenkins/peak3d%2Finputstream.adaptive/activity?branch=master):
  * [Android aarch64](https://jenkins.kodi.tv/job/peak3d/job/inputstream.adaptive/job/master/120/artifact/cmake/addons/build/zips/inputstream.adaptive+android-aarch64/inputstream.adaptive-2.4.0.zip)
  * [Android armv7](https://jenkins.kodi.tv/job/peak3d/job/inputstream.adaptive/job/master/120/artifact/cmake/addons/build/zips/inputstream.adaptive+android-armv7/inputstream.adaptive-2.4.0.zip)
  * [IOS aarch64](https://jenkins.kodi.tv/job/peak3d/job/inputstream.adaptive/job/master/120/artifact/cmake/addons/build/zips/inputstream.adaptive+ios-aarch64/inputstream.adaptive-2.4.0.zip)
  * [IOS armv7](https://jenkins.kodi.tv/job/peak3d/job/inputstream.adaptive/job/master/120/artifact/cmake/addons/build/zips/inputstream.adaptive+ios-armv7/inputstream.adaptive-2.4.0.zip)
  * [OSX 64bit](https://jenkins.kodi.tv/job/peak3d/job/inputstream.adaptive/job/master/120/artifact/cmake/addons/build/zips/inputstream.adaptive+osx-x86_64/inputstream.adaptive-2.4.0.zip)
  * [Windows 32bit](https://jenkins.kodi.tv/job/peak3d/job/inputstream.adaptive/job/master/120/artifact/cmake/addons/build/zips/inputstream.adaptive+windows-i686/inputstream.adaptive-2.4.0.zip)
  * [Windows 64bit](https://jenkins.kodi.tv/job/peak3d/job/inputstream.adaptive/job/master/120/artifact/cmake/addons/build/zips/inputstream.adaptive+windows-x86_64/inputstream.adaptive-2.4.0.zip)

* A build by somebody else:
  * [Raspberry Pi (Openelec)](http://users.telenet.be/peno/kodi/addons/inputstream.adaptive/inputstream.adaptive.zip) (compiled by @peno64)
  * [Vero4K+ (OSMC)](https://github.com/michaelarnauts/plugin.video.vtm.go/files/3720563/inputstream.adaptive.zip) (I had to copy the files to `/usr/lib/kodi/addons/inputstream.adaptive/` for it to work.)

* Or you can just compile it yourself:
```bash
git clone -b Leia https://github.com/xbmc/xbmc.git
git clone https://github.com/peak3d/inputstream.adaptive
cd ~/inputstream.adaptive && mkdir build && cd build
cmake -DADDONS_TO_BUILD=inputstream.adaptive -DADDON_SRC_PREFIX=../.. -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=../../xbmc/addons -DPACKAGE_ZIP=1 ../../xbmc/cmake/addons
make
cd ~/xbmc/addons/
zip -r inputstream.adaptive.zip inputstream.adaptive
```

## Disclaimer

This add-on is not officially commissioned/supported by DPG Media and is provided 'as is' without any warranty of any kind.
The VTM GO name, VTM GO logo, channel names and icons are property of DPG Media and are used according to the fair use policy. 
