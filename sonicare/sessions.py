"""Download the brushing sessions stored on the handle.

The sequence below is taken from the decompiled Philips app
(SessionStorageService / C5318t / C5184f) and was run successfully against an
HX991X (firmware 1.7.3), fetching three sessions. Not covered: very long
transfers (hundreds of sessions), error paths on a real brush, and the gyro
compensation record, which is not fetched here.

Protocol per session id (all in the Session service):

    write Type (40d5)     = type of the record wanted
    write Request (40e0)  = session id (u16)
    write Control (4110)  = 0                       start the transfer
    notify Data (4100)    = the record
    notify Control (4110) = 0 or 1                  record complete

repeated for ROUTINE_SESSION, BRUSH_HEAD_REPLACEMENT_DATA, BRUSH_ID and
SESSION_SUMMARY. The ids to fetch are `Last_id - Count + 1 .. Last_id`, with
Count read after selecting ROUTINE_SESSION in Type.
"""
from dataclasses import dataclass

from .data import SERVICES
from .enums import SonicareSessionType as Type
from . import parsers

RECORD_TYPES = (
    Type.ROUTINE_SESSION,
    Type.BRUSH_HEAD_REPLACEMENT_DATA,
    Type.BRUSH_ID,
    Type.SESSION_SUMMARY,
)


@dataclass
class Session:
    routine: parsers.RoutineSession
    brush_head_replacement: parsers.BrushHeadReplacementData
    brush_id: parsers.BrushId
    summary: bytes  # not decoded, the app ignores it as well


def parse_session(records):
    "Build a Session from {SonicareSessionType: bytes}"
    return Session(
        routine=parsers.parse_routine_session(records[Type.ROUTINE_SESSION]),
        brush_head_replacement=parsers.parse_brush_head_replacement(records[Type.BRUSH_HEAD_REPLACEMENT_DATA]),
        brush_id=parsers.parse_brush_id(records[Type.BRUSH_ID]),
        summary=bytes(records[Type.SESSION_SUMMARY]),
    )


class SessionDownloader:
    """Callback driven, needs the glib main loop of `gatt` to be running.

        SessionDownloader(client, on_session=print).start()
    """

    def __init__(self, client, on_session, on_done=None, on_error=None):
        self.client = client
        self.on_session = on_session
        self.on_done = on_done
        self.on_error = on_error

        service = SERVICES["0004"]
        self._data_uuid = service.uuid("4100")
        self._control_uuid = service.uuid("4110")

        self._active = False
        self._records = {}
        self._index = 0

    def start(self, first_id=None):
        "Fetch all stored sessions, or those from `first_id` on"
        client = self.client
        client.add_notify_listener(self._on_notify)
        client.subscribe_session_request()
        client.subscribe_session_data()
        client.subscribe_session_control()

        client.write_session_type(Type.ROUTINE_SESSION)
        self._last_id = client.read_session_last_id()
        count = client.read_session_count()

        self._next_id = self._last_id - count + 1
        if first_id is not None:
            self._next_id = max(self._next_id, first_id)
        self._fetch_next()

    def _fetch_next(self):
        if self._next_id > self._last_id:
            self._finish()
            return
        self._records = {}
        self._index = 0
        self._active = True
        self._request()

    def _request(self):
        client = self.client
        client.write_session_type(RECORD_TYPES[self._index])
        client.write_session_request(self._next_id)
        client.write_session_control(0)

    def _on_notify(self, uuid, value):
        if not self._active:
            return
        if uuid == self._data_uuid:
            self._records[RECORD_TYPES[self._index]] = bytes(value)
        elif uuid == self._control_uuid:
            status = value[0]
            if status not in (0, 1):
                self._fail(ValueError("session {}: control point answered {}".format(self._next_id, status)))
                return
            self._index += 1
            if self._index < len(RECORD_TYPES):
                self._request()
            else:
                self._complete()

    def _complete(self):
        try:
            session = parse_session(self._records)
        except (KeyError, ValueError) as error:
            self._fail(error)
            return
        self.on_session(session)
        self._next_id += 1
        self._fetch_next()

    def _fail(self, error):
        if self.on_error:
            self.on_error(error)
        self._finish()

    def _finish(self):
        self._active = False
        self.client.remove_notify_listener(self._on_notify)
        if self.on_done:
            self.on_done()
