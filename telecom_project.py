import numpy as np
import heapq
import random


# ==================================================
# ||              APPLICATION LAYER               ||
# ==================================================
# encode() -> Text to binary conversion
# decode() -> Binary back to original text

class ApplicationLayer:

    def encode(self, text):
        bits = ''.join(format(ord(c), '08b') for c in text)
        header = format(len(text), '016b') + "01"
        return header + bits

    def decode(self, bits):
        if len(bits) < 18:
            return ""

        header = bits[:18]
        length = int(header[:16], 2)

        data = bits[18:18 + length * 8]

        if len(data) < length * 8:
            chars = [
                chr(int(data[i:i+8], 2))
                for i in range(0, len(data), 8)
                if i + 8 <= len(data)
            ]
        else:
            chars = [
                chr(int(data[i:i+8], 2))
                for i in range(0, len(data), 8)
            ]

        return "".join(chars)


# ==================================================
# ||               TRANSPORT LAYER                ||
# ==================================================
# process() -> Splits data into segments
# extract() -> Reconstructs original data
# Simulates TCP/UDP communication

class TransportLayer:

    def __init__(self, protocol="TCP"):
        self.protocol = protocol
        self.window = 4

    def process(self, data):

        # Split into 32-bit segments
        segments = [data[i:i+32] for i in range(0, len(data), 32)]

        out = ""

        if self.protocol == "TCP":

            # Add sequence numbers
            for i, seg in enumerate(segments):
                seq = format(i, '08b')
                out += "1010" + seq + seg

        else:

            # UDP style
            for seg in segments:
                out += "0000" + seg

        return out

    def extract(self, data):

        res = ""
        i = 0

        while i < len(data):

            # TCP packet
            if i + 4 <= len(data) and data[i:i+4] == "1010":

                if i + 44 <= len(data):
                    seg = data[i+12:i+44]
                    res += seg
                    i += 44
                else:
                    break

            # UDP packet
            elif i + 4 <= len(data):

                if i + 36 <= len(data):
                    seg = data[i+4:i+36]
                    res += seg
                    i += 36
                else:
                    break

            else:
                break

        return res


# ==================================================
# ||                NETWORK LAYER                 ||
# ==================================================
# dijkstra() -> Finds shortest route
# route() -> Adds routing information
# receive() -> Removes routing header

class NetworkLayer:

    def __init__(self):

        # Network graph
        self.graph = {
            "A": {"B": 1, "C": 4},
            "B": {"A": 1, "C": 2, "D": 5},
            "C": {"A": 4, "B": 2, "D": 1},
            "D": {"B": 5, "C": 1}
        }

    def dijkstra(self, src, dst):

        pq = [(0, src, [])]
        visited = set()

        while pq:

            cost, node, path = heapq.heappop(pq)

            if node in visited:
                continue

            visited.add(node)
            path = path + [node]

            if node == dst:
                return path

            for nei in self.graph[node]:
                heapq.heappush(
                    pq,
                    (cost + self.graph[node][nei], nei, path)
                )

        return []

    def route(self, data):

        # Find shortest path
        path = self.dijkstra("A", "D")

        # Encode route
        encoded_path = ''.join(
            format(ord(p), '08b') for p in path
        )

        return format(len(path), '08b') + encoded_path + data

    def receive(self, data):

        if len(data) < 8:
            return ""

        l = int(data[:8], 2) \
            if data[:8].replace('0', '').replace('1', '') == '' else 0

        if l == 0:
            return data[8:] if len(data) > 8 else ""

        path_bits = data[8:8 + l * 8]

        return data[8 + l * 8:] \
            if len(data) > 8 + l * 8 else ""


# ==================================================
# ||              DATA LINK LAYER                 ||
# ==================================================
# add_crc() -> Adds parity/error bits
# check_crc() -> Detects transmission errors
# Handles framing

class DataLinkLayer:

    def add_crc(self, data):

        frames = [data[i:i+32] for i in range(0, len(data), 32)]

        out = ""

        for f in frames:

            # Even parity
            count = f.count('1')
            parity = str(count % 2)

            out += "01111110" + f + parity + "01111110"

        return out

    def check_crc(self, data):

        i = 0
        res = ""

        while i < len(data):

            if data[i:i+8] == "01111110":

                j = i + 8

                while j < len(data) and data[j:j+8] != "01111110":
                    j += 1

                frame = data[i+8:j-1]
                parity = data[j-1]

                # Check parity
                if str(frame.count('1') % 2) == parity:
                    res += frame

                i = j + 8

            else:
                i += 1

        return res


# ==================================================
# ||               PHYSICAL LAYER                 ||
# ==================================================
# modulate() -> Bits to BPSK signal
# demodulate() -> Signal back to bits

class PhysicalLayer:

    def modulate(self, bits):

        # BPSK modulation
        return np.array([
            1 if b == '1' else -1
            for b in bits
        ])

    def demodulate(self, signal):

        # Signal to bits
        return "".join([
            '1' if s > 0 else '0'
            for s in signal
        ])


# ==================================================
# ||                   CHANNEL                    ||
# ==================================================
# transmit() -> Adds AWGN noise
# Simulates noisy communication channel

class Channel:

    def transmit(self, signal, snr_db):

        snr = 10 ** (snr_db / 10)

        power = np.mean(signal ** 2)

        noise_power = power / snr

        # AWGN noise
        noise = np.random.normal(
            0,
            np.sqrt(noise_power),
            len(signal)
        )

        return signal + noise


# ==================================================
# ||                  SIMULATOR                   ||
# ==================================================
# run() -> Executes complete OSI-like flow
# Connects all communication layers together

class Simulator:

    def __init__(self):

        self.app = ApplicationLayer()
        self.trans = TransportLayer("TCP")
        self.net = NetworkLayer()
        self.dl = DataLinkLayer()
        self.phy = PhysicalLayer()
        self.channel = Channel()

    def run(self, text, snr_db):

        # Sender side
        bits = self.app.encode(text)
        bits = self.trans.process(bits)
        bits = self.net.route(bits)
        bits = self.dl.add_crc(bits)

        # Physical transmission
        signal = self.phy.modulate(bits)
        noisy = self.channel.transmit(signal, snr_db)

        # Receiver side
        rec_bits = self.phy.demodulate(noisy)
        rec_bits = self.dl.check_crc(rec_bits)
        rec_bits = self.net.receive(rec_bits)
        rec_bits = self.trans.extract(rec_bits)

        output = self.app.decode(rec_bits)

        return output, bits, rec_bits


# ==================================================
# ||               BER FUNCTION                   ||
# ==================================================
# ber() -> Computes Bit Error Rate
# Measures transmission accuracy

def ber(original, received):

    l = min(len(original), len(received))

    err = sum(
        1 for i in range(l)
        if original[i] != received[i]
    )

    return err / l if l > 0 else 0


# ==================================================
# ||                MAIN PROGRAM                  ||
# ==================================================
# Runs communication tests
# Calculates BER for different SNR values
# Generates BER vs SNR graph

if __name__ == "__main__":

    sim = Simulator()

    test_inputs = [
        "HelloWorld",
        "Telecom",
        "Test123"
    ]

    print("=" * 60)
    print("TELECOM COMMUNICATION SYSTEM SIMULATION")
    print("=" * 60)

    for test_text in test_inputs:

        print(f"\n{'='*60}")
        print(f"Test Input: {test_text}")
        print(f"{'='*60}")

        bers = []

        for snr in range(0, 11):

            out, orig, rec = sim.run(test_text, snr)

            ber_value = ber(orig, rec)

            bers.append(ber_value)

            if snr in [0, 5, 10]:

                print(f"\nSNR: {snr} dB")
                print(f"Input  : {test_text}")
                print(f"Output : {out}")
                print(f"Match  : {test_text == out}")
                print(f"BER    : {ber_value:.6f}")

        print(f"\nBER Summary for '{test_text}':")
        print(f"SNR 0 dB  -> BER: {bers[0]:.6f}")
        print(f"SNR 5 dB  -> BER: {bers[5]:.6f}")
        print(f"SNR 10 dB -> BER: {bers[10]:.6f}")

    # BER vs SNR analysis
    print(f"\n{'='*60}")
    print("BER vs SNR Analysis")
    print(f"{'='*60}")

    import matplotlib.pyplot as plt

    snrs = list(range(0, 15))
    bers_bpsk = []

    num_bits = 100000

    random_bits = "".join(
        random.choice(['0', '1'])
        for _ in range(num_bits)
    )

    for snr in snrs:

        signal = sim.phy.modulate(random_bits)

        noisy = sim.channel.transmit(signal, snr)

        rec = sim.phy.demodulate(noisy)

        err = sum(
            1 for i in range(num_bits)
            if random_bits[i] != rec[i]
        )

        ber_val = err / num_bits if err > 0 else 1e-6

        bers_bpsk.append(ber_val)

        print(
            f"Eb/N0: {snr:2d} dB "
            f"-> BPSK BER: {ber_val:.6f}"
        )

    # Plot graph
    plt.figure(figsize=(10, 6))

    plt.semilogy(
        snrs,
        bers_bpsk,
        'b-',
        label='BPSK'
    )

    plt.xlabel("Eb/N0 (dB)")
    plt.ylabel("Bit Error Rate")

    plt.grid(True, which="both", ls="--")

    plt.legend()

    plt.ylim(1e-5, 1)
    plt.xlim(0, 14)

    plt.tight_layout()

    plt.savefig("ber_plot.png")

    print("\nBER graph saved as 'ber_plot.png'")
