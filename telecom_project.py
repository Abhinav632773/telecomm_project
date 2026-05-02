import numpy as np
import heapq
import random

class ApplicationLayer:
    # Converts user text into bitstreams and decodes incoming bits back to text.
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
            chars = [chr(int(data[i:i+8], 2)) for i in range(0, len(data), 8) if i+8 <= len(data)]
        else:
            chars = [chr(int(data[i:i+8], 2)) for i in range(0, len(data), 8)]
        return "".join(chars)


class TransportLayer:
    # Handles data segmentation and sequencing (simulating e.g., TCP behavior).
    def __init__(self, protocol="TCP"):
        self.protocol = protocol
        self.window = 4

    def process(self, data):
        segments = [data[i:i+32] for i in range(0, len(data), 32)]
        out = ""
        if self.protocol == "TCP":
            for i, seg in enumerate(segments):
                seq = format(i, '08b')
                out += "1010" + seq + seg
        else:
            for seg in segments:
                out += "0000" + seg
        return out

    def extract(self, data):
        res = ""
        i = 0
        while i < len(data):
            if i + 4 <= len(data) and data[i:i+4] == "1010":
                if i + 44 <= len(data):
                    seg = data[i+12:i+44]
                    res += seg
                    i += 44
                else:
                    break
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


class NetworkLayer:
    # Computes optimal routing paths across the network using Dijkstra's algorithm.
    def __init__(self):
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
                heapq.heappush(pq, (cost + self.graph[node][nei], nei, path))
        return []

    def route(self, data):
        path = self.dijkstra("A", "D")
        encoded_path = ''.join(format(ord(p), '08b') for p in path)
        return format(len(path), '08b') + encoded_path + data

    def receive(self, data):
        if len(data) < 8:
            return ""
        l = int(data[:8], 2) if data[:8].replace('0','').replace('1','') == '' else 0
        if l == 0:
            return data[8:] if len(data) > 8 else ""
        path_bits = data[8:8 + l * 8]
        return data[8 + l * 8:] if len(data) > 8 + l * 8 else ""


class DataLinkLayer:
    # Responsible for framing data and adding error detection bits (CRC/parity).
    def add_crc(self, data):
        frames = [data[i:i+32] for i in range(0, len(data), 32)]
        out = ""
        for f in frames:
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
                if str(frame.count('1') % 2) == parity:
                    res += frame
                i = j + 8
            else:
                i += 1
        return res


class PhysicalLayer:
    # Modulates bits into analog signals (BPSK) and demodulates them back.
    def modulate(self, bits):
        return np.array([1 if b == '1' else -1 for b in bits])

    def demodulate(self, signal):
        return "".join(['1' if s > 0 else '0' for s in signal])


class Channel:
    # Simulates a noisy transmission medium by adding Additive White Gaussian Noise (AWGN).
    def transmit(self, signal, snr_db):
        snr = 10 ** (snr_db / 10)
        power = np.mean(signal ** 2)
        noise_power = power / snr
        noise = np.random.normal(0, np.sqrt(noise_power), len(signal))
        return signal + noise


class Simulator:
    # Orchestrates the entire OSI-like model data flow from application to physical layer and back.
    def __init__(self):
        self.app = ApplicationLayer()
        self.trans = TransportLayer("TCP")
        self.net = NetworkLayer()
        self.dl = DataLinkLayer()
        self.phy = PhysicalLayer()
        self.channel = Channel()

    def run(self, text, snr_db):
        bits = self.app.encode(text)
        bits = self.trans.process(bits)
        bits = self.net.route(bits)
        bits = self.dl.add_crc(bits)
        signal = self.phy.modulate(bits)
        noisy = self.channel.transmit(signal, snr_db)
        rec_bits = self.phy.demodulate(noisy)
        rec_bits = self.dl.check_crc(rec_bits)
        rec_bits = self.net.receive(rec_bits)
        rec_bits = self.trans.extract(rec_bits)
        output = self.app.decode(rec_bits)
        return output, bits, rec_bits


def ber(original, received):
    l = min(len(original), len(received))
    err = sum(1 for i in range(l) if original[i] != received[i])
    return err / l if l > 0 else 0


if __name__ == "__main__":
    sim = Simulator()
    
    # Test input data
    test_inputs = ["HelloWorld", "Telecom", "Test123"]
    
    print("="*60)
    print("TELECOM COMMUNICATION SYSTEM SIMULATION")
    print("="*60)
    
    for test_text in test_inputs:
        print(f"\n{'='*60}")
        print(f"Test Input: {test_text}")
        print(f"{'='*60}")
        
        bers = []
        outputs = []
        
        for snr in range(0, 11):
            out, orig, rec = sim.run(test_text, snr)
            outputs.append(out)
            ber_value = ber(orig, rec)
            bers.append(ber_value)
            
            # Print details for SNR 0, 5, and 10
            if snr in [0, 5, 10]:
                print(f"\nSNR: {snr} dB")
                print(f"  Input:  {test_text}")
                print(f"  Output: {out}")
                print(f"  Match:  {test_text == out}")
                print(f"  BER: {ber_value:.6f}")
        
        print(f"\nBER Summary for '{test_text}':")
        print(f"  SNR 0 dB  -> BER: {bers[0]:.6f}")
        print(f"  SNR 5 dB  -> BER: {bers[5]:.6f}")
        print(f"  SNR 10 dB -> BER: {bers[10]:.6f}")
    
    # Final simulation with all SNR values
    print(f"\n{'='*60}")
    print("Final BER vs SNR Analysis (Physical Layer: BPSK modulation)")
    print(f"{'='*60}")
    
    sim = Simulator()
    snrs = list(range(0, 15))
    bers_bpsk = []
    
    num_bits = 100000
    random_bits = "".join(random.choice(['0', '1']) for _ in range(num_bits))
    
    for snr in snrs:
        # BPSK Performance
        signal_bpsk = sim.phy.modulate(random_bits)
        noisy_bpsk = sim.channel.transmit(signal_bpsk, snr)
        rec_bpsk = sim.phy.demodulate(noisy_bpsk)
        err_bpsk = sum(1 for i in range(num_bits) if random_bits[i] != rec_bpsk[i])
        ber_bpsk_val = err_bpsk / num_bits if err_bpsk > 0 else 1e-6
        bers_bpsk.append(ber_bpsk_val)
                
        print(f"Eb/N0: {snr:2d} dB -> BPSK BER: {ber_bpsk_val:.6f}")

    import matplotlib
    matplotlib.use('Agg')  # Use non-interactive backend
    import matplotlib.pyplot as plt
    plt.figure(figsize=(10, 6))
    
    # Use semilogy to make the y-axis logarithmic
    plt.semilogy(snrs, bers_bpsk, 'b-', label='BPSK')    
    plt.xlabel("Eb/N0, dB", fontsize=12)
    plt.ylabel("Bit Error Rate", fontsize=12)
    plt.grid(True, which="both", ls="--", color='0.65')
    plt.legend()
    
    # Set limits similar to the image
    plt.ylim(1e-5, 1)
    plt.xlim(0, 14)
    
    plt.tight_layout()
    plt.savefig(r"c:\Users\nabhi\Desktop\telecom project\ber_plot.png", dpi=100)
    print("\n" + "="*60)
    print("Plot saved to: c:\\Users\\nabhi\\Desktop\\telecom project\\ber_plot.png")
    print("="*60)