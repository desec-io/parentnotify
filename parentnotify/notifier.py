import socket

import dns.name
import dns.rdatatype
import dns.resolver
from dns.message import make_query
from dns.name import root
from dns.opcode import NOTIFY
from dns.query import send_udp

from parentnotify.base import NotifierBase


class Notifier(NotifierBase):
    rrtype: str
    domains: list

    def __init__(self, rrtype, domains, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.rrtype = dns.rdatatype.from_text(rrtype)
        self.domains = map(dns.name.from_text, domains)

    def discover_notify_endpoint(self, domain, parent=None):
        if parent is dns.name.empty:
            qname = domain
        else:
            suffix = parent or dns.name.Name(domain[1:])
            prefix = domain.relativize(suffix)
            qname = dns.name.Name(("_dsync",)) + suffix
            if parent and len(prefix) == 1:  # don't retry the query
                return self.discover_notify_endpoint(qname, dns.name.empty)
            qname = prefix + qname

        try:
            self.logger.debug(f"Querying DSYNC for {qname}")
            answers = dns.resolver.resolve(qname, "DSYNC")
            # TODO check AD bit
            for answer in answers:
                if answer.scheme == 1 and answer.rrtype == self.rrtype:
                    return (answer.target, answer.port)
        except dns.resolver.NXDOMAIN as e:
            if parent is dns.name.empty:
                return
            if parent is None:
                return self.discover_notify_endpoint(
                    domain, e.response(qname).authority[0].name
                )
            return self.discover_notify_endpoint(
                dns.name.Name(("_dsync",)) + parent, dns.name.empty
            )
        except dns.resolver.NoAnswer:
            return

    def notify(self, domain):
        try:
            target, port = self.discover_notify_endpoint(domain)
        except TypeError:
            self.logger.info(f"No endpoint discovered (domain: {domain})")
            return

        target = str(target)
        self.logger.info(
            f"Sending NOTIFY({self.rrtype.name}) to {target}:{port} (domain: {domain})"
        )

        try:
            addrinfo = socket.getaddrinfo(target, port, 0, socket.SOCK_DGRAM)
        except socket.gaierror:
            self.logger.warning(f"Could not resolve {target}:{port} (domain: {domain})")
            return

        msg = make_query(domain, self.rrtype, rdclass="IN", flags=dns.flags.AA)
        msg.set_opcode(NOTIFY)
        # TODO add Report-Channel

        # Attempt one address at a time and break on success.
        excs = []
        for *socket_kwargs, _, sockaddr in addrinfo:
            try:
                sock = socket.socket(*socket_kwargs)
                send_udp(sock, what=msg, destination=sockaddr)
                break
            except Exception as e:
                excs.append(e)
        else:
            raise ExceptionGroup(
                f"Could not send NOTIFY to any target address (domain: {domain})",
                excs,
            )

    def process(self):
        for domain in self.domains:
            self.notify(domain)
