SRCS := $(wildcard src/*.c) $(wildcard src/*.h)

format:
	astyle --options=astyle.options $(SRCS)
