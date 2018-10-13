# zhouqi@20150601
#
# ARCH=X86 or ARCH=sw
ARCH="X86"
CX86="gcc -lpthread  -o sotailf sotailf.c strutils.c daemonize.c aggregation.c"
CSW="swgcc -I/usr/sz/swcc/swgcc-binary/include -L/usr/sz/swcc/swgcc-binary/lib -lpthread  -o sotailf_offset sotailf.c strutils.c daemonize.c aggregation.c"

all: sotailf

sotailf: sotailf.c
	@if test $(ARCH) = sw;then \
		echo $(CSW); \
		sh -c $(CSW); \
	else \
		echo $(CX86); \
		sh -c $(CX86); \
	fi
	
clean:
	rm -f sotailf strutils.o daemonize.o
