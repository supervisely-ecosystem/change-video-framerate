import os
import sys

if '--DebugImportEnvsFromFiles' in sys.argv:
    import debug_utils
    debug_utils.load_envs_from_files()

import supervisely as sly
from supervisely.video_annotation.key_id_map import KeyIdMap

import globals as g
from functions import FpsVideoInfo, convert_video


@sly.timeit
def change_framerate(api: sly.Api, target_fps, result_project_name):
    if not result_project_name:
        project_info = api.project.get_info_by_id(g.PROJECT_ID)
        result_project_name = f'{project_info.name} {target_fps:.6g} FPS'

    src_dir, res_dir = (os.path.join(g.temp_data_directory, n) for n in ('source', 'result'))
    for d in (src_dir, res_dir):
        sly.fs.mkdir(d, remove_content_if_exists=True)

    meta_json = api.project.get_meta(g.PROJECT_ID)
    meta = sly.ProjectMeta.from_json(meta_json)
    res_project = api.project.create(g.WORKSPACE_ID, result_project_name,
                                     type=sly.ProjectType.VIDEOS, change_name_if_conflict=True)
    api.project.update_meta(res_project.id, meta_json)
    dummy_map = KeyIdMap()

    datasets = api.dataset.get_list(g.PROJECT_ID)
    progress = sly.Progress('Video recoding', sum(ds.items_count for ds in datasets))

    for dataset in datasets:
        res_dataset = api.dataset.create(res_project.id, dataset.name, change_name_if_conflict=True)

        videos = api.video.get_list(dataset.id)
        for video_info in videos:

            ann_info = api.video.annotation.download(video_info.id)
            ann = sly.VideoAnnotation.from_json(ann_info, meta, dummy_map)
            if ann.frames.figures or ann.objects:
                sly.logger.warn(f'Annotation data from video {video_info.name!r} will be discarded.')

            fps_info = FpsVideoInfo(video_info.frames_to_timecodes)
            expected_frame_cnt = fps_info.expect_frames_cnt(target_fps)
            sly.logger.info(f'Dataset {dataset.name!r} Video {video_info.name!r} Source: {fps_info.fps:.5} FPS, '
                            f'{fps_info.frames_cnt} frames. Expect: {expected_frame_cnt} frames')
            if expected_frame_cnt < 2:
                raise ValueError('Low FPS value', {'dataset': dataset.id, 'video': video_info.id})

            if fps_info.fps_equals(target_fps):
                sly.logger.debug(f'Preserving existing frame rate for video {video_info.name!r}')
                api.video.upload_id(res_dataset.id, video_info.name, video_info.id)
                # api.video.upload_hash(res_dataset.id, video_info.name, video_info.hash)
            else:
                curr_dirs = [os.path.join(d, dataset.name) for d in (src_dir, res_dir)]
                for d in curr_dirs:
                    sly.fs.mkdir(d)
                in_fpath, out_fpath = [os.path.join(d, video_info.name) for d in curr_dirs]

                api.video.download_path(video_info.id, in_fpath)
                sly.logger.debug(f'Downloaded video to {in_fpath!r}')
                convert_video(target_fps, in_fpath, out_fpath)
                sly.logger.debug(f'Converted video to {out_fpath!r}')
                api.video.upload_paths(res_dataset.id, (video_info.name,), (out_fpath,))
                sly.logger.debug('Uploaded video')
            progress.iter_done_report()

    sly.logger.debug('Finished change_framerate')


if __name__ == '__main__':
    sly.logger.info(
        'Script arguments',
        extra={
            'context.teamId': g.TEAM_ID,
            'context.workspaceId': g.WORKSPACE_ID,
            'modal.state.slyProjectId': g.PROJECT_ID,
            'modal.state.targetFps': g.TARGET_FPS,
            'modal.state.resultProjectName': g.RES_PROJECT_NAME
        },
    )

    change_framerate(g.api, g.TARGET_FPS, g.RES_PROJECT_NAME)

    try:
        sly.app.fastapi.shutdown()
    except KeyboardInterrupt:
        sly.logger.info('Application shutdown successfully')
