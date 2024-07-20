import dns.zone
from dns.name import root

from parentnotify.base import NotifierBase


class Notifier(NotifierBase):
    rrtype: str
    domains: list

    def __init__(self, rrtype, domains):
        self.rrtype = rrtype
        self.domains = domains

    def process(self):
        print(self.rrtype)
        print(self.domains)
