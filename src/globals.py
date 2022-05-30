import os
import sys

if '--DebugImportEnvsFromFiles' in sys.argv:
    import debug_utils
    debug_utils.load_envs_from_files()

import supervisely as sly

from fastapi import FastAPI
from supervisely.app.fastapi import create
from supervisely.app.content import get_data_dir


app_root_directory = os.getcwd()
sly.logger.info(f"App root directory: {app_root_directory}")
sys.path.append(app_root_directory)

data_directory = get_data_dir()
sly.logger.info(f"App data directory: {data_directory}")

app = FastAPI()
sly_app = create()
app.mount("/sly", sly_app)
api = sly.Api.from_env()

TASK_ID = int(os.environ["TASK_ID"])
TEAM_ID = int(os.environ["context.teamId"])
WORKSPACE_ID = int(os.environ["context.workspaceId"])
PROJECT_ID = int(os.environ["modal.state.slyProjectId"])

TARGET_FPS = float(os.environ['modal.state.targetFps'])
RES_PROJECT_NAME = os.getenv('modal.state.resultProjectName', None)
