<div align="center" markdown>
<img src="https://github.com/supervisely-ecosystem/change-video-framerate/releases/download/v0.1.0/app-poster.png"/>

# Change Video Framerate

<p align="center">
  <a href="#Overview">Overview</a> •
  <a href="#How-To-Run">How To Run</a>
</p>
  
[![](https://img.shields.io/badge/slack-chat-green.svg?logo=slack)](https://supervise.ly/slack)
![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/supervisely-ecosystem/change-video-framerate)
[![views](https://app.supervise.ly/public/api/v3/ecosystem.counters?repo=supervisely-ecosystem/change-video-framerate&counter=views&label=views)](https://supervise.ly)
[![used by teams](https://app.supervise.ly/public/api/v3/ecosystem.counters?repo=supervisely-ecosystem/change-video-framerate&counter=downloads&label=used%20by%20teams)](https://supervise.ly)
[![runs](https://app.supervise.ly/public/api/v3/ecosystem.counters?repo=supervisely-ecosystem/change-video-framerate&counter=runs&label=runs&123)](https://supervise.ly)

</div>
  
  
## Overview

This app changes framerate for videos in Supervisely video project. It drops (or duplicates) video frames with preserving video duration. The process includes re-coding video. 

<img src="https://github.com/supervisely-ecosystem/change-video-framerate/releases/download/v0.1.0/point-up.png" width="20px"/> All annotated data (including tags and objects) will be discarded.

## How To Run

**Step 1**: Add app to your team from Ecosystem if it is not there.

**Step 2**: Open context menu of project -> `Run App` -> `Change video framerate` 

**Step 3**: Input target framerate (Frames Per Second) and (optionally) name of output project. New videos will be saved in new project of the same workspace.
