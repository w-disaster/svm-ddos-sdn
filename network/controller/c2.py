from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER
from ryu.ofproto import ofproto_v1_3
from ryu.controller.handler import set_ev_cls


class C2(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]   

    def __init__(self, *args, **kwargs):
        super(C2, self).__init__(*args, **kwargs)    

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        # Do not receive Packet In messages
        packet_in_mask = (1 << ofproto.OFPR_NO_MATCH
                & 1 << ofproto.OFPR_ACTION 
                & 1 << ofproto.OFPR_INVALID_TTL)

        # Do not receive port status messages
        port_status_mask = (1 << ofproto.OFPPR_ADD
                        & 1 << ofproto.OFPPR_DELETE
                        & 1 << ofproto.OFPPR_MODIFY)
        
        # Do not receive flow removed messages
        flow_removed_mask = (1 << ofproto.OFPRR_IDLE_TIMEOUT
                         & 1 << ofproto.OFPRR_HARD_TIMEOUT
                         & 1 << ofproto.OFPRR_DELETE)

        # Build request and send msg
        req = parser.OFPSetAsync(datapath, [packet_in_mask, 0], 
                [port_status_mask, 0], [flow_removed_mask, 0])
        datapath.send_msg(req)
