# dat-core
data activation tool (dat) is an open source Python library for creating and running data activation (reverse ELT) pipelines with ease

## Run tests
```bash
coverage -m pytest
```

## generate test coverage report on terminal
```bash
coverage report
```

## generate test coverage report in HTML
```bash
coverage html
```


## Getting started
- Deploy [dat Open Source](https://example.com) or set up [dat Cloud](https://example.com) to start fetching unstructured data, generating embeddings and loading them to vector databases.
- Explore popular use cases in our tutorials.

Getting started with dat takes only a few steps! This page guides you through the initial steps to get started and you'll learn how to setup your first connection on the following pages.

When self-managing dat, your data never leaves your premises. Get started immediately by deploying locally using Docker.

### Docker steps (placeholder)
- Install `Docker Engine` and the `Docker Compose plugin` on your workstation \(see [instructions](https://docs.docker.com/engine/install/)\).
- After Docker is installed, you can immediately get started locally by running:

```bash
curl -sSL https://gist.githubusercontent.com/riju-dc/0abdddfc7e70c3e5216171588537cbd0/raw/4169ff516295f92f7847ed78af272034f528f087/run-dat-platform.sh | bash
```

# dat Protocol Docker Interface

## Summary
The [dat Protocol](dat-protocol.md) describes a series of structs and interfaces for building data pipelines. The Protocol article describes those interfaces in language agnostic pseudocode, this article transcribes those into docker commands. dat's implementation of the protocol is all done in docker. Thus, this reference is helpful for getting a more concrete look at how the Protocol is used. It can also be used as a reference for interacting with dat's implementation of the Protocol.


## Source

### Pseudocode:

```
spec() -> ConnectorSpecification
check(Config) -> DatConnectionStatus
discover(Config) -> DatCatalog
read(Config, DatCatalog, State) -> Stream<DatRecordMessage | DatStateMessage>
```

### Docker:
```shell
docker run --rm -i <source-image-name> spec
docker run --rm -i <source-image-name> check --config <config-file-path>
docker run --rm -i <source-image-name> discover --config <config-file-path>
docker run --rm -i <source-image-name> read --config <config-file-path> --catalog <catalog-file-path> [--state <state-file-path>] > message_stream.json
```

The `read` command will emit a stream records to STDOUT.

## Generator

### Pseudocode:
```
spec() -> ConnectorSpecification
check(Config) -> DatConnectionStatus
generate(Config, Stream<DatMessage>(stdin)) -> Stream<DatStateMessage>
```

### Docker:
```shell
docker run --rm -i <destination-image-name> spec
docker run --rm -i <destination-image-name> check --config <config-file-path>
cat <&0 | docker run --rm -i <destination-image-name> generate --config <config-file-path>
```

The `generate` command will consume `DatMessage`s from STDIN and emit a stream records to STDOUT.

## Destination

### Pseudocode:
```
spec() -> ConnectorSpecification
check(Config) -> DatConnectionStatus
write(Config, DatCatalog, Stream<DatMessage>(stdin)) -> Stream<DatStateMessage>
```

### Docker:
```shell
docker run --rm -i <destination-image-name> spec
docker run --rm -i <destination-image-name> check --config <config-file-path>
cat <&0 | docker run --rm -i <destination-image-name> write --config <config-file-path> --catalog <catalog-file-path>
```

The `write` command will consume `DatMessage`s from STDIN.

## I/O:
* Connectors receive arguments on the command line via JSON files. `e.g. --catalog catalog.json`
* They read `DatMessage`s from STDIN. The destination `write` action is the only command that consumes `DatMessage`s.
* They emit `DatMessage`s on STDOUT.