import os
import sys

import supervisely as sly

from fastapi import FastAPI
from supervisely.app.fastapi import create
from supervisely.app.content import get_data_dir
from distutils.util import strtobool


app_root_directory = os.getcwd()
sly.logger.info(f'App root directory: {app_root_directory!r}')
sys.path.append(app_root_directory)

data_directory = get_data_dir()
temp_data_directory = os.getenv('DEBUG_TEMPORARY_APP_DIR', '/tmp/sly-app')  # to be removed after task execution
sly.logger.info(f'App data directory: {data_directory!r}  Temporary data directory: {temp_data_directory!r}')

app = FastAPI()
sly_app = create()
app.mount('/sly', sly_app)
api = sly.Api.from_env()

TASK_ID = int(os.environ['TASK_ID'])
TEAM_ID = int(os.environ['context.teamId'])
WORKSPACE_ID = int(os.environ['context.workspaceId'])
PROJECT_ID = int(os.environ['modal.state.slyProjectId'])
DATASET_ID = os.environ.get('modal.state.slyDatasetId', None)
if DATASET_ID is not None:
    DATASET_ID = int(DATASET_ID)
CHANGE_RESOLUTION = bool(strtobool(os.environ.get('modal.state.changeResolution', 'false')))
TARGET_HEIGHT = int(os.environ.get('modal.state.targetResolutionHeight'), 1280)
TARGET_WIDTH = int(os.environ.get('modal.state.targetResolutionWidth'), 720)
target_resolution = (TARGET_WIDTH, TARGET_HEIGHT)

TARGET_FPS = float(os.environ['modal.state.targetFps'])
RES_PROJECT_NAME = os.getenv('modal.state.resultProjectName', None)
