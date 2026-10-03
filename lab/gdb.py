"""Minimal GDB remote-serial client for Dolphin's stub (one client per Dolphin run)."""
import socket, time, re

class Gdb:
    def __init__(self, port=2345, timeout=180):
        t0 = time.time()
        while True:
            try:
                self.s = socket.create_connection(('127.0.0.1', port), timeout=5)
                break
            except OSError:
                if time.time() - t0 > timeout: raise
                time.sleep(0.3)
        self.s.settimeout(10)
        self.buf = b''
        self.running = False

    def _fill(self, timeout=None):
        if timeout is not None: self.s.settimeout(timeout)
        try:
            d = self.s.recv(65536)
        except socket.timeout:
            return False
        finally:
            self.s.settimeout(10)
        if not d: raise ConnectionError('gdb stub closed')
        self.buf += d
        return True

    def _packets(self):
        """Yield complete packet bodies currently buffered."""
        while True:
            m = re.search(rb'\$([^#]*)#..', self.buf, re.S)
            if not m: return
            self.buf = self.buf[m.end():]
            yield m.group(1).decode()

    def _drain(self, quiet=0.4):
        while self._fill(quiet): pass
        for _ in self._packets(): pass
        self.buf = b''

    def _send(self, payload):
        d = payload.encode()
        self.s.sendall(b'$' + d + b'#%02x' % (sum(d) & 0xff))

    def cmd(self, payload):
        self._send(payload)
        while True:
            for body in self._packets():
                if body and not body.startswith('T'):
                    return body
                if body == '' and not payload.startswith('m'):
                    return body
            self._fill()

    def cont(self):
        self._send('c'); self.running = True

    def halt(self):
        if not self.running: return
        self.s.sendall(b'\x03')
        self._drain()
        self.running = False

    def read(self, addr, n):
        was = self.running; self.halt()
        out = b''
        while len(out) < n:
            k = min(0x200, n - len(out))
            out += bytes.fromhex(self.cmd('m%x,%x' % (addr + len(out), k)))
        if was: self.cont()
        return out

    def write(self, addr, data):
        was = self.running; self.halt()
        r = self.cmd('M%x,%x:%s' % (addr, len(data), bytes(data).hex()))
        assert r == 'OK', r
        if was: self.cont()

    def u32(self, addr): return int.from_bytes(self.read(addr, 4), 'big')
