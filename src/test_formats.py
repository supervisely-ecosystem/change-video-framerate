import os

import supervisely as sly
import ffmpeg

from functions import convert_video


def print_info(f_path):
    probe_data = ffmpeg.probe(f_path, count_frames=None)
    vstream = next(filter(lambda x: x['codec_type'] == 'video', probe_data['streams']))
    info = {k: probe_data['format'][k] for k in ('duration', 'bit_rate', 'size')}
    info.update({k: vstream[k] for k in ('nb_read_frames', 'r_frame_rate', 'avg_frame_rate')})
    sly.logger.debug(f'ffmpeg.probe {f_path!r}', extra=info)


def test(target_fps, in_dir, out_dir):
    f_names = sorted(os.listdir(in_dir))
    for f_name in f_names:
        in_fpath, out_fpath = (os.path.join(d, f_name) for d in (in_dir, out_dir))
        if os.path.isfile(in_fpath):
            print_info(in_fpath)
            convert_video(target_fps, in_fpath, out_fpath)
            sly.logger.debug('recoded')
            print_info(out_fpath)
    sly.logger.debug('finished')


if __name__ == '__main__':
    TARGET_FPS = 5
    IN_DIR = 'debug_data/_video_samples'
    OUT_DIR = 'debug_data/recoded_video_samples'

    sly.logger.setLevel('DEBUG')
    sly.fs.mkdir(OUT_DIR, remove_content_if_exists=True)
    test(TARGET_FPS, IN_DIR, OUT_DIR)
