# SDN Packet Logger using Ryu Controller (Mininet)

## 📌 Problem Statement

This project implements a Software Defined Networking (SDN) solution using Mininet and Ryu controller to monitor, log, and control network traffic. It demonstrates controller-switch interaction, flow rule design, and packet-level analysis.

---

## 🎯 Objectives

* Capture and log packets using controller events
* Identify protocol types (TCP/UDP/IP)
* Implement flow rules using OpenFlow
* Demonstrate firewall behavior (allowed vs blocked traffic)

---

## 🛠️ Tools Used

* Mininet
* Ryu Controller
* OpenFlow 1.3
* ovs-ofctl (for flow tables)

---

## 🧩 Topology

* 1 Switch (s1)
* 3 Hosts (h1, h2, h3)

---

## ⚙️ Setup & Execution

### Step 1: Start Controller

```
ryu-manager packet_logger.py
```

### Step 2: Start Mininet

```
sudo mn --topo single,3 --controller remote --switch ovsk,protocols=OpenFlow13
```

---

## 🧪 Test Scenarios

### ✅ Allowed Traffic

```
h2 ping h3
```

Result: Successful communication (0% packet loss)

---

### ❌ Blocked Traffic

```
h1 ping h2
```

Result: 100% packet loss (blocked by controller)

---

### 📊 Performance Test

```
iperf h2 h3
```

Result: TCP throughput measured

---

## 📸 Screenshots

* Controller initialization
* Mininet topology
* Allowed ping result
* Blocked ping result
* Controller logs (IPv4, TCP, BLOCKED TRAFFIC)
* iperf output
* Flow table (ovs-ofctl)

---

## 🔍 Observations

* Controller receives packet_in events and installs flow rules dynamically
* Allowed traffic is forwarded efficiently
* Blocked traffic is dropped at controller level
* Flow table confirms match–action rule installation

---

## ✅ Conclusion

This project successfully demonstrates SDN concepts including packet logging, flow rule design, and traffic control using a Ryu controller in Mininet.

---
