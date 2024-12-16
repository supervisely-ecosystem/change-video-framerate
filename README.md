<div align="center" markdown>
<img src="https://github.com/supervisely-ecosystem/change-video-framerate/releases/download/v0.1.0/app-poster.png"/>

# Change Video Framerate

<p align="center">
  <a href="#Overview">Overview</a> •
  <a href="#How-To-Run">How To Run</a>
</p>
  
[![](https://img.shields.io/badge/slack-chat-green.svg?logo=slack)](https://supervisely.com/slack)
![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/supervisely-ecosystem/change-video-framerate)
[![views](https://app.supervisely.com/img/badges/views/supervisely-ecosystem/change-video-framerate.png)](https://supervisely.com)
[![runs](https://app.supervisely.com/img/badges/runs/supervisely-ecosystem/change-video-framerate.png)](https://supervisely.com)

</div>
  
  
## Overview

News:<br>
🎉 `v0.8.0` it's possible to change output video resolution 

This app changes framerate for videos in Supervisely video project. It drops (or duplicates) video frames with preserving video duration.

<img src="https://github.com/supervisely-ecosystem/change-video-framerate/releases/download/v0.1.0/point-up.png" width="20px"/> All annotated data (including tags and objects) will be discarded.

#### Technical note.
The process includes re-coding video. Besides, duration of the resulting video may not match precisely original duration. Also the re-coding preserves original video bitrate, if appropriate.

## How To Run

**Step 1**: Add app to your team from Ecosystem if it is not there.

<img src="https://github.com/supervisely-ecosystem/change-video-framerate/releases/download/v0.7.0/shot01.png"/>

**Step 2**: Open context menu of project -> `Run App` -> `Change video framerate` 

<img src="https://github.com/user-attachments/assets/4f7c9351-a50f-4c98-aa00-914a4ee59083"/>

**Step 3**: Input target framerate (Frames Per Second) and (optionally) name of output project. New videos will be saved in new project of the same workspace.

If you want to change the resolution of the output video, enable this option `ON` and adjust the `Width` and `Height`.

<img src="https://github.com/user-attachments/assets/776e7262-078c-4299-8c33-a353716ef0f3" width=500px/>

