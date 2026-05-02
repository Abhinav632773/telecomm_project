# Telecom Communication System Simulation

## Example Application: Satellite-Based Internet communications 

A modern application of this architecture is satellite communication
In these systems, hundreds to thousands of satellites form a dynamic network in space to provide global internet coverage. Data travels from a user terminal to a satellite, then across multiple satellites, and finally to a ground station.

Each OSI layer plays a critical role:

- The Application Layer handles user data such as web requests, video streaming, or messaging.
- The Transport Layer ensures reliable communication using protocols similar to TCP/UDP, handling segmentation, flow control, and retransmissions.
- The Network Layer performs dynamic routing between satellites, where topology constantly changes due to satellite motion. Algorithms like shortest-path routing are adapted for moving nodes.
- The Data Link Layer ensures reliable communication between adjacent satellites or between satellite and ground station using framing and error detection.
- The Physical Layer manages modulation schemes (like BPSK/QPSK) and signal transmission over radio frequencies.
- The Channel models real-world impairments such as noise, fading, and interference.
- The system evaluates performance under different conditions using metrics like BER vs SNR.

This application is realistic because it directly maps to modern communication infrastructure, where layered design is essential to handle dynamic topology, long distances, and noisy channels.

---

## System Components

### ApplicationLayer
Encodes and decodes data.

### TransportLayer
Breaks binary data into smaller segments and appends sequence number headers.  
Reassembles binary segments back into a contiguous stream by removing the sequence headers.

### NetworkLayer
Implements routing algorithms for packet transmission across nodes.

### DataLinkLayer
Adds CRC for error detection and checks CRC during reception.

### PhysicalLayer
Modulates and demodulates the signal.

### Channel
A virtual channel used for simulation purposes, such as introducing noise (e.g., AWGN).

### Simulator
Calculates performance metrics such as BER vs SNR.
