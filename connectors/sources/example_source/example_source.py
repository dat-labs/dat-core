import os
from typing import Any, Dict, List, Mapping, Optional, Tuple
from connectors.sources.base import SourceBase

class Zendesk(SourceBase):

    """
    Example source
    """
    _spec_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'specs.yml')

    def check_connection(self, config: Mapping[str, Any]) -> Tuple[bool, Any | None]:
        return (True, True)
    
    def streams(self, config: Mapping[str, Any]) -> List[Dict]:
        return [{}]

if __name__ == '__main__':
    print(Zendesk().spec())