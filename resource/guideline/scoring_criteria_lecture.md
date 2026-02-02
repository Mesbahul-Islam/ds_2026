### Lecture 0:

## Introduction to Course

**521290S Distributed Systems (202 6 )**

**Asst. Prof. Lauri Lovén**
Leader of FCG **,** Center for Applied Computing, ITEE, UOULU
(ds.yo.2026@proton.me)


#### Teaching staff

```
Lecturer: Asst. Prof. Lauri Lovén, Leader of FCG/ 6GF , APPCOMP, ITEE,
UOULU (responsible)
```
```
Teaching assistants: M.Sc. Alaa Saleh, APPCOMP, ITEE, UOULU (senior)
M.Sc. Mazen Hassaan, APPCOMP, ITEE, UOULU
M.Sc. Stanley Amaechi, APPCOMP, ITEE, UOULU
```
```
Contact: Email: ds.yo.2026@proton.me
At Lectures and Exercise (Classroom and Zoom)
Moodle: messages or discussion forum (for general questions)
```

#### Information Systems

##### Peppi:

```
‒ Course information:
```
- https://opas.peppi.oulu.fi/en/course/521290S/6422?period=2025- 2026
- Registration to the course


#### Information Systems

```
Moodle Virtual Learning Environment:
‒ main online course workspace
‒ URL: https://moodle.oulu.fi/course/view.php?id=
‒ Contents:
```
- - Lecture videos and slides, other handouts Problem sets availableCourse project material
- - Course project submissionOpen discussion forum


#### Course book

```
van Steen and Tanenbaum:
Distributed Systems, 4th ed., 2023
‒ Free preprint PDF available on
https://www.distributed-systems.net/
‒ Book website includes additional material:
another slide set, code examples, etc.
```

#### Course book

1. Introduction
2. Architectures
3. Processes
4. Communication
5. Naming
6. Synchronization
7. Consistency and replication
8. Fault tolerance
9. Security


#### Recommended reading


#### Implementation

```
Fully English
Components :
```
**1. Lectures** (voluntary), in English, Classroom and Zoom
**2. Exercises** (voluntary ), in English, Classroom and Zoom
**3. For lectures** (book chapters) #02-#09, self-study
**4. Course project** (mandatory), in groups of 3-5 students, self-study
**5. Final exam** (mandatory)

###### Grading


#### Lectures

```
‒ Classroom and Zoom:
https://oulu.zoom.us/j/
```
```
‒ Lecture PDFs will be available for self-study in Moodle
```

#### Exercises

```
‒ Will be done in hybrid fashion in classroom and zoom
(https://oulu.zoom.us/j/ 69927287679 )
‒ Frameworks and tools for implementing distributed systems
and supporting project progress.
‒ Exercises are not graded
‒ Q&A sessions with teaching assistants
```

#### Course project

```
‒ Mandatory - a student has to get at least 10 p from the
course project (max 20 p) to pass the course!
‒ Project can be completed in groups of 3 - 5 students.
‒ Select your project group by 15 January 2026 , 23 : 59.
‒ Grading is based on final submission and demonstration to
teaching staff.
‒ Support from teaching staff is available during exercises /
Moodle messages / email
‒ Nominal workload is 55 hours / student, hence keep your
project well-focused!
```

#### Course project

```
Task: Build a DISTRIBUTED SYSTEM
‒ Addresses a ”real-world” application or a research problem.
‒ Demonstrates selected distributed system functionalities.
‒ Software implementation satisfying given technical requirements.
```
- We will provide basic information, data, tutorial(s)...
- Requirements on the following slides...
‒ No hardware components unless you really want to use your own!
‒ Document using given report template.
‒ Demonstrate to teaching staff.


#### Course project

```
Task: Build a DISTRIBUTED SYSTEM
‒ We provide topics to choose from, or propose your own by 15 Jan
2026, 23:59 which has similar complexity level (implement &
demonstrate concepts from all lectures in one single final project)
‒ Our Topic List: https://docs.google.com/presentation/d/18eSfCQCoHp-
BvT5gkqZv3HMlEhwF2aImoegSMbtDhK8/edit?usp=sharing
‒ Register your topic by mentioning [Group ID] in our project google
sheet. Ensure that the project fits within 6-week outline.
‒ If you want to propose your own topic, send your slide and your group
ID via course email (ds.yo.2026@proton.me).
```

#### Course project: Application or

###### Research problem

```
‒ Your topics:
```
- Multiplayer game: card games, rock paper scissors, tic-tac-toe, ..
- Online bulletin board / library (tuple space), ..
- Web-based (minimal) collaboration tool, ..
- Synchronized streaming / content delivery: music player, ..
- To o l f o r s y s t e m m o n i t o r i n g / e v e n t d e t e c t i o n ,..
- ...?
- Results and/or further work can possibly lead to **thesis** /
**scientific article**!


#### Course Project Req 1: Distribution

```
Select 1+ distributed system functionalities that your
project demonstrates, for example:
‒ Distributed algorithm for synchronization, consistency control, election, brokering,
event matching
‒ Implementation of flooding / gossip protocols
‒ Resource naming / discovery / sharing mechanism
‒ Code migration
‒ Secure key management
‒ Etc.
```
**This is simpler than you may think!!**


#### Course project: Req 2. Architecture

```
Application-specific system components
‒ System must have at least three nodes (e.g, containers)
‒ Each node must have a role: client, server, peer, broker, etc.
Participating nodes must
‒ Exchange information (messages): RPC, client-server, publish-
subscribe, broadcast, streaming, etc.
‒ Log their behavior understandably: messages, events, actions, etc.
```

#### Course project: Req 2. Architecture

```
Nodes (or their roles) do not have to be identical
‒ For example, one acts as server, broker, monitor / admin, etc.
‒ Each node must be an independent entity and (partially)
autonomous
```

#### Course project: Req 3. Evaluation

```
Evaluate your implementation using selected criteria, for
example:
‒ Number of messages / lost messages, latencies, ...
‒ Request processing with different payloads, ..
‒ System throughput, ..
Design two evaluation scenarios that you compare with
each other, for example:
‒ Small number / large number of messages
‒ Small payload / big payload
```

#### Course project: Req 3. Evaluation

```
Collect numerical data of test cases
‒ Collecting logs of container operations
‒ Conduct simple analysis for documentation purposes (e.g. plots or
graphs)
```

#### Course project: About implementation

```
If you are familiar with a particular container technology,
feel free to use it (Docker is not mandatory)
Any programming language can be used
‒ Python, Java, JavaScript, R, C/C++, C#, Rust, ..
Any communication protocol / Internet protocol suite can
be used
‒ HTTP(S), MQTT, AMQP, CoAP, ..
```

#### Course project: About implementation

```
Implementation based on existing
libraries or codebases is ok
‒ But application logic must be your own design
‒ Just setting up an existing system is not accepted!
‒ If any doubt, please ask teaching staff in advance
```

#### Course project: Final submission

**1. Project report**
‒ Report template will be provided (in Moodle)
‒ Report template must be followed (otherwise immediate reject)
‒ Detailed description of the system architecture, functionality and evaluation
‒ Detailed descriptions of relevant principles covered in the course (architecture,
    processes, communication, naming, synchronization, consistency and replication, fault
    tolerance); irrelevant principles can be left out.
**2. Source code**
‒ Reasonably commented code (in GitHub, etc.)


#### Course project: Guidelines and tips

```
‒ A proper initial design helps a lot in the
implementation phase.
‒ Do not over-engineer!
‒ Project focus is NOT on UI or application logic!
‒ Re-use existing code base as much as possible to
reduce workload!
```

#### Course project: Guidelines and tips

```
‒ Remember to cite existing work properly.
‒ If in doubt, don’t make guesses but ask course staff.
```

#### Course project: Timeline

```
Upload final submission to Moodle by Mon
01.3.2026 at 23:59 (hard & mandatory DL)
```
```
Give online demo to teaching staff in Zoom
‒ Book a slot for demo in Moodle.
‒ All group members must be present at the demo!
```

#### Project grading

‒ 20 points total

- 10 points on Demonstration
- 10 points on Report
- **Minimum accepted: 10 points total (Demo+Report)**


#### Demonstration grading: 10 points

```
‒ Each report will be presented to teaching staff.
‒ Each group has 15 minutes for presentation + 5 minutes for questions.
‒ Points are cumulative. If a condition is not fully satisfied, partial points
are given.
‒ 10 points in total:
```
- 2 points – clear presentation logic flow
- 2 points – message is clearly conveyed, providing evidence that authors understand
    the topic
- 2 points – nice visual appearance of slides (not only text on the slides!)
- 2 points – examples are provided
- 2 points – well-prep


#### Report Grading: 10 points

```
Grading:
Structure: 3 points max
Description: 3 points max
Clarity: 2 points max
Language: 1 points max
Visual: 1 points max
```

```
Structure: 3 points max
How is the structure of the report?
Points are cumulative.
1 points – Structure follows template.
1 points – All content follows structure
(e.g., Results section only describes
the results, all discussion is in the
discussion section, etc.).
1 points – Repetition is minimized.
```
#### Project

#### report

#### 10 points


```
Description: 3 points max
How well is the implementation described?
Points are cumulative:
1 points – Main functionality is well-
described, with diagrams on the different
components and their interaction.
1 points – Repo structure is well-described,
making it easy for new developers to start
using the repo.
1 points – Tests and evaluations are well-
described.
```
#### Project

#### report

#### 10 points


```
Clarity: 2 points max
How clear and logical is the documentation?
0.5 points – It is very hard to understand the design
choices, the overall functionality, and the
implementation.
1 points – It is somewhat hard to understand the
overall functionality and implementation.
1.5 points – Project is described with satisfactory
clarity.
2 points – Project described with exceptional
clarity.
```
#### Project

#### report

#### 10 points


```
Language: 1 points max
Is the report well-written?
```
```
0.5 points – Grammar and style has minor flaws.
1 point – Grammar and style are good.
```
#### Project

#### report

#### 10 points


```
Visual: 1 points max
Is the report visually pleasing?
```
```
0.5 points – Minor flaws, such as unclear figures or
minor deviation from template.
1 point – Report is visually flawless.
```
#### Project

#### report

#### 10 points


#### Final Exam (mandatory) (3h)

- Mandatory - a student has to get at least 10 p on
the final exam (max 20 p) to pass the course!
- Questions are based on full course book +
lectures (# 1 - # 10 ).

```
EXAM PROTOCOL/ DATE WILL BE
ANNOUNCED LATER !!!
```

#### Grading

To p a s s t h e c o u r s e t h e f o l l o w i n g i s r e q u i r e d :

1. Course project: demonstration and report.
- Max 20, 10p required to pass
2. Final Exam:
- Max 20, 10p required to pass


#### Grading

```
The weighted average of course project and exam determines
the course grade (max. 20p):
```
- 10.00 → **1**
- 12.00 → **2**
- 14.00 → **3**
- 16.00 → **4**
- 18.00 → **5**

```
Exam and course project points carry over to future years.
```

```
University of Oulu
```
#### Schedule

```
Date Time Location Activity
07 /01/202 6 08:15-10:00 Online-TA105 Lecture #0: Introduction to course
13 /01/202 6 12 :15- 14 :00 Online- L2 Lecture #1: Introduction to Distributed Systems
14 /01/202 6 08:15-10:00 Online- TA105 Lecture #2: Architectures
16 /01/202 6 10 :15-12:00 Online- PR104 Exercise #1
20 /01/202 6 12 :15- 14 :00 Online- L2 Lecture #3: Processes
21/01/202 6 08:15-10:00 Online- L7 Lecture #4: Communication
23/01/202 6 08:15-10:00 Online- L2 Exercise #2
30/01/202 6 10:15-12:00 Online-TS101 Exercise #3
03 /0 2 /202 6 12 :15- 14 :00 Online- L2 Lecture #5: Naming
04 /0 2 /202 6 08:15-10:00 Online- TA105 Lecture #6: Coordination
06 /02/202 6 08:15-10:00 Online- TA105 Exercise #4
10 /0 2 /202 6 1 2:15-14:00 Online- L2 Lecture #7: Consistency and replication
11 /0 2 /202 6 08:15-10:00 Online- TA105 Lecture #8: Fault Tolerance
13 /0 2 /202 6 12 :15- 14 :00 Online- IT115 Exercise #5
17 /0 2 /202 6 12:15-14:00 Online- L2 Lecture #9: Security
18 /0 2 /202 6 08:15-10:00 Online- TA105 Lecture #10: Edge computing
20 /0 2 /202 6 12 :15- 14 :00 Online- IT115 Exercise #6
24 /0 2 /202 6 12:15-14:00 Online- L2 Lecture placeholder
25 /0 2 /202 6 08:15-10:00 Online- TA105 Lecture placeholder
27 /0 2 /202 6 12 :15- 14 :00 Online- IT115 Exercise #7
```

#### Fair play

```
Student is removed from the course for cheating in exams or
submitting duplicate course work (plagiarism). Self-plagiarism
(re-using previous course work or similar) is not allowed.
Do NOT just task AI to do your work – it will come out!
In all cases, the penalties apply to all students involved.
```
```
When in doubt, ask teaching staff!
```

#### Q & A

```
‒ ??
```

# Thank you

ds.yo.2026@proton.me


