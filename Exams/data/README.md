### Input Data

You are given a starting package containing data on the exams for the last semesters at the Faculty of Science, SDU and some Python code to read the
data.

Data about the days available for scheduling and the parameter
`WEIGHT_PROGRAMS` is
provided in a json file `config.json` (see below for an example). The
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


An instance of the exam schedule problem consists of two files:
`config.json` and a file containing details about the exams to schedule.
Specifically, you are given exams composing five different instances of
the problem with different size and difficulty:

|--|-|-|
||E20|E21|
|--|-|-|
| Exams in samf |      |6|
| Exams in biologi |      8|21|
| Exams in bmb     |     17|36|
| Exams in imada   |     41|76|
| Exams in fkf     |     45|60|
| Exams in all     |    123|205|



The Python code calculates a matrix with the number of shared students
between exams that can turn out relevant for the assignment.
