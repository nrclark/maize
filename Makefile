
OUTPUT_LIB := libmaize.so

ALL_SRCS := $(wildcard src/*.c) $(wildcard src/*.h)
BUILD_SRCS := $(wildcard src/maize.*) $(wildcard src/queue.*)

OBJS := $(patsubst src/%.c,build/%.o,$(filter %.c,$(BUILD_SRCS)))
DEPS := $(patsubst build/%.o,build/%.d,$(OBJS))

CFLAGS ?= -O0 -g3 -pedantic -Wall -Wextra -Wconversion
CFLAGS := $(CFLAGS) --std=c99 -c -fpic

.DEFAULT_GOAL := $(OUTPUT_LIB)
$(foreach x,$(DEPS),$(eval -include $(x)))

%.o: build/%.o
	cp $< $@

build/%.o : src/%.c
	mkdir -p $(dir $@)
	gcc $(CFLAGS) \
	-MMD -MP -MF"$(basename $@).d" -MT"$(basename $@).o" \
	-o "$(basename $@).o" $<

$(OUTPUT_LIB): $(OBJS)
	gcc -shared -o $@ $^

clean:
	rm -rf build
	rm -f $(OUTPUT_LIB)

format:
	astyle --options=astyle.options $(ALL_SRCS)

