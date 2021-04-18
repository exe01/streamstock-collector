from streamstock_common.api_models import Model, Source, PipelineSettings, Compilation, Project
from streamstock_common.api_models.const import *
from streamstock_common.time import str_to_datetime
from streamstock_collector.configs import config
from streamstock_collector.title_formatter import format_title
from datetime import timedelta
from time import sleep
from requests import HTTPError
import twitch
import logging
import threading


logger = logging.getLogger(__name__)


tmp_locations = {}


def init():
    sleep_timedelta = timedelta(minutes=5)
    Model.DB_URL = config.STREAMSTOCK_API

    while True:
        try:
            for source in Source.get_():
                if source[SOURCE_TYPE] == SOURCE_TYPE_TWITCH:
                    credentials = source[SOURCE_CREDENTIALS]

                    helix = twitch.Helix(
                        credentials[TWITCH_CLIENT_ID],
                        credentials[TWITCH_CLIENT_SECRET],
                    )

                    last_video = None
                    for last_video in helix.user(source[SOURCE_LOCATION]).videos():
                        break

                    if compilation_exist(source, last_video.id):
                        continue

                    published = str_to_datetime(last_video.published_at)
                    title = format_title(
                        pattern=source[SOURCE_TITLE_PATTERN],
                        title=last_video.title,
                        name=source[SOURCE_NAME],
                        date=published,
                    )

                    pipeline_settings = PipelineSettings({
                        TWITCH_VOD_DOWNLOADER_QUALITY: '1080p60',
                        PIPELINE_NAME_OF_COMPILATIONS: title,
                    })
                    pipeline_settings.save()

                    compilation = Compilation({
                        SOURCE: source[ID],
                        COMPILATION_SOURCE_LOCATION: str(last_video.id),
                        PROJECT: source[PROJECT],
                        PIPELINE_SETTINGS: pipeline_settings[ID],
                    })

                    if source[SOURCE_AUTO_COMPILE] is True:
                        compilation[COMPILATION_STATUS] = COMPILATION_STATUS_ACTIVE

                    send_thread = threading.Thread(target=send_compilation, args=(compilation, ))
                    send_thread.start()
        except Exception as err:
            if isinstance(err, HTTPError):
                try:
                    logger.error(str(err.response))
                except:
                    pass
            elif hasattr(err, 'message'):
                logger.error(str(err.message))
            else:
                logger.error(str(err))

            logger.exception(err)

        sleep(sleep_timedelta.total_seconds())


def send_compilation(compilation):
    tmp_locations[compilation[COMPILATION_SOURCE_LOCATION]] = True
    sleep(timedelta(hours=5).total_seconds())
    compilation.save()


def compilation_exist(source, video_id):
    if str(video_id) in tmp_locations:
        return True

    params = {
        'source_location': str(video_id)
    }

    for compilation in source.get_compilations(params=params):
        return True

    return False
