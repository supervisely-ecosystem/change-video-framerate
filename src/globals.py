import os
import sys

import supervisely as sly

from fastapi import FastAPI
from supervisely.app.fastapi import create


app_root_directory = os.getcwd()
sly.logger.info(f"App root directory: {app_root_directory}")
sys.path.append(app_root_directory)

data_directory = '/var/sly-app'   # @TODO: ok?

# debug code BEGIN
# from dotenv import load_dotenv
#
# debug_env_path = os.path.join(app_root_directory, "debug.env")
# secret_debug_env_path = os.path.join(app_root_directory, "secret_debug.env")
# load_dotenv(debug_env_path)
# load_dotenv(secret_debug_env_path, override=True)
# sly.logger.setLevel(os.environ['LOG_LEVEL'].upper())    # because sly logger has been already initialized
# data_directory = os.environ['LOCAL_DEBUG_DATA_DIR']
# debug code END


app = FastAPI()
sly_app = create()
app.mount("/sly", sly_app)
api = sly.Api.from_env()

TASK_ID = int(os.environ["TASK_ID"])
TEAM_ID = int(os.environ["context.teamId"])
WORKSPACE_ID = int(os.environ["context.workspaceId"])
PROJECT_ID = int(os.environ["modal.state.slyProjectId"])

TARGET_FPS = float(os.environ['modal.state.targetFps'])
RES_PROJECT_NAME = os.environ['modal.state.resultProjectName']
