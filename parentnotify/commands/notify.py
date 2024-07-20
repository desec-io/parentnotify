import argparse
import sys

from parentnotify import Notifier


def main():
    description = "Send DNS notifications to the parent"
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        "rrtype",
        help="type of notification to send (CDS)",
        type=str,
    )
    parser.add_argument(
        "domain",
        help="child domain sending the notification",
        type=str,
        nargs="+",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        help="logging verbosity (default: 0)",
        action="count",
        default=0,
    )
    args = parser.parse_args()

    notifier = Notifier(args.rrtype, args.domain, log_level=args.verbose)
    notifier.process()


if __name__ == "__main__":
    main()
