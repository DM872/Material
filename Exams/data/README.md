### Input Data

You are given a starting package containing data on the exams for the
last semesters at the Faculty of Science, SDU and some Python code to
read the data.


An instance of the *exam scheduling problem* consists of two files:
`config.json` and a file containing details about the exams to schedule.
Specifically, you are given exams composing different instances of the
problem with different size and difficulty. The following tables resume 
each instance with a tuple indicating in the order: the number of
exams, the number of exam days to allocate, the number of room days
available and the number of students.

```
|---------+--------------+--------------+--------------+--------------+--------------+--------------+-------------|
|         | E21          | F21          | F21re        | F22          | F22re        | E22          | E22re       |
|---------+--------------+--------------+--------------+--------------+--------------+--------------+-------------|
| samf    | 9/9/1950     |              |              |              |              | 21/34/2316   |             |
| biologi | 21/28/1950   | 15/17/2482   | 11/11/1496   | 21/24/1775   | 18/18/1386   | 19/25/2316   | 16/16/610   |
| bmb     | 36/42/1950   | 24/30/2482   | 17/17/1496   | 34/40/1775   | 29/29/1386   | 24/33/2316   | 21/21/610   |
| fkf     | 60/67/1950   | 58/68/2482   | 47/47/1496   | 54/76/1775   | 47/47/1386   | 63/81/2316   | 45/45/610   |
| imada   | 76/124/1950  | 57/79/2482   | 44/44/1496   | 97/140/1775  | 85/85/1386   | 75/115/2316  | 59/59/610   |
| all     | 205/275/1950 | 167/233/2482 | 121/121/1496 | 208/288/1775 | 181/181/1386 | 206/296/2316 | 145/145/610 |


|---------+-------------------|
|         | E21               |
|---------+-------------------|
| samf    | 24/33/2850/581    |
| biologi | 17/20/2850/210    |
| bmb     | 24/25/2850/592    |
| fkf     | 63/71/2850/692    |
| imada   | 75/116/2850/861   |
| all     | 212/282/2850/2428 |
```

There are other instances as well, E20 and E21re, however you can focus
on the above only with precedence to F22, F21 and E21. 

The Python code provided reads the instances and makes available:
- `config` a dictionary with the `DAYS` available for scheduling exams
- `exams` a dictionary with information on the exams to schedule 
- `adj` a dictionary reporting for each pair of exams the list of shared students
- `share` a dictionary reporting for each pair of exams the number of
  shared students
- `rooms` a dictionary with information on the rooms available for scheduling


#### config.json

Data about the days available for scheduling and the parameter
`WEIGHT_PROGRAMS` is provided in a json file `config.json` (see below for an example). The
field `DAYS` contains a list of days with weekends and holidays already
removed. The days are given as a number from `DAYONE`. You do NOT need
to convert them back in dates. The other fields in the input data are
not relevant for this assignment.


```
 {
     "DISTANCE": 3,
     "SEMESTER": "e2020",
     "SESSION": 0,
     "MAX_SEATS_PER_DAY": 300,
     "MAX_ROOMS_PER_DAY": 20,
     "MAX_STUDENTS_PER_DAY": 16,
     "WEIGHT_PROGRAMS": 100,
     "YEAR": 2021,
     "MAX_EXAMS": 15,
     "MAX_ECTS": 40,
     "FIRST_DAY": [1,4],
     "LAST_DAY": [1,29],
     "MONTH": 1,
     "DAYS": [4,5,...,28,29],
     "DAYONE": "2021-01-01"
} 
```

#### Exams

Data about the exams is provided in a json file consisting of a
dictionary, whose elements are the exams e in E. See the code snippet
below. The key of each exam e in E is the STADS identifier. Then, for
each entry corresponding to an exam the following information is
provided (not all the information is relevant for this assignment):

-   `EKA` the STADS code of the exam. The same as the key.

-   `STADS_ID` the STADS code of the course to which the exam belongs

-   `NAT_code` the corresponding code of the course at the Faculty of
    Natural Sciences. This might not be unique as a course might have
    both a written exam and an oral exam.

-   `title` the title of the course

-   `ECTS` the number of ECTS for the course

-   `Prøveform` the form of the exam: written or oral

-   `stype` a shortname for the form of exam: 'm' for oral and 's' for
    written

-   `Administrationsenhed` the administering unit

-   `institute` the administering institute

-   `ECTS/prøve` the ECTS per exam component

-   `Eksamensperiode` when the exam has to be offered: in the ordinary
    session and in the reexam session

-   `students` a list of students registered to the exam

-   `nstds` the total number of students registered

-   `rdays` duration $r_e$ of the exam expressed in number of required
    days. A written exam requires one day while the number of days of an
    oral exam is the number of students divided by 16, the number of
    students that can be examined orally in one day.

-   `schedule` if the exam has already been scheduled then information
    about the schedule is provided here as a list of days given by the
    pair number of day, date.

-   "Available", when present, is a restriction on the set of days defined in "config.json". When not present the whole set of days defined in "config.json" has to be assumed. 

-   `Faste datoer` preassigned dates the same as the previous field, it
    can be ignored.

-   `joined` a list of exams that must be scheduled jointly, that is
    starting on the same days

-   `conflicting` a list of exams that must necessarily be scheduled in
    different days.

<!-- -->

```
{
 "N300003102": {
        "STADS_ID": "N300003101",
        "NAT_code": "MM531",
        "title": "Differentialligninger II",
        "ECTS": 5,
        "Administrationsenhed": "IMADA",
        "EKA": "N300003102",
        "Prøveform": "Mundtlig prøve",
        "ECTS/prøve": 5.0,
        "Eksamensperiode": "Ordinær/reeksamen",
        "Faste datoer": null,
        "stype": "m",
        "institute": "imada",
        "students": [
            "xxxxxxx",
            "yyyyyyy",
            "zzzzzzz",
            "wwwwwww",
        ],
        "nstds": 4,
        "rdays": 1,
        "joined": [
            "N310004102"
        ],
        "conflicting:" []
    },
...
}
```

##### rooms.json and room_unavailabilities

Details about the rooms are contained in the files `rooms.json` and `room_unavailabilities.json`, which are read and joined together to provide a dictionary `rooms`. See excerpt example below. From this dictionary you will need only the fields: `roomCode`, `seats` and `available`.

```
{
  "room.U93": {
        "id": "room.U93",
        "name": "Odense U93",
        "roomCode": "U93",
        "seats": 50,
        "campus": {
            "name": "Odense"
        },
        "building": {
            "name": "O Campus vej"
        },
        "equipments": "2 Tavler,Fladt gulv,Fleksible møbler,Microfon,Mørklægning,Netstik,Projektor",
        "roomFunctions": [
            {
                "name": "Undervisning"
            }
        ],
        "available": [152, 153, 154, 158, 159, 160, 161, 164, 165, 166, 167, 168, 171, 172, 173, 174, 175, 178, 179]
    }
...
}
```




