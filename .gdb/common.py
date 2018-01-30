"""
Common utilities for GDB 

"""
# Clear python pretty printers
#gdb.pretty_printers[:] = []

#******************************************************************************
#                           Little Helpers
#******************************************************************************
b_str = {True: "T" , False: "F"}

#******************************************************************************
#                              Commands 
#******************************************************************************
# (gdb) pyval arg0
class PythonGDBValue(gdb.Command):
    """ Prints information out about the gdb.Value passed """

    def __init__(self):
        super(PythonGDBValue, self).__init__("pyval", gdb.COMMAND_SUPPORT,
                                                      gdb.COMPLETE_NONE,
                                                      True)
    def invoke(self, arg, from_tty):
        val = gdb.parse_and_eval(arg)

        print("Type is gdb.Value, you can consult documentation to see " +
              "what methods are available\n")

        print("val.type          = " + str(val.type))
        print("val.type.tag      = " + str(val.type.tag))
        try:
            print("val.type.target() = " + str(val.type.target()))
        except:
            pass
        print("val.type.const()  = " + str(val.type.const()))
        print("val.type.keys(): ")
        try:
            for k in val.type.keys():
                try:
                    print("\n     val[{0}] = {1}\n".format(k, val[k]))
                except Exception as e:
                    print("\n     Key {0} ERROR: {1}\n".format(k, e))
        except:
            pass
PythonGDBValue()

class HereInfo(gdb.Command):
    """ Prints information out about the gdb.Value passed """

    def __init__(self):
        super(HereInfo, self).__init__("pyhere", gdb.COMMAND_SUPPORT,
                                                      gdb.COMPLETE_NONE,
                                                      True)
    def invoke(self, arg, from_tty):
        pc = gdb.selected_frame().pc()
        ln = gdb.find_pc_line(pc)
        #bl = gdb.block_for_pc(pc)
        print("Line Number: \33[33m" + str(ln.line) + "\33[0m")

HereInfo()


class PrettyPrintBreakpoints(gdb.Command):
    """ A cleaner view of the breakpoints 
    
    For more details: bpls   or   info b
    For an individual breakpoint: pybs #
    
    """

    def __init__(self):
        super(PrettyPrintBreakpoints, self).__init__("pybs", 
                                                      gdb.COMMAND_SUPPORT,
                                                      gdb.COMPLETE_NONE,
                                                      True)
        self.type = {}
        self.type[0] = "d0"
        self.type[1] = "breakpoint"
        self.type[2] = "d2"
        self.type[3] = "d3"
        self.type[4] = "d4"
        self.type[5] = "d5"
        self.type[6] = "HW watchpoint"
        self.type[7] = "d7"
        self.type[8] = "d8"

    def invoke(self, arg, from_tty):
        bs = gdb.breakpoints()
      
        if(len(arg) != 0):
            try:
                bnumber = int(arg)
                bvals = [b.number for b in bs]
                if bnumber not in bvals:
                    print("{0} not a breakpoint".format(bnumber))
                    return
                self._print_single(bs, bnumber)
            except Exception as e:
                print e
                print("Call like this: pybs #, where # is the bp number")
                return 


        else:
            if(from_tty):
                self._print_all(bs)
            else:
                print("No color, why bother, use bpls")

    def _print_all(self, bs):
        
        print("")
        print("\33[33m NUM         TYPE       ENABL  Location\33[0m")
        print("------  --------------  -----  --------")
        tp = "{0:>5}:  {1:<14} {2:>4}     {3}"
        if(bs):
            for b in bs:
                if b.is_valid():

                    if(b.location != None):
                        loc =  b.location.split("/")[-1]
                    elif(b.expression != None):
                        loc = b.expression

                    print(tp.format(b.number, 
                                    self.type[b.type],
                                    b_str[b.enabled], loc))

        print("")

    def _print_single(self, bs, bnumber):
        print("")
        print("\33[33m NUM         TYPE       Location\33[0m")
        print("------  --------------  --------")
        tp = "{0:>5}:  {1:<14}   {2}"
        for b in bs:
            if b.is_valid():
                if(b.number == bnumber):
                    if(b.location != None):
                        loc =  b.location
                    elif(b.expression != None):
                        loc = b.expression
                    print(tp.format(b.number, 
                                self.type[b.type],
                                loc))
        print("")
PrettyPrintBreakpoints()


class Framermation(gdb.Command):
    """ Info about frame and block 
    """

    def __init__(self):
        super(Framermation, self).__init__("pyfm", 
                                           gdb.COMMAND_SUPPORT,
                                           gdb.COMPLETE_NONE,
                                           True)

    def invoke(self, arg, from_tty):
        f = gdb.selected_frame()


        block = f.block()

        try:
            print("SUPER Block: " + str(f.block().superblock().function))
        except:
            print("No super block")


            
        print("")
        try:
            print("Above this " + str(f.older().block().function))
        except:
            pass
        print("")
        print("    Dis Block: " + str(f.block().function))
        print("")

        for b in block:
            print "Is argument {0}".format(b.is_argument)
            print "Is constant {0}".format(b.is_constant)
            print "Is function {0}".format(b.is_function)
            print "Name " + b.name
            print "Print Name " + b.print_name
            print "Type {0}".format(b.type) 
            print "Line Number {0}".format(b.line)
            print "Symtab {0}".format(b.symtab)
            print "Is variable {0}".format(b.is_variable)
            print "Is valid {0}".format(b.is_valid())
            try:
                print "Value: " + str(b.value(f))
            except Exception as e:
                print "Need Frame" + str(e)
            
        

Framermation()
