import os
import argparse
import io
import json
from conftest import *
from connectors.destinations.vector_db_helpers.utils import create_chunks


class TestDestination:

    def test_create_chunks(self, ):
        """
        GIVEN a list of 1000 items
        WHEN create_chunks is called with a batch_size of 100
        THEN 10 chunks of 100 items are returned
        """
        _chunk_cnt = 0
        input_list = list(range(112))
        chunks = create_chunks(input_list, batch_size=100)
        for chunk in chunks:
            _chunk_cnt += 1
            print(f"Count {_chunk_cnt} - chunk: {chunk}")
            assert len(chunk) == 100
