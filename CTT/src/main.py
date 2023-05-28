#! /usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import argparse

import data
import model


def main():
    parser = argparse.ArgumentParser(description='MILP solver for timetabling.')
    parser.add_argument(dest="dirname", type=str, help='dirname')
    parser.add_argument("-e", "--example", type=str, dest="example",
                        default="value", metavar="[value1|value2]", help="Explanation [default: %default]")

    args = parser.parse_args()  # by default it uses sys.argv[1:]

    instance = data.Data(args.dirname)


if __name__ == "__main__":
    main()
