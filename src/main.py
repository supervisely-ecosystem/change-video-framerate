import os
import math

import supervisely as sly
from supervisely.video_annotation.key_id_map import KeyIdMap

import ffmpeg

import globals as g


class FpsVideoInfo:
    FPS_EPSILON = 1e-4

    def __init__(self, pts_times):
        self.duration = pts_times[-1] - pts_times[0]
        self.frames_cnt = len(pts_times)
        frames_changed = self.frames_cnt - 1
        self.fps = frames_changed / self.duration if self.duration > 0 else 0

    def expect_frames_cnt(self, other_fps):
        return math.ceil(self.duration * other_fps)

    def fps_equals(self, other_fps):
        return abs(other_fps - self.fps) < self.FPS_EPSILON


def get_encoding_info(f_path):
    def get_name(stream_type):
        streams_info = list(filter(lambda x: x['codec_type'] == stream_type, probe_data['streams']))
        codec_name = streams_info[0]['codec_name'] if streams_info else None
        return codec_name

    probe_data = ffmpeg.probe(f_path)
    video_codec_name, audio_codec_name = [get_name(s) for s in ('video', 'audio')]
    bitrate = probe_data['format']['bit_rate']
    return video_codec_name, audio_codec_name, bitrate


def convert_video(target_fps, in_fpath, out_fpath):
    video_codec, audio_codec, bitrate = get_encoding_info(in_fpath)
    sly.logger.debug('Source codecs: Video="{}", Audio="{}" Source bitrate: {} bps'.format(
        video_codec, audio_codec, bitrate))

    ffmpeg_verbosity = {'hide_banner': None, 'loglevel': 'error'}
    in_video = ffmpeg.input(in_fpath, **ffmpeg_verbosity)
    video_stream = in_video.video.filter("fps", target_fps)

    stream_list = [video_stream]
    kwargs = {'vcodec': video_codec, 'video_bitrate': bitrate,
              'x265-params': 'log-level=error'}  # x265 lib bug with loglevel
    if audio_codec:
        stream_list.append(in_video.audio)
        kwargs.update({'acodec': audio_codec, 'strict': -2})    # 'strict' for libvorbis case
    ffmpeg.output(*stream_list, out_fpath, **kwargs).run()


@sly.timeit
def change_framerate(api: sly.Api, target_fps, result_project_name):
    if not result_project_name:
        project_info = api.project.get_info_by_id(g.PROJECT_ID)
        result_project_name = '{} {:.3} FPS'.format(project_info.name, target_fps)

    src_dir, res_dir = (os.path.join(g.data_directory, n) for n in ('source', 'result'))
    for d in (src_dir, res_dir):
        sly.fs.mkdir(d, remove_content_if_exists=True)

    meta_json = api.project.get_meta(g.PROJECT_ID)
    meta = sly.ProjectMeta.from_json(meta_json)
    res_project = api.project.create(g.WORKSPACE_ID, result_project_name,
                                     type=sly.ProjectType.VIDEOS, change_name_if_conflict=True)
    api.project.update_meta(res_project.id, meta_json)
    dummy_map = KeyIdMap()

    for dataset in api.dataset.get_list(g.PROJECT_ID):
        res_dataset = api.dataset.create(res_project.id, dataset.name, change_name_if_conflict=True)
        videos = api.video.get_list(dataset.id)
        progress = sly.Progress('Video recoding', len(videos))
        for video_info in videos:

            ann_info = api.video.annotation.download(video_info.id)
            ann = sly.VideoAnnotation.from_json(ann_info, meta, dummy_map)
            if ann.frames.figures or ann.objects:
                sly.logger.warn('Annotation data from video {} will be discarded.'.format(video_info.name))

            fps_info = FpsVideoInfo(video_info.frames_to_timecodes)
            expected_frame_cnt = fps_info.expect_frames_cnt(target_fps)
            sly.logger.info('Dataset "{ds}" Video "{vid}" '
                            'Source: {fps0:.5} FPS, {fc0} frames. Expect: {fc1} frames'.format(
                                ds=dataset.name, vid=video_info.name,
                                fps0=fps_info.fps, fc0=fps_info.frames_cnt, fc1=expected_frame_cnt))
            if expected_frame_cnt < 2:
                raise ValueError('Low FPS value', {'dataset': dataset.id, 'video': video_info.id})

            if fps_info.fps_equals(target_fps):
                sly.logger.debug('Preserving existing frame rate for video {}'.format(video_info.name))
                api.video.upload_hash(res_dataset.id, video_info.name, video_info.hash)
            else:
                curr_dirs = [os.path.join(d, dataset.name) for d in (src_dir, res_dir)]
                for d in curr_dirs:
                    sly.fs.mkdir(d)
                in_fpath, out_fpath = [os.path.join(d, video_info.name) for d in curr_dirs]

                api.video.download_path(video_info.id, in_fpath)
                sly.logger.debug('Downloaded video to {}'.format(in_fpath))
                convert_video(target_fps, in_fpath, out_fpath)
                sly.logger.debug('Converted video to {}'.format(out_fpath))
                api.video.upload_paths(res_dataset.id, (video_info.name,), (out_fpath,))
                sly.logger.debug('Uploaded video')
            progress.iter_done_report()

    sly.logger.debug('Finished change_framerate')


if __name__ == "__main__":
    sly.logger.info(
        "Script arguments",
        extra={
            "context.teamId": g.TEAM_ID,
            "context.workspaceId": g.WORKSPACE_ID,
            "modal.state.slyProjectId": g.PROJECT_ID,
            "modal.state.targetFps": g.TARGET_FPS,
            "modal.state.resultProjectName": g.RES_PROJECT_NAME
        },
    )

    change_framerate(g.api, g.TARGET_FPS, g.RES_PROJECT_NAME)

    try:
        sly.app.fastapi.shutdown()
    except KeyboardInterrupt:
        sly.logger.info("Application shutdown successfully")
