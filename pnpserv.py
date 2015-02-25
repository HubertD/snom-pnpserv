#! /usr/bin/python
#
# snom multicast telephone discovery
#
#
# Author: Filip Polsakiewicz <filip.polsakiewicz@snom.de>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

import socket
import struct
import sys
import re

from optparse import OptionParser
from string import Template

class snom_phone(object):
    """Basic representation of a snom phone."""

    def __init__(self, mac=None, ip=None, mod=None, fw=None, subs=None):
        """Default constructor."""
        self.mac_addr = mac
        self.ip_addr = ip
	self.sip_port = 5060
        self.model = mod
        self.fw_version = fw
        self.subscribe = subs

    def __repr__(self):
        """Gets a string representation of the phone"""
        return "%s (MAC: %s) running Firmware %s found at IP %s" % (self.model, self.__macrepr(self.mac_addr), self.fw_version, self.ip_addr)

    def __macrepr(self, m):
        """ Normalize a MAC address to lower case unix style """  
        m = re.sub("[.:-]", "", m)
        m = m.lower()
        n =  "%s:%s:%s:%s:%s:%s" % (m[0:2], m[2:4], m[4:6], m[6:8], m[8:10], m[10:])
        return n

def parse(text):
    """Parses the incoming SUBSCRIBE."""
    try:
        lines = text.split('\r\n')
    
        # Line 1 conatains the SUBSCRIBE and our MAC
        new_phone = snom_phone(subs=text)
        new_phone.mac_addr = lines[0][20:32]
        
        # We can read the IP address from line 2
        new_phone.ip_addr = lines[1][17:].split(';')[0].split(':')[0]
	new_phone.sip_port = lines[1][17:].split(';')[0].split(':')[1]
        
        # The other interesting information can be found in line 7
        model_info = lines[6]
        l_model_info = model_info.split(';')
        new_phone.model = l_model_info[3].split('=')[1][1:-1]
        new_phone.fw_version = l_model_info[4].split('=')[1][1:-1]
        print new_phone
    	
        return new_phone
    except:
        # Parsing failed. Probably not a SUBSCRIBE
        return None


def get_sip_info(text):
    """Get some relevant SIP information which we need in order to generate the responses."""
    
    lines = text.split('\r\n')
    # Some SIP info we need
    call_id = lines[4][9:]
    cseq = lines[5][6]
    via_header = lines[1]
    from_header = lines[2]
    to_header = lines[3]
    
    if options.verbose: print "CallId: " + call_id + "; CSeq: " + cseq + "\r\n";    
    return (call_id, cseq, via_header, from_header, to_header)

def get_ip_address():
	# This is a simple hack to find our IP address
	# AFAIK this is the only platform-independent way to obtain the address

	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    	s.connect(('snom.com', 0))
    	return s.getsockname()[0]

prov_uri = None
parser = OptionParser()
parser.add_option('-u', '--url', action="store", dest="prov_uri", help="URI of the provisioning server")
parser.add_option('-l', '--local-ip', action="store", dest="local_ip", help="Local IP address")
parser.add_option("-v", "--verbose",
                  action="store_true", dest="verbose", default=False,
                  help="make lots of noise")

(options, args) = parser.parse_args()


print """                                                                                
                                                                                
                                                                                
      .ijjt;     ..... :tjt:           LLLi    ..... .ijt,    :tjt:             
    .LLLLLLLLL,  LLLLtLLLLLLL      ,ft LLLLL.  LLLLLjLLLLLL .LLLLLLL            
    LLLLLLLLLLLt LLLLLLLLLLLL;   :LLLj LLLLLL  fLLLLLLLLLLLLLLLLLLLLt           
   tLLLf,,iLLLt  LLLLLLfLLLLLf. :LLLLf  :LLLLj fLLLLLffLLLLLLLfLLLLLL           
   LLLL     :t   LLLLL   jLLLf. LLLLL:   :LLLL fLLLL.  :LLLLL   jLLLL           
   LLLLL;.       LLLLt   ,LLLf.;LLLL      LLLL.fLLLL    LLLLj   :LLLL           
   jLLLLLLLLf,   LLLLt   ,LLLf.fLLL;      LLLL:fLLLL    LLLLj   .LLLL           
    LLLLLLLLLLL  LLLLt   ,LLLf.LLLL:      fLLL:fLLLL    LLLLj   .LLLL           
     ,fLLLLLLLLt LLLLt   ,LLLf.LLLL.      LLLL.fLLLL    LLLLj   .LLLL           
         :iLLLLL LLLLt   ,LLLf.LLLL,     .LLLL fLLLL    LLLLj   .LLLL           
    L;      LLLL LLLLt   ,LLLf.jLLLj    .LLLLf fLLLL    LLLLj   .LLLL           
   iLL:    .LLLL LLLLt   ,LLLf.iLLLL   ;fLLLL; fLLLL    LLLLj   .LLLL           
  tLLLLLjjfLLLL; LLLLt   ,LLLf. LLLLf. fLLLLf  fLLLL    LLLLj   .LLLL           
   fLLLLLLLLLLf  LLLLt   ,LLLf. ;LLLLL jLLLt   fLLLL    LLLLj   .LLLL           
    ,LLLLLLLLi   LLLLt   ,LLLf.  iLLLL tf;     LLLLL    LLLLj   .LLLL           
       :,,:.                      .jLL                                          
"""
print "\nsnom multicast PnP Provisioning Server (mcserv)\n"
print "(c) 2008-2009 snom technology AG\n"
print "=" * 80
print "Provisioning URI is %s\n" % options.prov_uri

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind(('224.0.1.75', 5060))
mreq = struct.pack('4sl', socket.inet_aton('224.0.1.75'), socket.INADDR_ANY)
sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
if not options.local_ip:
    ip_adr = get_ip_address()
else:
    ip_adr = options.local_ip
    
print "Local IP Address is :: %s" % ip_adr
print "=" * 80

while True:
    subs = sock.recv(10240)
    
    if options.verbose: print subs
    
    phone = parse(subs)
    (call_id, cseq, via_header, from_header, to_header) = get_sip_info(subs)
    
    if phone:
        # Create a socket to send data
        sendsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
	sendsock.bind(('%s' % ip_adr, 1036))

    	# If a phone has been recognized first send 200 OK
        ok_response = "SIP/2.0 200 OK\r\n"
        ok_response += via_header + "\r\n"
        ok_response += "Contact: <sip:" + phone.ip_addr + ":" + phone.sip_port + ";transport=tcp;handler=dum>\r\n"
        ok_response += to_header + "\r\n"
        ok_response += from_header + "\r\n"
        ok_response += "Call-ID: %s\r\n" % call_id
        ok_response += "CSeq: %s SUBSCRIBE\r\nExpires: 0\r\nContent-Length: 0\r\n" % cseq
        
        sendsock.sendto(ok_response, ("%s" % phone.ip_addr, int(phone.sip_port)))

	# Now send a NOTIFY with the configuration URL
	
	if options.prov_uri:
	    uri_template_string = options.prov_uri
	else:
	    uri_template_string = "http://provisioning.snom.com/${model}/${model}.php?mac=${mac_addr}"

        uri_template = Template(uri_template_string)
	tmpl_data = {"model":phone.model, "mac_addr":phone.mac_addr, "ip_addr":phone.ip_addr, "fw_version":phone.fw_version}
        prov_uri = uri_template.safe_substitute(tmpl_data)

	notify = "NOTIFY sip:%s:%s SIP/2.0\r\n" % (phone.ip_addr, phone.sip_port)
	notify += via_header + "\r\n"
	notify += "Max-Forwards: 20\r\n"
	notify += "Contact: <sip:%s:1036;transport=TCP;handler=dum>\r\n" % ip_adr
	notify += to_header + "\r\n"
	notify += from_header + "\r\n"
	notify += "Call-ID: %s\r\n" % call_id
	notify += "CSeq: 3 NOTIFY\r\n"
	notify += "Content-Type: application/url\r\n"
	notify += "Subscription-State: terminated;reason=timeout\r\n"
	notify += "Event: ua-profile;profile-type=\"device\";vendor=\"OEM\";model=\"OEM\";version=\"7.1.19\"\r\n"
	notify += "Content-Length: %i\r\n" % (len(prov_uri))
	notify += "\r\n%s" % prov_uri

	print "Sending NOTIFY with URI :: %s\n" % prov_uri
        if options.verbose: print notify
	sendsock.sendto(notify, ("%s" % phone.ip_addr, int(phone.sip_port)))
	
