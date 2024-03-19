import os
import json
from typing import Mapping, Any
from dat_core.pydantic_models.dat_document_stream import DatDocumentStream

class StateManager:

    def save_stream_state(self, stream: DatDocumentStream, stream_state: Mapping[Any, Any]) -> None:
        raise NotImplementedError()
    
    def read_current_stream_state(self, stream: DatDocumentStream) -> Mapping[Any, Any]:
        raise NotImplementedError()


class LocalStateManager(StateManager):

    def _local_path_from_stream(self, configured_stream: DatDocumentStream) -> None:
        _path = os.path.join(os.path.curdir, f'.{configured_stream.namespace}')
        if not os.path.exists(_path):
            os.mkdir(_path)
        return os.path.join(_path, 'stream_state.json')
    
    def save_stream_state(self, stream: DatDocumentStream, stream_state: Mapping[Any, Any]) -> None:
        with open(self._local_path_from_stream(stream), 'w') as _state_file:
            return _state_file.write(json.dumps(stream_state))

    def get_stream_state(self, stream: DatDocumentStream) -> Mapping[Any, Any]:
        state_file_content = self._get_state_file_content(stream)
        return state_file_content
    
    def _get_state_file_content(self, stream: DatDocumentStream) -> Mapping[Any, Any]:
        with open(self._local_path_from_stream(stream), 'r') as _state_file:
            state_file_content = json.loads(_state_file.read())
            return state_file_content or {}
