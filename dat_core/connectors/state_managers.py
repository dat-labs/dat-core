import os
import json
from typing import Mapping, Any
from dat_core.pydantic_models import (
    DatDocumentStream,
    StreamState,
)

class StateManager:

    def save_stream_state(self, stream: DatDocumentStream, stream_state: StreamState) -> None:
        raise NotImplementedError()
    
    def get_stream_state(self, stream: DatDocumentStream) -> Mapping[Any, Any]:
        raise NotImplementedError()

    def cleanup_stream_state(self, stream: DatDocumentStream) -> Mapping[Any, Any]:
        raise NotImplementedError()

class LocalStateManager(StateManager):

    def _local_path_from_stream(self, stream: DatDocumentStream) -> None:
        _path = os.path.join(os.path.curdir, f'.{stream.namespace}')
        if not os.path.exists(_path):
            os.mkdir(_path)
        return os.path.join(_path, 'stream_state.json')
    
    def save_stream_state(self, stream: DatDocumentStream, stream_state: StreamState) -> None:
        with open(self._local_path_from_stream(stream), 'w+') as _state_file:
            return _state_file.write(stream_state.model_dump_json())

    def get_stream_state(self, stream: DatDocumentStream) -> Mapping[Any, Any]:
        state_file_content = self._get_state_file_content(stream)
        return StreamState(**state_file_content)
    
    def cleanup_stream_state(self, stream: DatDocumentStream) -> Mapping[Any, Any]:
        if os.path.exists(self._local_path_from_stream(stream)):
            os.remove(self._local_path_from_stream(stream))
    
    def _get_state_file_content(self, stream: DatDocumentStream) -> Mapping[Any, Any]:
        state_file_content = {'data': {}}
        try:
            with open(self._local_path_from_stream(stream), 'r') as _state_file:
                state_file_content = json.loads(_state_file.read())
                return state_file_content
        except:
            # TODO: raise proper exception
            pass
        
        return state_file_content
