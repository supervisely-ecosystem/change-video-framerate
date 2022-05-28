import math

import supervisely as sly

import ffmpeg


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
