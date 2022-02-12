#!/usr/bin/env python3
"""
Analyze the content of the grouprise-tasks log

Example usage:

  journalctl --output=json --unit=grouprise-tasks \
    | grouprisectl tasks_analyze_log --duration 6h --output-format=json

The log data emitted by the django management command `run_huey` is parsed.
The tasks are analyzed, classified and their timing is gathered.
The resulting summary is emitted as human readable text or JSON.

The input format can be:
- JSON: line-separated dictionaries containing the fields "MESSAGE" and
  "__REALTIME_TIMESTAMP" (microseconds since epoch)
- or the plain output emitted by `journalctl`.

This tool is supposed to help with debugging the utilization and resource consumption of certain
tasks in grouprise.
"""

import collections
import datetime
import enum
import json
import logging
import os
import re
import sys

from django.core.management.base import BaseCommand, CommandError


JOURNALCTL_TEXT_REGEX = re.compile(
    r"^(?P<timestamp>\w+ \d+ [\d:]+) "
    r"(?P<hostname>[\w-]+) "
    r"(?P<process_name>[^ ]+)\[(?P<pid>\d+)\]: "
    r"(?P<message>.*)$"
)
MESSAGE_REXEX = re.compile(
    r"\[(?P<timestamp>[^\]]+),\d+\] (?P<level>[A-Z]+):(?P<details>.*)\.?$"
)
EXCEPTION_REGEX = re.compile(r"^(?P<exception>[\w.]+): (?P<message>.*)$")

Entry = collections.namedtuple("Entry", ("timestamp", "event", "target", "job_id"))


class Command(BaseCommand):
    help = __doc__

    DURATION_REGEX = re.compile(r"(?P<number>\d+(?:\.\d+)?)(?P<unit>[dhm])$")
    DURATION_MULTIPLIER_MAP = {
        "m": datetime.timedelta(minutes=1),
        "h": datetime.timedelta(hours=1),
        "d": datetime.timedelta(days=1),
    }

    def add_arguments(self, parser):
        parser.add_argument(
            "--output-format",
            choices=("json", "text"),
            default="text",
            help="format of the emitted output",
        )
        parser.add_argument(
            "--duration",
            default="1d",
            help=(
                "The wanted amount of log data to be processed (e.g. 'the last 10 minutes')."
                " The numeric value may be suffixed with 'd' (days), 'h' (hours) or 'm' (minutes)."
                " By default numeric values without a suffix are interpreted as hours."
            ),
        )

    def handle(self, *args, **options):
        output_format = options.get("output_format")
        duration_text = options.get("duration").strip().lower()
        duration_match = self.DURATION_REGEX.match(duration_text)
        if not duration_match:
            raise CommandError(
                f"Invalid duration given: '{duration_text}'"
                f" (extected a number optionally followed by one of d/h/m)"
            )
        duration_number = float(duration_match.groupdict()["number"])
        duration_unit = duration_match.groupdict().get("unit", "m")
        duration_multiplier = self.DURATION_MULTIPLIER_MAP[duration_unit]
        duration = duration_multiplier * duration_number
        minimum_timestamp = datetime.datetime.now() - duration
        entries = parse_entries(sys.stdin, minimum_timestamp=minimum_timestamp)
        statistics = assemble_statistics(entries)
        if output_format == "text":
            export_string = export_statistics_text(statistics)
        elif output_format == "json":
            export_string = export_statistics_json(statistics)
        else:
            raise CommandError(f"Unsupported output format: '{output_format}'")
        if export_string:
            self.stdout.write(export_string)


class DurationAssembler:
    """collect multiple durations and calculate count/min/max/average for these values"""

    def __init__(self):
        self.count = 0
        self.min_duration = None
        self.max_duration = None
        self.cumulated_duration = 0

    def add(self, duration):
        if (self.min_duration is None) or (duration < self.min_duration):
            self.min_duration = duration
        if (self.max_duration is None) or (duration > self.max_duration):
            self.max_duration = duration
        self.cumulated_duration += duration
        self.count += 1

    def to_dict(self):
        average = (self.cumulated_duration / self.count) if self.count else None
        return {
            "count": self.count,
            "duration": {
                "min": self.min_duration,
                "max": self.max_duration,
                "average": average,
            },
        }

    def __str__(self):
        if self.count > 0:
            average_duration = self.cumulated_duration / self.count
            return (
                f"{self.count} | "
                f"{self.min_duration:.0f} ... ({average_duration:.3f}) ... {self.max_duration:.0f}"
            )
        else:
            return "None"


class EntryEvent(enum.Enum):
    SCHEDULED = "scheduled"
    STARTED = "started"
    FINISHED = "finished"
    FAILURE = "failure"
    EXCEPTION = "exception"
    QUEUE_ERROR = "queue_error"
    STALE_TASK = "stale_task"
    XAPIAN_LOCKED = "xapian_locked"

    def __lt__(self, other):
        sort_order = (
            EntryEvent.SCHEDULED,
            EntryEvent.STARTED,
            EntryEvent.FINISHED,
            EntryEvent.FAILURE,
            EntryEvent.EXCEPTION,
            EntryEvent.QUEUE_ERROR,
            EntryEvent.STALE_TASK,
            EntryEvent.XAPIAN_LOCKED,
        )
        return sort_order.index(self) < sort_order.index(other)


def parse_entries(source, minimum_timestamp=None):
    last_exception_job_id = None
    current_year = datetime.datetime.now().year
    for line in source:
        if line.startswith("{"):
            data = json.loads(line)
            timestamp = datetime.datetime.fromtimestamp(
                int(data["__REALTIME_TIMESTAMP"]) / 1000000
            )
            message = data["MESSAGE"]
        else:
            log_match = JOURNALCTL_TEXT_REGEX.match(line)
            if not log_match:
                # ignore irregular lines (e.g. "-- Journal begins ...")
                continue
            match_dict = log_match.groupdict()
            timestamp = datetime.datetime.strptime(
                match_dict["timestamp"], "%b %d %H:%M:%S"
            )
            if timestamp.year < 2000:
                timestamp = timestamp.replace(year=current_year)
            message = match_dict["message"]
        message_match = MESSAGE_REXEX.match(message)
        exception_match = EXCEPTION_REGEX.match(message)
        if (minimum_timestamp is not None) and (timestamp < minimum_timestamp):
            continue
        if exception_match:
            match_dict = exception_match.groupdict()
            exception_name = match_dict["exception"]
            exception_message = match_dict["message"]
            logging.debug(
                "Exception parsed: %s -> %s", exception_name, exception_message
            )
            yield Entry(timestamp, EntryEvent.EXCEPTION, None, last_exception_job_id)
        elif message_match:
            match_dict = message_match.groupdict()
            details = match_dict["details"]
            if details.startswith("huey:Worker-") or details.startswith(
                "huey.consumer.Worker:Worker-"
            ):
                if "Unhandled exception in task" in details:
                    # just remember the job ID
                    last_exception_job_id = details.split()[1].rstrip(".")
                    continue
                elif "Error reading from queue" in details:
                    # this may happen due to outdated task names
                    continue
                elif "retries executed in" in details:
                    event = EntryEvent.FINISHED
                    target = details.split(":")[2]
                    job_id = details.split()[1]
                elif "executed in" in details:
                    event = EntryEvent.FINISHED
                    target = details.split(":")[2]
                    job_id = details.split()[1]
                elif ":Executing " in details:
                    event = EntryEvent.STARTED
                    target = details.split()[1].rstrip(":")
                    job_id = details.split()[2]
                elif details.endswith(" retries"):
                    event = EntryEvent.FAILURE
                    target = details.split()[1].rstrip(":")
                    job_id = details.split()[2]
                else:
                    print(f"Unknown worker import line: {details}", file=sys.stderr)
                    continue
            elif ":Enqueueing periodic task " in details:
                event = EntryEvent.SCHEDULED
                target = details.split()[3].rstrip(":")
                job_id = details.split()[4].rstrip(".")
            elif ":MainThread:" in details:
                # management messages
                continue
            else:
                print(f"Unknown import line: {details}", file=sys.stderr)
                continue
            yield Entry(timestamp, event, target, job_id)


def get_event_by_type(events, event_type):
    for event in events:
        if event.event == event_type:
            return event


def assemble_statistics(entries):
    UNSCHEDULED_SUCCESS_EVENTS = frozenset({EntryEvent.STARTED, EntryEvent.FINISHED})
    SCHEDULED_SUCCESS_EVENTS = frozenset(
        {EntryEvent.SCHEDULED, EntryEvent.STARTED, EntryEvent.FINISHED}
    )
    jobs = {}
    for entry in entries:
        job = jobs.setdefault(entry.job_id, [])
        job.append(entry)
    targets = {}
    for entries in jobs.values():
        all_targets = list({item.target for item in entries if item.target is not None})
        target = all_targets[0] if all_targets else "undefined"
        events = frozenset({entry.event for entry in entries})
        start_event = get_event_by_type(entries, EntryEvent.STARTED)
        finish_event = get_event_by_type(entries, EntryEvent.FINISHED)
        schedule_event = get_event_by_type(entries, EntryEvent.SCHEDULED)
        target_summary = targets.setdefault(
            target,
            {
                "target": target,
                "count": 0,
                "delays": DurationAssembler(),
                "durations": DurationAssembler(),
                "problems": {},
                "incomplete": {},
            },
        )
        target_summary["count"] += 1
        if events in {UNSCHEDULED_SUCCESS_EVENTS, SCHEDULED_SUCCESS_EVENTS}:
            duration = (finish_event.timestamp - start_event.timestamp).total_seconds()
            target_summary["durations"].add(duration)
        if {EntryEvent.SCHEDULED, EntryEvent.STARTED}.issubset(events):
            delay = (start_event.timestamp - schedule_event.timestamp).total_seconds()
            target_summary["delays"].add(delay)
        else:
            # count invalid states
            incomplete_states = []
            if (EntryEvent.SCHEDULED in events) and (EntryEvent.STARTED not in events):
                incomplete_states.append("just scheduled")
            if (EntryEvent.FINISHED in events) and (EntryEvent.STARTED not in events):
                incomplete_states.append("missed start")
            for key in incomplete_states:
                target_summary["incomplete"].setdefault(key, 0)
                target_summary["incomplete"][key] += 1
            if not incomplete_states:
                for event in events:
                    if event in SCHEDULED_SUCCESS_EVENTS:
                        continue
                    target_summary["problems"].setdefault(event.value, 0)
                    target_summary["problems"][event.value] += 1
    return targets


def export_statistics_json(targets: dict) -> str:
    exportable = []
    for data in targets.values():
        data["delays"] = data["delays"].to_dict()
        data["durations"] = data["durations"].to_dict()
        exportable.append(data)
    return json.dumps(exportable, indent=2)


def export_statistics_text(targets: dict) -> str:
    lines = []
    for target_name, target_data in targets.items():
        lines.append(f"{target_name}:")
        lines.append(f"    count:                     {target_data['count']}")
        lines.append(f"    durations of success:      {target_data['durations']}")
        lines.append(f"    delays of success:         {target_data['delays']}")
        if target_data["problems"]:
            lines.append("    failures:")
            for key, value in sorted(target_data["problems"].items()):
                label = key + ":"
                lines.append(f"        {label:<22s} {value}")
        if target_data["incomplete"]:
            lines.append("    incomplete:")
            for key, value in sorted(target_data["incomplete"].items()):
                label = key + ":"
                lines.append(f"        {label:<22s} {value}")
    return os.linesep.join(lines)
