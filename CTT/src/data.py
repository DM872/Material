import os
import sys
import json
import pprint


class Data:

    def __init__(self, dirname):
        self.slots, self.banned = self.read_slots(dirname)
        self.rooms = self.read_rooms(dirname)
        self.events = self.read_events(dirname)
        self.teachers = self.read_teachers(dirname)
        self.students = self.read_students(dirname)
        # pprint.pprint(self.events)

    def read_slots(self, dirname):
        filename = os.path.join(dirname, "timeslots.json")
        with open(filename, mode="r", encoding="utf-8") as filehandle:
            try:
                slots = json.load(filehandle)
            except ValueError as e:
                sys.exit('try to read file: {1} error: {2}'.format(filename, e))
        return slots["slots"], slots["banned"]

    def read_rooms(self, dirname):
        filename = os.path.join(dirname, "rooms.json")
        with open(filename, mode="r", encoding="utf-8") as filehandle:
            try:
                rooms = json.load(filehandle)
            except ValueError as e:
                sys.exit('try to read file: {1} error: {2}'.format(filename, e))
        return rooms

    def read_events(self, dirname):
        filename = os.path.join(dirname, "events.json")
        with open(filename, mode="r", encoding="utf-8") as filehandle:
            try:
                events = json.load(filehandle)
            except ValueError as e:
                sys.exit('try to read file: {1} error: {2}'.format(filename, e))
        print(events.keys())
        return events

    def read_teachers(self, dirname):
        filename = os.path.join(dirname, "teachers.json")
        with open(filename, mode="r", encoding="utf-8") as filehandle:
            try:
                teachers = json.load(filehandle)
            except ValueError as e:
                sys.exit('try to read file: {1} error: {2}'.format(filename, e))
        return teachers

    def read_students(self, dirname):
        filename = os.path.join(dirname, "students.json")
        with open(filename, mode="r", encoding="utf-8") as filehandle:
            try:
                students = json.load(filehandle)
            except ValueError as e:
                sys.exit('try to read file: {1} error: {2}'.format(filename, e))
        return students
