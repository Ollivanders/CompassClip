# CompassClip

## Winner of Encode 2024 Hackathon - Compass Labs Shrink the Chain challenge

Runs SuperSet JSON-RPC calls to a chain, storing the result in S3.

Provides a wrapper library for making RPC calls to these files to collect desired information

## Overview

The system syncs with an archive node (currently by rpc calls), creating a local partitioned file
set based on block, transaction and contract data. These represent efficient yet responsive stores
of blockchain data, allowing querying of desired information by apis, abstracted as rpc methods. The
initial sync takes chain, start block, end block as parameters. Indexing is unique my chain allowing
for parallel implementations while syncing varying block ranges do not overlap with each other.

An example output running pruning on the eth chain:

```
data
└── eth
    ├── block
    ├── block_partitioned
    │   └── block
    │       ├── 0.json
    │       └── partition_depth.txt
    ├── contract
    ├── contract_partitioned
    │   └── contract
    │       ├── 0.json
    │       ├── 1.json
    │       ├── 2.json
    │       ├── 3.json
    │       ├── 4.json
    │       ├── 5.json
    │       ├── 6.json
    │       ├── 7.json
    │       ├── 8.json
    │       ├── 9.json
    │       ├── a.json
    │       ├── b.json
    │       ├── c.json
    │       ├── d.json
    │       ├── e.json
    │       ├── f.json
    │       └── partition_depth.txt
    ├── transaction
    └── transaction_partitioned
        └── hash
            ├── 0x00.json
            ├── 0x01.json
            ├── 0x02.json
            ├── 0x03.json
            ├── 0x04.json
            ├── 0x05.json
            ├── 0x06.json
            ├── 0x07.json
            ├── 0x08.json
            ├── 0x09.json
            ├── 0x0a.json
            ├── 0x0b.json
            ├── 0x0c.json
            ...
            └── partition_depth.txt
```

## Installation

Run python3.11 or lower. It is recommended this project is run in venv.

```
python3 -m pip install -r requirements.txt
```

Problems with latency and python version were had with the ethereum-etl lib. Therefore, where ever
possible the lib was replaced with a local version that did not require multiple pip packages of
varying dependencies to run. Inspiration on the mapper layout was taking from this lib but was
extended with the partition writer and reader for faster retrieval of data.

## Syncing

The data collection has already ran on a subset of blocks used for the examples below (the last
10,000). This can be downloaded from s3 using the following command:

`python3 application/sync.py`
The shell command here is abstracted into python to ensure no confusion about what dir you should be
when the command. You will need the `aws-cli` installed locally to utilise the parallelisation of
the download. The bucket is setup so that you will not need any credentials to sync cached versions
of the database.

Syncing currently works using ankr rpc nodes, credits to which were provided by @Compass.

## Syncing yourself

There is currently not a cli for configuring options, however the latest 1000 blocks can be synced
by running
`python3 application/main.py`

## Making RPC calls

Start the flask server by running

```bash
python3 application/app.py
```

## Website version

Remote hosted version
<http://35.179.186.61:5000>

Synced on:

- eth chain
- block ranges 21055431 - 21056431
- the USDC contract address

Then visit <http://127.0.0.1:5000> for some examples as a frontend.

![frontend](docs/frontend.jpg)

Query the api by hitting the json rpc endpoint with the following

```bash
curl -i -X POST    -H "Content-Type: application/json; indent=4"    -d '{
    "jsonrpc": "2.0",
    "method": "eth_getCode",
    "params": {"address": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48", "blockNumber": "21054566"},
    "id": "1"
}' http://localhost:5000/api
```

## Aims and design philosophy

The most drop in solution to solving the "pruned node" issue would be patching an existing node technology,
thus maintaining its interfaces and clients at a fraction of the size. This is explored below in
alternative approaches but would involve a low level database formatting by monkey patching an
existing node. This is a task that will likely demand more time than a weekends work to effectively
create a POC. Its chances of success also hinge on being able to create a file that is still treated
as a valid blockchain and thus could result in a reimplementation or fork of the node software all
together.

In the spirit of the hackathon and producing a viable solution, the second approach has been chosen of creating a
data store from rpc calls, filtering these into a data structure which can be rapidly called by an
rpc like client to serve up relevant data. In production, this could be deployed and a consumer of
it unaware of the underlying data structure.

- How many chains supported? - any that have an rpc client. Abstract dataclasses in python are
  currently built from the rpc calls. This is done for speed an ease of pruning and can be applied
  to support any chain type but is abstract enough to support most EVM chains in a base capacity
- Include with n degree proximity to origin contract
  - can collect addresses and then re-run a separate exporter to append these to the file stores
- Include all transactions - remove address filtering
- What RPC methods can it respond to - lib implementation for each as below. Focused on key look up
  patterns

## eth_ method focuses

- `eth_getCode`
- `eth_getTransaction`

<https://docs.alchemy.com/reference/eth-gettransactionbyhash>

## Feature Improvements

- As discussed below, use an Erigon node directly to hit the database directly and ignore the
  overhead of rpc calls.
- facility for real time syncing to the chian, indexing storage say by block range

## Alternative approach: Patching an Existing Chain

### Erigon

Experimented with usage of mbdx.dat file that erigon uses.

<https://ethereum.org/en/developers/docs/nodes-and-clients/archive-nodes/#what-is-an-archive-node>
<https://lmdb.readthedocs.io/en/release/> - lmdb, python client used to investigate database structure
on file

![took a while to download](docs/image.png)

as specified at *<https://github.com/erigontech/erigon/blob/main/ethdb/Readme.md>*
mdbx file format is a key-value database, utilising B+ trees in order to store reciept, transaction
and block data in a mapping format.

```asciiflow.com
// This is not call graph, just show classes from low-level to high-level.
// And show which classes satisfy which interfaces.

                    +-----------------------------------+   +-----------------------------------+
                    |  github.com/erigontech/mdbx-go    |   | google.golang.org/grpc.ClientConn |
                    |  (app-agnostic MDBX go bindings)  |   | (app-agnostic RPC and streaming)  |
                    +-----------------------------------+   +-----------------------------------+
                                      |                                      |
                                      |                                      |
                                      v                                      v
                    +-----------------------------------+   +-----------------------------------+
                    |       ethdb/kv_mdbx.go            |   |       ethdb/kv_remote.go          |
                    |  (tg-specific MDBX implementation) |   |   (tg-specific remote DB access)  |
                    +-----------------------------------+   +-----------------------------------+
                                      |                                      |
                                      |                                      |
                                      v                                      v
            +----------------------------------------------------------------------------------------------+
            |                                       ethdb/kv_abstract.go                                   |
            |         (Common KV interface. DB-friendly, disk-friendly, cpu-cache-friendly.                |
            |           Same app code can work with local or remote database.                              |
            |           Allows experiment with another database implementations.                           |
            |          Supports context.Context for cancellation. Any operation can return error)           |
            +----------------------------------------------------------------------------------------------+
                 |                                        |                                      |
                 |                                        |                                      |
                 v                                        v                                      v
+-----------------------------------+   +-----------------------------------+   +-----------------------------------+
|       ethdb/object_db.go          |   |          ethdb/tx_db.go           |   |    ethdb/remote/remotedbserver    |
|     (thread-safe, stateless,      |   | (non-thread-safe, more performant |   | (grpc server, using kv_abstract,  |
|   opens/close short transactions  |   |   than object_db, method Begin    |   |   kv_remote call this server, 1   |
|      internally when need)        |   |  DOESN'T create new TxDb object)  |   | transaction maps on 1 grpc stream |
+-----------------------------------+   +-----------------------------------+   +-----------------------------------+
                |                                          |
                |                                          |
                v                                          v
            +-----------------------------------------------------------------------------------------------+
            |                                    ethdb/interface.go                                         |
            |     (Common DB interfaces. ethdb.Database and ethdb.DbWithPendingMutations are widely used)   |
            +-----------------------------------------------------------------------------------------------+
                |
                |
                v
+--------------------------------------------------+
|             ethdb/mutation.go                    |
| (also known as "batch", recording all writes and |
|   them flush to DB in sorted way only when call  |
|     .Commit(), use it to avoid random-writes.    |
|   It use and satisfy ethdb.Database in same time |
+--------------------------------------------------+

```

Further details can be found at
<https://github.com/erigontech/erigon/blob/main/docs/programmers_guide/db_walkthrough.MD>. While this
is an interesting read, it reveals about as much as the Dragon scroll did in the first Kung Fu Panda
film.

The key part here is the ethdb/kv-abstract.go implementation. An ideal solution would interface
directly with the database using one of the methods described in
<https://github.com/erigontech/erigon/blob/main/docs/programmers_guide/db_faq.md>. This by passes the
rpc interface, thus as long as the file can be read either locally or via ssh-fs seek calls, one
could utilise the `RoKV` interface that is provided to quickly make abstracted `eth_` calls to get
the information required.

Using this interface, a duplicate mdbx.dat could be created. One would read from one file to collect
whats needed to write to another one. Writing however is the tricky part. The provided methods
assume a "node" is running and thus expect all the checksums to be correct. If one was to prune
transactions to only collect ones that touched specific contract addresses, this would break the
ability to "run on the chain".

![building new erigon mbdx.dat files](docs/image-1.png)

The advantage of an mdbx.dat storage format is that an Erigon archive node would be able to read
from it, thus enabling use of their existing `rpcdaemon` lib and native calls to a pruned private
blockchain only containing relevant contract address information.

To conclude, an approach of patching a node would require:

- creating methods for writing to a new mdbx.dat file in the same format Erigon expects
  - add new methods for back populating block data, deleting transactions for instance that do not
    meet certain requirements
  - use existing methods of writing a new block by mining it on to a private chain, only including
      the filtered addresses. This however would invalidate checksums. This would either need to be
      ignored when the pruned node is queried or overwritten in some way and any errors thrown
      because of it discarded
- hotfix the sync library to enable an option to migrate one mdbx.dat file to another
- hope and pray the pruned mdbx.dat file is compatible

The above libs would have to be maintained with each Erigon node release for each support language
(Rust, C++ and go)

### Anvil

The following is the provision of the backend to the database following a pointer from
CompassLabs. This would be a good place to start if looking to work with Anvil. Erigon was
investigated primarily due to the size of the project by comparison but also cause the provided
examples and node is an Erigon node.

<https://github.com/foundry-rs/foundry/blob/master/crates/anvil/src/eth/backend/db.rs>

### Geth

Running a private pruned blockchain as a geth node.
t

- Fork an existing chain for study. Back delete unneeded transactions. This would however not allow
  clean resyncing
- Sync on a polling basis to a new chain, mining each block on with only necessary transactions.
  This would not be a valid blockchain and would need be a new protocol specific for each chain and
  therefore a heavy approach.

### TheGraph

Used as an intermediate data store. Creates a postgres SQL database and syncs with a blockchain.
This can then provide a more searchable and faster response time then individual rpc calls, as well
as a better response to getStorageAt. Creating a subgraph and then run such a service as above to
convert to a No-SQL or otherwise format would provide a scalable prunable node.

<https://thegraph.com>
