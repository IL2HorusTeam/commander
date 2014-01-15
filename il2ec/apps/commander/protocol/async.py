# -*- coding: utf-8 -*-
import simplejson as json

from twisted.protocols.basic import LineOnlyReceiver

from commander import log
from commander.constants import API_OPCODE


LOG = log.get_logger(__name__)


class APIServerProtocol(LineOnlyReceiver):
    """
    This is a twisted implementation of commander-side version of protocol for
    communicating with commander from the outside world.
    """
    def __init__(self):
        self.handlers = {
            API_OPCODE.QUIT: self.on_quit,
        }

    def lineReceived(self, line):
        peer = self.transport.getPeer()

        try:
            code_value, payload = tuple(json.loads(line))
        except Exception as e:
            LOG.error(
                "Failed to decode JSON from {host}:{port} in request "
                "\"{request}\": {err}".format(host=peer.host, port=peer.port,
                                              request=line, err=unicode(e)))
            self.transport.loseConnection()
            return
        try:
            opcode = API_OPCODE.lookupByValue(code_value)
        except ValueError as e:
            LOG.error("Failed to parse opcode '{code}' from {host}:{port} in "
                      "request \"{request}\"".format(code=code_value,
                      host=peer.host, port=peer.port, request=line))
            self.transport.loseConnection()
            return

        handler = self.handlers.get(opcode)
        if handler is None:
            LOG.error("No handler for opcode {opcode}!".format(opcode=opcode))
        else:
            handler(payload)

    def on_quit(self, _):
        self.factory.commander.stop()
