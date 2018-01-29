import re
import struct
import array


#*****************************************************************************
#                      Commands 
#*****************************************************************************
class VRTPrint(gdb.Function):
    """ function returns a gdb.Value 
      
    do something like:
        (gdb) p $pvrt(svec)
    """
    def __init__(self):
        super(VRTPrint, self).__init__("pvrt")

    def invoke(self, svec):
        """ you can pass as many parameters as you like"""

        vec_s =  svec["_M_impl"]["_M_start"]
        vec_e =  svec["_M_impl"]["_M_finish"]
        L = int(vec_e - vec_s)
        sm = self._get_pkt_barray(vec_s, L) 

        print(str(sm))

        return "ok" 

    def _get_pkt_barray(self, pvec, L):
        """ returns a byte array of the packet """

        vec = [0]*L
        
        for n,_ in enumerate(vec): 
            vec[n] = int(((pvec + n).dereference()))

        bts = []

        for v in vec:
            bts.extend(int_to_bytes(v))

        return bts
        

VRTPrint()

#*****************************************************************************
#                      Helpful quick ones
#*****************************************************************************
def swap32(val):
    return struct.unpack("<I", struct.pack(">I", val))[0]

def int_to_bytes(val):
    b = [0, 0, 0, 0]
    b[3] = val & 0xFF
    val >>= 8
    b[2] = val & 0xFF
    val >>= 8
    b[1] = val & 0xFF
    val >>= 8
    b[0] = val & 0xFF
    val >>= 8

    return b

#*****************************************************************************
#                       Pretty printers
#*****************************************************************************
class GenericVRTPacketPrinter(object):
    """ Print the Generic VRT Packet """

    def __init__(self, val):
        self.val = val

        self.paktype = {}
        self.paktype["vita49_2::DATA_NO_STREAM"] = "DATA_NO_STREAM"
        self.paktype["vita49_2::DATA_WITH_STREAM"] = "DATA_WITH_STREAM"
        self.paktype["vita49_2::EXT_DATA_NO_STREAM"] = "EXT_DATA_NO_STREAM"
        self.paktype["vita49_2::EXT_DATA_WITH_STREAM"] = "EXT_DATA_WITH_STREAM"
        self.paktype["vita49_2::CONTEXT"] = "CONTEXT"
        self.paktype["vita49_2::EXT_CONTEXT"] = "EXT_CONTEXT"
        self.paktype["vita49_2::COMMAND"] = "COMMAND"
        self.paktype["vita49_2::EXT_COMMAND"] = "EXT_COMMAND"

        self.boolstr = {}
        self.boolstr["true"] = "T"
        self.boolstr["false"] = "F"

        self.tsitype = {}
        self.tsitype["vita49_2::NO_TSI"] = "NO_TSI"
        self.tsitype["vita49_2::UTC"] = "UTC"
        self.tsitype["vita49_2::GPS"] = "GPS"
        self.tsitype["vita49_2::OTHER"] = "OTHER"
        
        self.tsftype = {}
        self.tsftype["vita49_2::NO_TSF"] = "NO_TSF"
        self.tsftype["vita49_2::SAMPLE_COUNT"] = "SAMPLE_COUNT"
        self.tsftype["vita49_2::REAL_TIME"] = "REAL_TIME"
        self.tsftype["vita49_2::FREE_RUNNING"] = "FREE_RUNNING"

        self.pkt_size_words = int(self.val["_packetSizeWords"])
        self.pkt_size_bytes = self.pkt_size_words*4
        self.pload_size_bytes = int(self.val["_payloadSizeWords"])*4
        self.pload_offset_bytes = int(self.val["_payloadOffset"])*4
        self.is_trailer = str(self.val["_trailerPresent"]) == "true"
        #This is a pointer to the actual data. To get a value you must use
        #dereference()
        self.packet_std_vec =  self.val["_packetData"]["_M_impl"]["_M_start"]

    def to_string(self):
        
        ss = ("*** GeneralVRTPacket ***\n"  
        " ------------------------------------------------------------------------------ \n"
        "                         HEADER (1 Word, Mandatory)                             \n"
        " ------------------------------------------------------------------------------ \n"
        " Packet Type            C T  R R     TSI        TSF       Pkt Count Pkt Size    \n"
        " --------------------   - -  ---   ------   ------------  --------- ---------   \n"
        " {0: >20}   {1} {2}  {3} {4}   {5: >6}   {6: >12}\33[33m{7: >11}\33[0m{8: >8}                \n"
        "                                                                                \n"
        " Trailer Present: {9}                                                           \n"
        "    Payload Size: {10: <11} [bytes]                                                  \n"
        "  Payload Offset: {11: <11} [bytes]                                                  \n"
        "                                                                                \n"
        " ------------------------------------------------------------------------------ \n")

        rs = ss.format(self.paktype[str(self.val["_packetType"])],
                       self.boolstr[str(self.val["_classIdentifierPresent"])],
                       self.boolstr[str(self.val["_indicator26"])],
                       self.boolstr[str(self.val["_indicator25"])],
                       self.boolstr[str(self.val["_indicator24"])],
                       self.tsitype[str(self.val["_TSI"])],
                       self.tsftype[str(self.val["_TSF"])],
                       str(self.val["_packetCount"]),
                       self.pkt_size_bytes,
                       self.val["_trailerPresent"],
                       self.pload_size_bytes,
                       self.pload_offset_bytes 
                       )             


        bts = self._get_payload_carray()

        #for b in bts:
        #    rs += str(b) + " "

        #rs += str(self._get_payload_carray())
        rs += self._render_complex_array()
        
        rs += "      .\n"
        rs += "      .\n"
        rs += "      .\n"

        if self.is_trailer:
            rs += (" ------------------------------------------------------------------------------  \n"
                  "                             Trailer \33[32mIS\33[0m Present                     \n" 
                    " ------------------------------------------------------------------------------ \n")
        else:
            rs += (" ------------------------------------------------------------------------------ \n"
                  "                             Trailer \33[31mNOT\33[0m Present                                 \n" 
                   " ------------------------------------------------------------------------------ \n")

        rs += "\n"
            
        return rs 

    def display_hint(self):
        return "GenericVRTPacket"

    def _get_pkt_barray(self):
        """ returns a byte array of the packet """

        pvec =  self.packet_std_vec

        vec = [0]*self.pkt_size_words
        
        for n,_ in enumerate(vec): 
            vec[n] = int(((pvec + n).dereference()))

        bts = []

        for v in vec:
            bts.extend(int_to_bytes(v))

        return bts

    def _get_payload_barray(self):
        """ returns the payload byte array """
        ba = self._get_pkt_barray()
        start = self.pload_offset_bytes
        end = self.pload_offset_bytes + self.pload_size_bytes

        return ba[start:end]

    def _get_payload_sarray(self):
        """ returns array of shorts """
        ba = self._get_payload_barray()
        count = len(ba)/2
        return  struct.unpack('H'*count, bytearray(ba))

    def _get_payload_carray(self):
        """ returns array of complex """
        sa = self._get_payload_sarray()
        count = len(sa)/2
        cs = [0+0j]*count
        for n, a in enumerate(cs):
           cs[n] = complex(sa[2*n], sa[2*n + 1]) 
        return cs

    def _render_complex_array(self):
        ca = self._get_payload_carray()   
        L = len(ca)  
        rows = L / 4
        left_over = L - 4*rows

        ss = ""
        template = "{0:>5} + {1:>5}j | {2:>5} + {3:>5}j | {4:>5} + {5:>5}j | {6:>5} + {7:>5}j\n"
        for n in xrange(15):
        
            ss += template.format( ca[4*n + 0].real , ca[4*n + 0].imag,
                                   ca[4*n + 1].real , ca[4*n + 1].imag,
                                   ca[4*n + 2].real , ca[4*n + 2].imag,
                                   ca[4*n + 3].real , ca[4*n + 3].imag)

        return ss
             
           
            
    


def vrt_lookup_function(val):
    """ add GeneralVRTPacket printer to list """
    lookup_tag = val.type.tag
    if lookup_tag == None:
        return None

    regex = re.compile("GenericVRTPacket");
    if regex.search(lookup_tag):
        return GenericVRTPacketPrinter(val)

    return None
   
#*******************************************************************************
#
#*******************************************************************************
class VrtChunkPrinter(object):
    """ Print the Generic VRT Packet """

    def __init__(self, val):

        self.val = val

        self.paktype = {}
        self.paktype[0] = "DATA_NO_STREAM"
        self.paktype[1] = "DATA_WITH_STREAM"
        self.paktype[2] = "EXT_DATA_NO_STREAM"
        self.paktype[3] = "EXT_DATA_WITH_STREAM"
        self.paktype[4] = "CONTEXT"
        self.paktype[5] = "EXT_CONTEXT"
        self.paktype[6] = "COMMAND"
        self.paktype[7] = "EXT_COMMAND"

        self.boolstr = {}
        self.boolstr["true"] = "T"
        self.boolstr["false"] = "F"

        self.tsitype = {}
        self.tsitype[0] = "NO_TSI"
        self.tsitype[1] = "UTC"
        self.tsitype[2] = "GPS"
        self.tsitype[3] = "OTHER"
        
        self.tsftype = {}
        self.tsftype[0] = "NO_TSF"
        self.tsftype[1] = "SAMPLE_COUNT"
        self.tsftype[2] = "REAL_TIME"
        self.tsftype[3] = "FREE_RUNNING"

        self.pkt_size_words = int(self.val["pktSize"])
        self.pkt_size_bytes = self.pkt_size_words*4
        self.pkt_count = int(self.val["pktCount"])
        self.TSF = int(self.val["fracTimePresTSF"])
        self.TSI = int(self.val["timeStampPresTSI"])
        self.pkt_type = int(self.val["PacketType"]) 
        #This is a pointer to the actual data. To get a value you must use
        #dereference()
        #self.packet_std_vec =  self.val["_packetData"]["_M_impl"]["_M_start"]

    def to_string(self):
        
        ss = ("VRTChunk PktCount: {0:>2}\n" ) 

        rs = ss.format(self.pkt_count)             

        return rs 

    def display_hint(self):
        return "string"



def vrt2_lookup_function(val):
    """ add VrtChunk printer to list """
    lookup_tag = val.type.tag
    if lookup_tag == None:
        return None

    regex = re.compile("VrtChunk");
    if regex.search(lookup_tag):
        return VrtChunkPrinter(val)

    return None

# Make sure there are no pretty printers registered
del gdb.pretty_printers[:]
print gdb.pretty_printers

# Add to list of pretty printers 
#gdb.pretty_printers.append(vrt_lookup_function)
gdb.pretty_printers.append(vrt2_lookup_function)
