import os

import supervisely as sly
import ffmpeg


def get_codec_names(f_path):
    def get_name(stream_type):
        streams_info = list(filter(lambda x: x['codec_type'] == stream_type, probe_data['streams']))
        codec_name = streams_info[0]['codec_name'] if streams_info else None
        return codec_name

    probe_data = ffmpeg.probe(f_path)
    video_codec_name, audio_codec_name = [get_name(s) for s in ('video', 'audio')]
    return video_codec_name, audio_codec_name


def print_info(f_path):
    probe_data = ffmpeg.probe(f_path, count_frames=None)
    fmt = probe_data['format']
    vs = next(filter(lambda x: x['codec_type'] == 'video', probe_data['streams']))
    print('duration: {}  bit_rate: {}  size: {}'.format(fmt['duration'], fmt['bit_rate'], fmt['size']))
    print('nb_read_frames: {}  r_frame_rate: {}  avg_frame_rate:  {}'.format(
        vs['nb_read_frames'], vs['r_frame_rate'], vs['avg_frame_rate']))


def test_file2(target_fps, in_fpath, out_fpath):
    print('in: "{}"  out: "{}"'.format(in_fpath, out_fpath))
    print_info(in_fpath)
    video_codec, audio_codec = get_codec_names(in_fpath)
    print('codecs: "{}", "{}"'.format(video_codec, audio_codec))
    ffmpeg_verbosity = {'hide_banner': None, 'loglevel': 'error'}
    in_video = ffmpeg.input(in_fpath, **ffmpeg_verbosity)
    video_stream = in_video.video.filter("fps", target_fps)

    stream_list = [video_stream]
    kwargs = {'vcodec': video_codec, 'x265-params': 'log-level=error'}  # x265 lib bug with loglevel
    if audio_codec:
        stream_list.append(in_video.audio)
        kwargs.update({'acodec': audio_codec, 'strict': -2})    # 'strict' for libvorbis case
    ffmpeg.output(*stream_list, out_fpath, **kwargs).run()
    print('recoded')
    print_info(out_fpath)
    print(os.linesep)


def test(target_fps, in_dir, out_dir):
    f_names = sorted(os.listdir(in_dir))
    for f_name in f_names:
        in_fpath, out_fpath = (os.path.join(d, f_name) for d in (in_dir, out_dir))
        if os.path.isfile(in_fpath):
            test_file2(target_fps, in_fpath, out_fpath)
    print('finished')


if __name__ == "__main__":
    TARGET_FPS = 5
    IN_DIR = 'debug_data/_video_samples'
    OUT_DIR = 'debug_data/recoded_video_samples'

    sly.fs.mkdir(OUT_DIR, remove_content_if_exists=True)
    test(TARGET_FPS, IN_DIR, OUT_DIR)
