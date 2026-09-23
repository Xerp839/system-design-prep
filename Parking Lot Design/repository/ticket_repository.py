from typing import Dict, Optional

from domain.ticket import Ticket


class TicketRepository:
    def __init__(self):
        self._tickets: Dict[str, Ticket] = {}

    def save(self, ticket: Ticket) -> Ticket:
        self._tickets[ticket.id] = ticket
        return ticket

    def find_by_id(self, ticket_id: str) -> Optional[Ticket]:
        return self._tickets.get(ticket_id)
