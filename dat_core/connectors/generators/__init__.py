"""
A generator receives on the Data Ingress and generates vector embeddings using a generator. E.g. OpenAI

It implements the following interface.

    spec() -> ConnectorSpecification
    check(Config) -> VectorizeConnectionStatus
    generate(Config, VectorizeCatalog, Stream<VectorizeMessage>(stdin)) -> Stream<VectorizeStateMessage>
"""
