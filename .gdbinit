################################################################################
# Randy Direen
# Started January 2018
################################################################################
# Additional commands 
#
# Python: 
# pyval - how Python sees a value
# pybs - pretty view of breakpoints
# pyfm - pretty view of selected frame
#
# Native:
# main - Start program and stop on main
# asm - view assembly
# bpls - list all breakpoints
# bprml - clear all breakpoints
# bp
# bpc
# bpe
# bpd
# bpt
# stack 
# frame
# flags
# eflags
# reg 
# lib 
# threads 

# set to 1 to enable 64bits target by default (32bit is the default)
set $64BITS = 1

set confirm off
set verbose off
set prompt \033[32mgdb$ \033[0m
set listsize 30

# Display instructions in Intel format
set disassembly-flavor intel

set print pretty on
set print object on
set print static-members on
set print vtbl on
set print demangle on
set print sevenbit-strings off

#*****************************************************************************
#*****************************************************************************
# Python helpers 
#*****************************************************************************
#*****************************************************************************

source ~/.gdb/common.py
source ~/.gdb/vrt.py

#*****************************************************************************
#*****************************************************************************
# Added defines 
#*****************************************************************************
#*****************************************************************************

define main
    tbreak main
    if $argc == 0
        r
    end
    if $argc == 1
        r $arg0
    end
    if $argc == 2
        r $arg0 $arg1
    end
    if $argc == 3
        r $arg0 $arg1 $argr2
    end
    if $argc == 4
        r $arg0 $arg1 $arg2 $arg3
    end
    if $argc == 5
        r $arg0 $arg1 $arg2 $arg3 $arg4
    end
    if $argc == 6
        r $arg0 $arg1 $arg2 $arg3 $arg4 $arg5
    end
    if $argc == 7
        r $arg0 $arg1 $arg2 $arg3 $arg4 $arg5 $arg6
    end
    if $argc == 8
        r $arg0 $arg1 $arg2 $arg3 $arg4 $arg5 $arg6 $arg7
    end

# I could have made this differently, but I like the way it looks.
end
document main
Run program and break on main()

You can pass arguments with main "param1" "param2" etc. Just make sure to use
the quotes!
end

define here
    list *$rip
end
document here
Shows you where you are right now
end

define cmd
    print "Add commands to execute when bp hit, type end when done"
    command $arg0
end
document cmd
Add commands to a breakpoint every  time it's hit. Type end to stop commands.
end

define asm
    if $argc == 0
        disassemble
    end
    if $argc == 1
        disassemble $arg0
    end
    if $argc == 2
        disassemble $arg0 $arg1
    end
end
document asm
Disassemble a specified section of memory.
Default is to disassemble the function surrounding the PC (program counter)
of selected frame. With one argument, ADDR1, the function surrounding this
address is dumped. Two arguments are taken as a range of memory to dump.
Usage: dis <ADDR1> <ADDR2>
end

#*****************************************************************************
# Breakpoints
#*****************************************************************************

define bpls
    info breakpoints
end
document bpls
List all breakpoints.
end

define bprm
    delete breakpoints
end
document bpls
Delete all breakpoints.
end

define bp
    if $argc != 1
        help bp
    else
        break $arg0
    end
end
document bp
Set breakpoint.
Usage: bp LOCATION
LOCATION may be a line number, function name, or "*" and an address.

To break on a symbol you must enclose symbol name inside "".
Example:
bp "[NSControl stringValue]"
Or else you can use directly the break command (break [NSControl stringValue])
end

define bpc 
    if $argc != 1
        help bpc
    else
        clear $arg0
    end
end
document bpc
Clear breakpoint.
Usage: bpc LOCATION
LOCATION may be a line number, function name, or "*" and an address.
end

define bpe
    if $argc != 1
        help bpe
    else
        enable $arg0
    end
end
document bpe
Enable breakpoint with number NUM.
Usage: bpe NUM
end

define bpd
    if $argc != 1
        help bpd
    else
        disable $arg0
    end
end
document bpd
Disable breakpoint with number NUM.
Usage: bpd NUM
end

define bpt
    if $argc != 1
        help bpt
    else
        tbreak $arg0
    end
end
document bpt
Set a temporary breakpoint.
Will be deleted when hit!
Usage: bpt LOCATION
LOCATION may be a line number, function name, or "*" and an address.
end

#*****************************************************************************
# 
#*****************************************************************************
define stack
    if $argc == 0
        info stack
    end
    if $argc == 1
        info stack $arg0
    end
    if $argc > 1
        help stack
    end
end
document stack
Print backtrace of the call stack, or innermost COUNT frames.
Usage: stack <COUNT>
end

define frame
    info frame
    info args
    info locals
end
document frame
Print stack frame.
end

define flags
# OF (overflow) flag
    if (($eflags >> 0xB) & 1)
        printf "O "
        set $_of_flag = 1
    else
        printf "o "
        set $_of_flag = 0
    end
    if (($eflags >> 0xA) & 1)
        printf "D "
    else
        printf "d "
    end
    if (($eflags >> 9) & 1)
        printf "I "
    else
        printf "i "
    end
    if (($eflags >> 8) & 1)
        printf "T "
    else
        printf "t "
    end
# SF (sign) flag
    if (($eflags >> 7) & 1)
        printf "S "
        set $_sf_flag = 1
    else
        printf "s "
        set $_sf_flag = 0
    end
# ZF (zero) flag
    if (($eflags >> 6) & 1)
        printf "Z "
        set $_zf_flag = 1
    else
        printf "z "
        set $_zf_flag = 0
    end
    if (($eflags >> 4) & 1)
        printf "A "
    else
        printf "a "
    end
# PF (parity) flag
    if (($eflags >> 2) & 1)
        printf "P "
        set $_pf_flag = 1
    else
        printf "p "
        set $_pf_flag = 0
    end
# CF (carry) flag
    if ($eflags & 1)
        printf "C "
        set $_cf_flag = 1
    else
        printf "c "
        set $_cf_flag = 0
    end
    printf "\n"
end
document flags
Print flags register.
end

define eflags
    printf "     OF <%d>  DF <%d>  IF <%d>  TF <%d>",\
        (($eflags >> 0xB) & 1), (($eflags >> 0xA) & 1), \
        (($eflags >> 9) & 1), (($eflags >> 8) & 1)
    printf "  SF <%d>  ZF <%d>  AF <%d>  PF <%d>  CF <%d>\n",\
        (($eflags >> 7) & 1), (($eflags >> 6) & 1),\
        (($eflags >> 4) & 1), (($eflags >> 2) & 1), ($eflags & 1)
    printf "     ID <%d>  VIP <%d> VIF <%d> AC <%d>",\
        (($eflags >> 0x15) & 1), (($eflags >> 0x14) & 1), \
        (($eflags >> 0x13) & 1), (($eflags >> 0x12) & 1)
    printf "  VM <%d>  RF <%d>  NT <%d>  IOPL <%d>\n",\
        (($eflags >> 0x11) & 1), (($eflags >> 0x10) & 1),\
        (($eflags >> 0xE) & 1), (($eflags >> 0xC) & 3)
end
document eflags
Print eflags register.
end

define reg
    i registers
end
document reg
Print CPU registers.
end

define smallregisters
 if ($64BITS == 1)
#64bits stuff
# from rax
   set $eax = $rax & 0xffffffff
   set $ax = $rax & 0xffff
   set $al = $ax & 0xff
   set $ah = $ax >> 8
   # from rbx
   set $bx = $rbx & 0xffff
   set $bl = $bx & 0xff
   set $bh = $bx >> 8
   # from rcx
   set $ecx = $rcx & 0xffffffff
   set $cx = $rcx & 0xffff
   set $cl = $cx & 0xff
   set $ch = $cx >> 8
   # from rdx
   set $edx = $rdx & 0xffffffff
   set $dx = $rdx & 0xffff
   set $dl = $dx & 0xff
   set $dh = $dx >> 8
   # from rsi
   set $esi = $rsi & 0xffffffff
   set $si = $rsi & 0xffff
   # from rdi
   set $edi = $rdi & 0xffffffff
   set $di = $rdi & 0xffff     
#3 bits stuff
   else
   # from eax
   set $ax = $eax & 0xffff
   set $al = $ax & 0xff
   set $ah = $ax >> 8
   # from ebx
   set $bx = $ebx & 0xffff
   set $bl = $bx & 0xff
   set $bh = $bx >> 8
   # from ecx
   set $cx = $ecx & 0xffff
   set $cl = $cx & 0xff
   set $ch = $cx >> 8
   # from edx
   set $dx = $edx & 0xffff
   set $dl = $dx & 0xff
   set $dh = $dx >> 8
   # from esi
   set $si = $esi & 0xffff
   # from edi
   set $di = $edi & 0xffff     
  end
   
end
document smallregisters
Create the 16 and 8 bit cpu registers (gdb doesn't have them by default)
And 32bits if we are dealing with 64bits binaries
end

define lib
    info sharedlibrary
end
document lib
Print shared libraries linked to target
end

define threads
    info threads
end
document threads
Print threads in target
end

