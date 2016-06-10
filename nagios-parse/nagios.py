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
    if source is not None:
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
    else:
        raise ValueError("parse method requires an intput stream")

    # flattens the array conf
    return reduce(add, conf)[1::2]


def parse_alerts(source):
    """
    Parses nagios alerts from nagios.log source
    """
    if source is not None:
        warnings = []
        errors = []
        for line in source:
            line = line.strip()
            err = re.search(r'Error', line)
            warn = re.search(r'Warning', line)
            if err is not None:
                data = re.split(r' Error:', line)
                errors.append(dict(state=err.group(), time=data[0][1:-1],
                                   info=data[1]))
            elif warn is not None:
                data = re.split(r' Warning:', line)
                warnings.append(dict(state=warn.group(), time=data[0][1:-1],
                                     info=data[1]))
            else:
                return
        return dict(warnings=warnings, errors=errors)
    else:
        raise ValueError("parse_alerts method requires an input stream")


if __name__ == "__main__":
    FILE = None if len(argv) == 1 else argv[1]
    if FILE is not None:
        #with open(FILE) as stream, open("out/parse.out", "w+") as out:
        #    out.write(simplejson.dumps(parse(stream), indent=4, sort_keys=False))
        with open(FILE) as stream, open("out/alerts.out", "w+") as out:
            out.write(simplejson.dumps(parse_alerts(stream), indent=4,
                                       sort_keys=False))
