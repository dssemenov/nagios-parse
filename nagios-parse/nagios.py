"""
This script parses contents of nagios input file and returns JSON data

Basic usage:
    python nagios.py <nagios_file>

Output:
    Stores the output in out/parse.out
"""
# author: dsemenov
from sys import argv
from operator import add
import re
import simplejson


def parse(source):
    """
    Iterates the source file to extract nagios alert data and turns it
    into JSON structure

    This is a slightly modified version of code found on
    http://stackoverflow.com/questions/503148/how-to-parse-nagios-status-dat-file
    """
    conf = []

    for line in source:
        line = line.strip()
        matched_id = re.match(r"(?:\s*define)?\s*(\w+)\s+{", line)
        matched_attr = re.match(r"\s*(\w+)(?:=|\s+)(.*)", line)
        matched_end_attr = re.match(r"\s*}", line)

        if len(line) == 0 or line[0] == '#':
            pass
        elif matched_id:
            identifier = matched_id.group(1)
            cur = [identifier, {}]
        elif matched_attr:
            attribute = matched_attr.group(1)
            value = matched_attr.group(2).strip()
            cur[1][attribute] = value
        elif matched_end_attr and cur:
            conf.append(cur)
            del cur

    # flattens the array conf
    return reduce(add, conf)[1::2]


if __name__ == "__main__":
    FILE = None if len(argv) == 1 else argv[1]
    if FILE is not None:
        with open(FILE) as stream, open("out/parse.out", "w+") as out:
            out.write(simplejson.dumps(parse(stream), indent=4, sort_keys=False))
    else:
        print "Parse method requires an intput stream"
