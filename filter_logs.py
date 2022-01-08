#!/usr/bin/env python3
import fileinput
import re
import sys

allowed_errors = [
    [
        r"WARNING:ANNOUNCEMENT +- Could not build var 'torrentName', missing variable 'if_setregex1'"
    ],
    [
        r"WARNING:ANNOUNCEMENT +- Could not build var 'torrentUrl', missing variable 'extractone1'"
    ],
    [
        r"WARNING:ANNOUNCEMENT +- Could not build var 'torrentUrl', missing variable 'setregex2'"
    ],
    [
        r"WARNING:ANNOUNCEMENT +- Extract: Variable 'extract1' did not match regex '.tags: ....'"
    ],
    [
        r"WARNING:ANNOUNCEMENT +- Extract: Variable 'extract2' did not match regex '.....;....'"
    ],
    [r"WARNING:ANNOUNCEMENT +- ExtractOne: No matching regex found"],
    [
        r"WARNING:ANNOUNCEMENT +- ExtractTags: Could not extract tags, variable 'varreplace1' not found"
    ],
    [
        r"WARNING:ANNOUNCEMENT +- HTTP header .e.g. cookie. in tracker configuration not supported. This might cause problems downloading the torrent file."
    ],
    [
        r"WARNING:ANNOUNCEMENT +- If: Could not check condition, variable 'setregex1' not found"
    ],
    [r"WARNING:ANNOUNCEMENT +- Missing torrent URL"],
    [r"WARNING:ANNOUNCEMENT +- Missing torrent name"],
    [r"WARNING:ANNOUNCEMENT +- SetRegex: Could not set variable, 'extract4' not found"],
    [
        r"WARNING:ANNOUNCEMENT +- SetRegex: Could not set variable, 'extractone1' not found"
    ],
    [
        r"WARNING:ANNOUNCEMENT +- VarReplace: Could not replace, variable 'extract5' not found"
    ],
    [
        r"WARNING:ANNOUNCE_PARSER +- Single: No match found for 'this is a name  -  cow. ¤..- #angry#  -  pasta and sauce'"
    ],
    [
        r"WARNING:BACKEND +- No valid JSON reply from my_(sonarr|lidarr|radarr)",
        r"Traceback .most recent call last.:",
        r"TypeError: string indices must be integers",
    ],
    [
        r"WARNING:MANAGER +- single: Tracker seems to require cookies to download torrent files. Sonarr.Radarr.Lidarr API does not support cookies"
    ],
    [r"WARNING:WEB-HANDLER *- Could not find the requested backend 'nonexistent'"],
    [r"WARNING:IRC:.+ - Unknown command: "],
    [
        r"Could not access backend 'http://localhost:7880/api/v3/diskspace': Cannot connect to host localhost:7880",
    ],
    [
        r"Could not access backend 'http://localhost:7880/api/diskspace': Cannot connect to host localhost:7880",
    ],
    # These logs are seen when arrnounced is shutdown while the IRC clients are
    # connecting. It happens sometimes in test_database_age when restarting
    # arrnounced
    [
        r"ERROR:pydle.client\s+-\s+Failed to execute on_raw_372 handler.",
        r"Traceback \(most recent call last\):",
        r"TypeError: unsupported operand type\(s\) for \+=: 'NoneType' and 'str'",
    ],
    # TODO: Replace werkzeug
    [r"WARNING:werkzeug\s+-\s+\* Running on all addresses"],
    [
        r"WARNING: This is a development server. Do not use it in a production deployment"
    ],
]

if sys.version_info < (3, 8):
    allowed_errors.extend(
        [
            [
                r"ERROR:SESSION\s+-\s+OS error when pushing release to http://localhost:7880",
                r"Traceback .most recent call last.:",
                r"raise exceptions.0.",
                r"raise OSError.err, f'Connect call failed {address}'.",
                r"ConnectionRefusedError: .Errno 111. Connect call failed .'127.0.0.1', 7880.",
                r"The above exception was the direct cause of the following exception:",
                r"Traceback .most recent call last.:",
                r"client_error=client_error",
                r"raise client_error.req.connection_key, exc. from exc",
                r"aiohttp.client_exceptions.ClientConnectorError: Cannot connect to host localhost:7880 ssl:default .Connect call failed .'127.0.0.1', 7880..",
            ],
            [
                r"ERROR:MESSAGE_HANDLER +- Database transaction failed for database transaction title",
                r"Traceback .most recent call last.",
                r"try: raise exc.with_traceback.tb.",
                r"File ..* line",
                r"pony.orm.core.UnexpectedError: Object Announced.new:1. cannot be stored in the database. OperationalError: no such table: Announced",
            ],
        ]
    )
else:
    allowed_errors.extend(
        [
            [
                r"ERROR:SESSION\s+-\s+OS error when pushing release to http://localhost:7880",
                r"Traceback .most recent call last.:",
                r"raise exceptions.0.",
                r"raise OSError.err, f'Connect call failed {address}'.",
                r"ConnectionRefusedError: .Errno 111. Connect call failed .'127.0.0.1', 7880.",
                r"The above exception was the direct cause of the following exception:",
                r"Traceback .most recent call last.:",
                r"raise client_error.req.connection_key, exc. from exc",
                r"aiohttp.client_exceptions.ClientConnectorError: Cannot connect to host localhost:7880 ssl:default .Connect call failed .'127.0.0.1', 7880..",
            ],
            [
                r"ERROR:MESSAGE_HANDLER +- Database transaction failed for database transaction title",
                r"Traceback .most recent call last.",
                r"try: raise exc.with_traceback.tb.",
                r"throw.UnexpectedError, 'Object %r cannot be stored in the database. %s: %s'",
                r"File ..* line",
                r"pony.orm.core.UnexpectedError: Object Announced.new:1. cannot be stored in the database. OperationalError: no such table: Announced",
            ],
        ]
    )

check_matched = [False for _ in allowed_errors]


class Ongoing:
    def __init__(self, rs, line):
        self.rs = rs
        self.offending_line = line
        self.i = 1


def main():
    ongoing = None
    for i, line in enumerate(fileinput.input()):
        matched = False
        if ongoing is None:
            for rs in allowed_errors:
                if re.search(rs[0], line.strip()):
                    # print("Matched", line.strip())
                    # print("     regex: ", rs[0])
                    matched = True
                    if len(rs) > 1:
                        ongoing = Ongoing(rs, line.strip())
                # else:
                #    print("NO Matched", line.strip())
                #    print("     regex: ", rs[0])

        else:
            if re.match(ongoing.rs[ongoing.i], line.strip()):
                matched = True
                if len(ongoing.rs) == (ongoing.i + 1):
                    ongoing = None
                else:
                    ongoing.i = ongoing.i + 1
            else:
                print("-------------- Ongoing failed", line.strip())
                print("-------------- Compared", ongoing.rs[ongoing.i])
                ongoing = None

        if not matched:
            print("----------------", line.strip())
        # else:
        #    print(line.strip())


if __name__ == "__main__":
    main()
