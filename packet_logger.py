# Import required Ryu SDN framework modules
from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER, CONFIG_DISPATCHER, set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet, ethernet, ipv4, tcp, udp


class PacketLogger(app_manager.RyuApp):
    # Specify OpenFlow version (1.3)
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(PacketLogger, self).__init__(*args, **kwargs)

        # Dictionary to store MAC → port mapping (learning switch)
        self.mac_to_port = {}

        print("=== Packet Logger + Firewall Controller Started ===")

    # Function to install flow rules into switch
    def add_flow(self, datapath, priority, match, actions):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        # Define instruction (apply actions)
        inst = [parser.OFPInstructionActions(
            ofproto.OFPIT_APPLY_ACTIONS, actions)]

        # Create flow modification message
        mod = parser.OFPFlowMod(
            datapath=datapath,
            priority=priority,
            match=match,
            instructions=inst
        )

        # Send flow rule to switch
        datapath.send_msg(mod)

    # Triggered when switch connects to controller
    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        print("Switch connected:", datapath.id)

        # Install table-miss flow entry
        # This sends unknown packets to controller
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(
            ofproto.OFPP_CONTROLLER,
            ofproto.OFPCML_NO_BUFFER
        )]

        self.add_flow(datapath, 0, match, actions)

    # Main packet processing function
    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, ev):
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        dpid = datapath.id
        in_port = msg.match['in_port']

        # Parse packet
        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocol(ethernet.ethernet)

        # Ignore LLDP packets (used by controller internally)
        if eth.ethertype == 35020:
            return

        dst = eth.dst
        src = eth.src

        # Learn MAC address (store source MAC and input port)
        self.mac_to_port.setdefault(dpid, {})
        self.mac_to_port[dpid][src] = in_port

        print(f"\nPacket in: DPID={dpid} SRC={src} DST={dst} IN_PORT={in_port}")

        # Extract IPv4 packet
        ip_pkt = pkt.get_protocol(ipv4.ipv4)

        # 🚫 FIREWALL RULE: Block traffic from h1 → h2
        if ip_pkt:
            if ip_pkt.src == "10.0.0.1" and ip_pkt.dst == "10.0.0.2":
                print(f"🚫 BLOCKED TRAFFIC: {ip_pkt.src} → {ip_pkt.dst}")
                return  # Drop packet (no forwarding)

            # Log IP packet details
            print(f"IPv4 Packet: {ip_pkt.src} → {ip_pkt.dst}")

            # Check transport layer protocols
            tcp_pkt = pkt.get_protocol(tcp.tcp)
            udp_pkt = pkt.get_protocol(udp.udp)

            if tcp_pkt:
                print(f"TCP Packet: Port {tcp_pkt.src_port} → {tcp_pkt.dst_port}")
            elif udp_pkt:
                print(f"UDP Packet: Port {udp_pkt.src_port} → {udp_pkt.dst_port}")

        # Learning switch forwarding logic
        # If destination MAC known → forward to specific port
        # Else → flood to all ports
        if dst in self.mac_to_port[dpid]:
            out_port = self.mac_to_port[dpid][dst]
        else:
            out_port = ofproto.OFPP_FLOOD

        # Define forwarding action
        actions = [parser.OFPActionOutput(out_port)]

        # Install flow rule for known destinations
        if out_port != ofproto.OFPP_FLOOD:
            match = parser.OFPMatch(
                in_port=in_port,
                eth_src=src,
                eth_dst=dst
            )

            self.add_flow(datapath, 1, match, actions)

        # Send packet out (forwarding decision)
        out = parser.OFPPacketOut(
            datapath=datapath,
            buffer_id=msg.buffer_id,
            in_port=in_port,
            actions=actions,
            data=msg.data
        )

        datapath.send_msg(out)
