# 📡 Packet Logger using SDN Controller

**Author:** Neha Sachin
**SRN:** PES1UG24CS296
**Section:** 4-E

---

## 📌 Problem Statement

Traditional networks rely on distributed, hardware-based packet forwarding with limited visibility and control. This project implements a **Software-Defined Networking (SDN)** solution that centralizes network control using a Ryu OpenFlow controller. The controller acts as both a **packet logger** and a **firewall**, enabling:

- Real-time packet inspection and logging
- Selective traffic blocking based on source/destination IP rules
- Flow rule installation for efficient forwarding
- Performance monitoring using standard tools

---

## 🎯 Objectives

- Demonstrate controller–switch interaction using OpenFlow 1.3
- Design explicit match–action flow rules for forwarding and filtering
- Observe and measure real network behavior (latency, throughput, packet loss)
- Validate firewall and logging functionality using Mininet, iperf, and flow table inspection

---

## 🛠️ Tech Stack

| Component      | Tool/Framework         |
|----------------|------------------------|
| Network Emulation | Mininet             |
| SDN Controller | Ryu Framework          |
| Protocol       | OpenFlow 1.3           |
| Switch         | Open vSwitch (OVS)     |
| Testing        | iperf, ping, ovs-ofctl |
| Packet Analysis| Wireshark              |

---

## ⚙️ Setup & Execution Steps

### Prerequisites

Make sure the following are installed on your system (Ubuntu 20.04 recommended):

```bash
sudo apt-get update
sudo apt-get install mininet python3-pip wireshark iperf
pip3 install ryu
```

### Step 1 — Clone the Repository

```bash
git clone https://github.com/<your-username>/sdn-packet-logger.git
cd sdn-packet-logger
```

### Step 2 — Start the Ryu Controller

Open a terminal and run:

```bash
ryu-manager packet_logger.py
```

Expected output:
```
=== Packet Logger + Firewall Controller Started ===
instantiating app packet_logger.py of PacketLogger
```

### Step 3 — Launch Mininet Topology

Open a **second terminal** and run:

```bash
sudo mn --topo single,3 --controller remote --switch ovsk,protocols=OpenFlow13
```

This creates:
- 1 switch: `s1`
- 3 hosts: `h1` (10.0.0.1), `h2` (10.0.0.2), `h3` (10.0.0.3)
- Connected to the Ryu controller at `127.0.0.1:6653`

---

## 🧪 Test Scenarios

### Scenario 1 — Allowed Traffic (h2 → h3)

```bash
mininet> h2 ping h3
```

**Expected Output:**
- 0% packet loss
- Controller logs show `IPv4 Packet: 10.0.0.2 → 10.0.0.3`
- Flow rules installed for forwarding

---

### Scenario 2 — Blocked Traffic (h1 → h2) — Firewall Rule

```bash
mininet> h1 ping h2
```

**Expected Output:**
- Packets are intercepted by the controller
- Controller logs show repeated: `🚫 BLOCKED TRAFFIC: 10.0.0.1 → 10.0.0.2`
- No forwarding rule installed; traffic is dropped

---

### Scenario 3 — TCP Throughput Test (h2 → h3)

```bash
mininet> iperf h2 h3
```

**Expected Output:**
```
*** Iperf: testing TCP bandwidth between h2 and h3
*** Results: ['27.5 Gbits/sec', '29.7 Gbits/sec']
```

---

### Scenario 4 — Flow Table Inspection

```bash
mininet> sh ovs-ofctl -O OpenFlow13 dump-flows s1
```

Shows all installed match–action rules including priority, packet counts, byte counts, and output ports.

---

## 📊 Expected Output Summary

| Test | Source | Destination | Result |
|------|--------|-------------|--------|
| Ping | h2 | h3 | ✅ 0% packet loss |
| Ping | h1 | h2 | ❌ Blocked (firewall) |
| iperf TCP | h2 | h3 | ✅ ~27–29 Gbits/sec |
| Flow table | — | — | ✅ Rules installed correctly |

---

## 🔍 Controller Logic Overview

The `packet_logger.py` controller handles:

1. **`EventOFPSwitchFeatures`** — Installs a default table-miss flow rule to send unmatched packets to the controller.

2. **`EventOFPPacketIn`** — Triggered for every new packet:
   - Logs source/destination MAC and IP
   - Checks against **firewall block rules** (e.g., h1 → h2 is blocked)
   - If allowed: installs a **forwarding flow rule** and outputs the packet
   - If blocked: drops the packet and logs `BLOCKED TRAFFIC`

3. **Match–Action Design:**
   - Match on: `in_port`, `eth_src`, `eth_dst`, `ipv4_src`, `ipv4_dst`
   - Action: `OUTPUT` to appropriate port, or `DROP`

---

## 📸 Proof of Execution

Screenshots are available in the `/screenshots` directory and include:

- Controller initialization logs
- Mininet topology setup
- Successful ping between h2 and h3 (0% packet loss)
- Blocked traffic logs (h1 → h2)
- iperf throughput results
- OpenFlow flow table dump

---

## 📚 References

1. Ryu SDN Framework Documentation — https://ryu.readthedocs.io/en/latest/
2. Mininet Documentation — http://mininet.org/walkthrough/
3. OpenFlow 1.3 Specification — https://opennetworking.org/wp-content/uploads/2014/10/openflow-spec-v1.3.0.pdf
4. Open vSwitch Documentation — https://docs.openvswitch.org/
5. B. A. A. Nunes et al., "A Survey of Software-Defined Networking," *IEEE Communications Surveys & Tutorials*, 2014.
