#### Lecture 2:

### Architecture

###### 521290S Distributed Systems (2026)

Prof. Lauri Lovén, 6GF/CAC, Future Computing Group, ITEE, UOULU

(ds.yo.2026@proton.me)


#### Outline

###### 1. What is architecture?

###### 2. Software architectures

###### 3. System architectures

###### 4. Take-home message


## What do we mean by

## architecture?

###### Definitions.


#### Distributed systems architectures

###### ”A distributed system is a

###### collection of autonomous

###### computing elements that

###### appears to its users as a

###### single coherent system”

###### (-- Maarten van Steen,

###### Andrew S. Tanenbaum)


#### Distributed systems architectures

**Software architecture**

```
‒ Logical organization of the
distributed system into (system or
application-specific) software
components.
```
- How the components are organized and
    how they interact.
‒ For example: The design of the
    middleware that separates
    applications from the platform.
- Tradeoffs, as discussed in last lecture.

**System architecture**

```
‒ Placement and instantiation of the
software components on real
(physical) computers.
```
```
‒ Often very different from logical
organization
```
- Real-world distributed systems are often
    organized in hybrid fashion with both
    centralized and decentralized components.

Give an

example!


## Software architectures

###### Architectural styles.


#### Software architectures

**Architectural style** is defined by **:**

**1. Software components** : modular,
    replaceable units with well-defined
    requirements and interfaces.
**2. Connectors:** The way the components
    are connected to each other.
**3. Data/information exchanges between**
    **the components** for applications and
    control.
**4. Configuration** of the components and
    connectors to a system.

```
Mechanisms that facilitate interactions
between components, mediating
communication, coordination and
cooperation.
```
```
Example : RPC or streaming
frameworks.
```

#### Software architectures

**Fundamental architectural styles:**

1. Layered
2. Object-based
3. Publish-subscribe


#### Layered style

```
Software components are organized as
logical layers (/levels)
```
```
‒ Each layer implements an interface that
specifies the functions/services that its
components provide...
```
```
‒ ...while it hides the underlying
functionalities: application/system
components, lower layer services.
```

#### Layered style

```
Example?
```

```
University of Oulu
```
#### Example: communication protocols

```
Protocol:
```
- which messages are to be exchanged for setting up or tearing down a connection,
- what needs to be done to preserve the ordering of transferred data, and
- what both parties need to do to detect and correct data that was lost during
    transmission.

**Interface:**

- a relatively
    simple
    programming
    interface,
    containing
    calls to set up
    a connection,
    send and
    receive
    messages,
    and to tear
    down the
    connection
    again.

```
Example:
TCP service
```

#### Application Layering

**Traditional three-layered view:**

```
‒ Application-interface layer contains units for
interfacing to users or external applications.
```
```
‒ Processing layer contains the functions of an
application, i.e., without specific data.
```
```
‒ Data layer contains the data that a client wants to
manipulate through the application components.
```

#### Application layering

**Example: A simple search engine for buying houses**


#### Application layering

**Example: IoT application** Application layer

```
Middleware layer
```
```
Transmission layer
```
```
Perception layer
```
```
Smart
applications
```
```
Database
```
```
Cloud computing
```
```
Ubiq. computing
```
```
Decision making
```
```
Information
transmission
```
```
Physical
objects
```
```
How is this related to
traditional, 3-layered
architecture:
```
1. Application-interface layer,
2. Processing layer, and
3. Data layer?


#### Middleware layer

```
Middleware is (typically) an interconnection layer logically placed between applications
and the computers that are part of the distributed system
```
‒ Hides the hardware and software (e.g. OS) differences of these computers.

‒ Each application provided with the same interfaces and services.

‒ Manages system resources (and composes services for applications).

```
‒ Enables applications and their distributed components to reliably communicate with
each other.
```
Application layer

Middleware layer

Transmission layer

Perception layer

```
Smart
applications
Database
Cloud computing
```
```
Ubiq. computing
Decision making
Information
transmission
Physical
objects
```
```
Computer 1
App A
```
```
Local
OS 1
```
```
Local
OS 2
```
```
Local
OS 3
```
```
App C
```
```
Local
OS 4
```
```
App B
```
```
Distributed system layer (middleware)
```
```
Computer 2 Computer 3 Computer 4
```

#### Object-based style

**Components** (=objects) are _loosely but directly_ connected to each other

```
‒ Objects may be placed on different machines; calls can thus execute
across a network.
```
```
‒ Component encapsulates data and exposes methods (=functionality)
to access the data, similar to OOP.
```

```
University of Oulu
```
#### Middleware for objects?

Wrapper / adapter Broker Interceptor
Pros and cons of
brokers when
compared to
wrappers??

```
What additional
functionality could
we have here
regarding the
Servant object?
```

#### Resource-centered architectures

```
Fundamentally different point-of-view: functionality abstracted as
a resource, managed by a component.
```
‒ No more function calls – instead, manipulation of a resource (=content).

**Key characteristics:**

1. Resources are identified through a single naming scheme.
2. All services offer the same interface.
3. Messages sent to or from a service are fully self-described.
4. After executing an operation at a service, that component forgets everything
    about the caller.


```
University of Oulu
```
#### Resource-centered architectures

**Example: Representational State Transfer (REST) architectural style**

```
‒ Resources can be added, modified, retrieved and removed through the same interface
(HTTP methods PUT, GET, DELETE and POST).
```
‒ Interface methods have exactly the same semantics for every resource.

‒ Resources have a single naming scheme, i.e., URL hierarchy.

```
‒ But.. both clients and servers must have the common context (i.e. the meaning of
resources).
```
```
Operation Description
PUT Create a new resource.
GET Retrieve the state of a resource in some representation.
DELETE Delete a resource.
POST Modify a resource by transferring a new state.
```

#### Resource-centered architectures

**Example: Amazon’s Simple Storage Service (S 3 )**

```
Objects (i.e., files) are placed into buckets (i.e., directories). Buckets cannot be placed
into buckets. Operations on ObjectName in bucket BucketName require the following
identifier:
```
[http://BucketName.s](http://BucketName.s) 3 .amazonaws.com/ObjectName

Typical operations:

All operations are carried out by sending HTTP requests:

‒ Create a bucket/object: PUT, along with the URI

‒ Listing objects: GET on a bucket name

‒ Reading an object: GET on a full URI


```
University of Oulu
```
#### On interfaces

```
Issue: Many people like RESTful approaches because the interface to a
service is so simple. The catch is that much needs to be done in the
parameter space.
```
Amazon S3 SOAP interface:

```
Bucket operations Object operations
ListAllMyBuckets PutObjectInline
CreateBucket PutObject
DeleteBucket CopyObject
ListBucket GetObject
GetBucketAccessControlPolicy GetObjectExtended
SetBucketAccessControlPolicy DeleteObject
GetBucketLoggingStatus GetObjectAccessControlPolicy
SetBucketLoggingStatus SetObjectAccessControlPolicy
```

#### On interfaces

**Example** :

```
Assume an interface bucket offering an operation create , requiring an input
string such as mybucket , for creating a bucket “mybucket.”
```
**SOAP:**

_import bucket_

_bucket.create("mybucket")_

**RESTful**

```
PUT "https://mybucket.s3.amazonsws.com/" Pros and cons of
SOAP when
compared to
RESTful??
```

#### Publish-subscribe architectures

```
Flexibility is beneficial for distributed systems design and
implementation
```
```
‒ Relaxing dependencies between components (e.g. clients and
servers) makes it easier to update, modify and reconfigure the system.
```
- E.g., join or leave.
‒ **The catch:** requires separation of processing and coordination
(distribution transparency?)


#### Publish-subscribe architectures

###### Coordination:

‒ Binds functionalities of components into a complete system.

‒ Different coordination models:

_1. referential_ (address and name) vs _temporal_.
_2. coupled_ vs. _decoupled_
    - Referential decoupling: interact without explicit naming.
    - Temporal decoupling: interact without being active at the same time.

```
Temporally coupled Temporally decoupled
Referentially coupled Direct Mailbox
```
```
Referentially decoupled Event-based Shared data space
```
**Pub-sub**


#### Event-based coordination

Event-based coordination model is enabled by **loose referential coupling.**

```
‒ Component interactions through publish & subscribe of events / notifications.
Middleware:
```
‒ Provides mechanisms for naming and matching subscribers & publishers.

‒ Matching based on declared topics of interest and/or content.

‒ Receives, stores and forwards the events (or notifications) to subscribers.


#### Event-based coordination

**Example** : MQTT protocol for IoT systems, based on topic-based matching.


#### Shared data spaces coordination

**Shared associative memory:**

```
‒ Associative : components need to
know the semantics.
```
```
‒ Model : publisher / subscriber, with no
referential or temporal coupling.
```
```
‒ Clients upload their state / data / tasks
to a common storage.
```
- If the storage is **distributed** , separate
    coordination needed.

```
What could become
a problem with this?
```

#### Shared data spaces coordination

**Example: Tuple space**

‒ **Tuple** :

- Finite ordered list of elements
    (a 1 ,a 2 ,...an).
‒ **Simple atomic operations** to
    use the space:
- **out** : Write a tuple into space.
- **in** : Read and remove a tuple from
    space.
- **rd** : Non-destructive read from space.
    Tuple space

```
1: [data]
```
```
2: [data]
```
```
3: [data]
```
```
4: [data]
```
```
Process
```
```
Process
```
```
Process
```
```
Process
```
```
Process
```
```
out
```
```
out
```
```
out
```
```
out
```
```
rd
```
```
rd
```
```
in
```

**Issue** : how to match events?

‒ Assume events are described by (attribute,value) pairs.

‒ **Topic-based subscription** : specify a “attribute = myvalue” series.

‒ **Content-based subscription** : specify a “attribute ∈ myrange” series.

#### Publish-subscribe architectures

```
What
could
become a
problem
with this?
```

## System architectures

###### Vertical, horizontal and hybrid organization.


#### System architectures

**Instantiation/realization of a software architecture**

```
Server
```
Client

```
Client
```
```
Client
```
```
Peer
```
```
Peer
Peer Peer
```
```
Peer
Peer
```
```
Centralized
organization
```
```
Decentralized
organization
```
```
Hybrid
organization
```
```
Client
Client
```
```
Client
```
```
Client
```
```
Client
```
```
Client
```

#### System architectures

**Instantiation/realization of a software architecture**

```
Server
```
Client

```
Client
```
```
Client
```
```
Peer
```
```
Peer
Peer Peer
```
```
Peer
Peer
```
```
Centralized
organization
```
```
Decentralized
organization
```
```
Hybrid
organization
```
```
Client
Client
```
```
Client
```
```
Client
```
```
Client
```
```
Client
```

##### Centralized organization

**Client-server model**

```
‒ There are processes offering services ( servers ).
‒ There are processes that use services ( clients ).
```
‒ Clients and servers can be on different machines.

‒ Clients follow request/reply model regarding using services.


#### Multi-tiered Centralized organization

```
(a) (b) (c) (d) (e)
```

```
University of Oulu
```
#### Multi-tiered Centralized organization

```
(a) (b) (c) (d) (e)
```
Why go back
Why left?
move
right?

```
Why go back
right again?
```
```
Can we go to
(f)?
```

#### Multi-tiered Centralized organization

**Some traditional organizations**

```
Single-tiered Two-tiered
```
##### ?


#### Multi-tiered Centralized organization

**Some traditional organizations**

```
Three-tiered
```
```
Client
```
```
Application
server
```
```
DB server
```

#### Multi-tiered Centralized organization

**Some traditional organizations:**

```
Three-tiered
```
```
Client
```
```
Application
server
```
```
DB server
```

#### Example: Simple Web servers

```
Website == collection of
HTML files, referring to each
other with hyperlinks.
```
```
Needs only a
hyperlink to fetch the
right HTML file.
```
Renders the
page.


##### Example: Slighly more complicated

##### web servers

```
Still needs only a
hyperlink to fetch the
right HTML file.
```
CGI (Common Gateway Interface)
program composes the page from
DB contents, fecthed from the DB.
Client still Hyperlinks still refer to web pages.
renders the
page.


#### Alternative organizations

**Vertical distribution Horizontal distribution**

```
Peer
```
```
Peer
Peer
```
```
Peer-to-peer distribution
```
```
A client or server may be
physically split up into
logically equivalent parts, but
each part is operating on
its own share of the
complete data set.
```
```
Symmetric.
```
```
E.g., Spark ,
Hadoop...
```

#### Peer-to-peer distribution

```
Interaction between peers (=processes) is
symmetric , i.e. each peer is both client and server
(servant) at the same time.
‒ Functions that need to be carried out are
represented by every process.
```
```
‒ Leads to logical application-specific overlay
networks, that are either:
```
1. **Structured** , with deterministic topology.
2. **Unstructured** , as a random graph.
3. **Hierarchical** organization of peers.

```
Peer
```
```
Peer
```
Peer

```
Distributed
Organization,
peer-to-peer
(P2P) distribution
```

#### Structured P2P

**Specific deterministic topology:**

‒ Topology can be ring, binary, tree, grid, etc.

‒ Peers maintain shortcuts to other peers used to look up data.

- _Semantic-free index_ : each data item is uniquely associated with a key, in turn used as
    an index.

**Hypercube:**

```
Looking up d with key k
∈ { 0 , 1 , 2 ,..., 24 − 1 }
means routing request
to node with identifier k.
```

#### Structured P2P

‒ Common practice: use a hash function

_key(data item) = hash(data item’s value)._

‒ P2P system now responsible for storing (key,value) pairs.

- DHT: data items assigned with random keys that are mapped to random peer ids, look
    up returns the peer network address.

**Hypercube:**

```
Looking up d with key k
∈ {0, 1, 2,..., 24 − 1}
means routing request
to node with identifier k.
```

#### Unstructured P2P

‒ Peers maintain list(s) of neighbors.

- Results continuously change.
- Data items are placed randomly, so requires searching of data with
    **flooding** (send request to all neighbors), **policy-based search** or with
    **random walk** over the network**.**

```
Example: keep
track of preferred
neighbours.
```

#### Hierarchical P2P

**Super peer:**

```
‒ Peers are connected to super
peers that are organized as P2P
network.
```
```
‒ Leader election mechanism
needed.
```
```
Super
Peer
Super
Super Peer
Peer
```
```
Peer
```
```
Peer
```
```
Peer
```
```
Peer
```
```
Peer
```
```
Peer
```
```
Example:
```
P2P system
performance can
be improved with
_index servers_

- > super peers.

```
Example:
```
```
Collaborative CDNs
can decide where to
store data more
efficiently through
brokers - > super
peers.
```

#### Example: BitTorrent

**Distributed file-sharing system.**

```
‒ P2P system where users download files in chunks that are then assembled into
complete files.
```
‒ Ensures collaboration as download chunk is shared with others.

```
‒ Global directory (Web server) hosts torrent files that contain the information to
download a file.
```
```
‒ Tracker (a server) keeps a list of active peers (that host chunks).
‒ Peer becomes active when it starts downloading the file.
```
‒ To avoid bottleneck, trackers can also form separate P2P system to share workload.


#### Example: BitTorrent

**Case: search for a file F:**

```
‒ Lookup file at a global directory ⇒ returns a torrent file
‒ Torrent file contains reference to tracker: a server keeping an accurate account of
active nodes that have (chunks of) F.
```
```
‒ Peer P can join swarm, get a chunk for free, and then trade a copy of that chunk for
another one with a peer Q also in the swarm.
```

#### Hierarchical P2P

```
Super
Peer
Super
Super Peer
Peer
```
```
Peer
```
```
Peer
```
```
Peer
```
```
Peer
```
```
Peer
```
```
Peer
```
```
How are these
different?
```
```
Peer
```
```
Peer
Peer
```
```
Hybrid
organization
```
```
Client
Client
```
Client

```
Client
```
```
Client
```
```
Client
```

#### Hybrid organization: Cloud computing


```
University of Oulu
```
#### Hybrid organization: Cloud computing

```
Processors, routers, power and
cooling systems. Customers
normally never get to see these.
```
**PaaS:** Provides higher-level abstractions for
storage and such. Example: Amazon S3 storage
system offers an API for (locally created) files to
be organized and stored in so-called buckets.

```
SaaS: Actual applications, such as office suites
(text processors, spreadsheet applications,
presentation applications). Comparable to the
suite of apps shipped with OSes.
```
```
IaaS: Deploys virtualization techniques.
Evolves around allocating and managing
virtual storage devices and virtual servers.
```

#### Take-home message:

```
To choose the right software and system architecture,
consider:
```
‒ What’s the driver for distribution/decentralization?

‒ What are the **necessary** and **sufficient** conditions?

- Where is the data?
- Where are the users?
- What administrative boundaries must be crossed? How? Policy issues?
- How computation/communication/data intensive is the application?
- Trust, security aspects?


#### Take-home message:

**Based on the answers, decide:**

- **Degree of transparency** : What must be exposed, what can be hidden?
- **Degree of centralization:** Any necessary condition keeping you from a centralized
    system architecture?
- **Degree of coupling** : Referential or temporal decoupling, or both? Required
    functionality of Middleware?

**Finally:**

- **Software architecture:** The components, connectors, data streams, and their
    configurations required.
- **System architecture** : The system configuration supporting the software architecture.


# Thank you

## ds.yo.2026@proton.me


