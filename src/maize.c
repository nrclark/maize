/*
 ============================================================================
 Name        : maize.c
 Author      : Nick Clark
 Version     :
 Copyright   : BSD License
 Description : Hello World in C, Ansi-style
 ============================================================================
 */

#include <stdio.h>
#include <stddef.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>

void tx(char output, bool bold) {
	static uint16_t count = 0;
	static uint8_t new_line = 1;

	if (new_line) {
		printf("%04d: ", count);
		new_line = 0;
	}

	if(output == '\x00') {
		printf("\033[0;45m");
		printf(" %02X", (uint8_t) output);
		printf("\033[0;34m");
	}

	else if(bold) {
		printf("\033[0;44m");
		printf(" %02X", (uint8_t) output);
		printf("\033[0;34m");
	}
	else {
		printf(" %02X", (uint8_t) output);
		printf("\033[0;34m");
	}

	count++;

	if ((count % 8) == 0) {
		printf("\n");
		new_line = 1;
	}
}

static inline const char * next_block(const char *data, const uint8_t maxlen) {
	uint8_t len;
	uint8_t x;

	for(len = 1; len <= maxlen; len++) {
		if(data[len] == 0) {
			break;
		}
	}

	tx((char)len, true);

	for(x = 1; x < len; x++)
		tx(data[x], false);

	if(len == (maxlen+1))
		len--;

	return data + len;
}

void tx_packet(const char * const data, const uint16_t length) {
	const char *position;
	const char *end;
	ptrdiff_t remaining;
	uint8_t window;

	printf("\033[0;34m");
	tx('\x00', false);

	if(length == 0) {
		tx('\x01', false);
	} else {

		end = data + length - 1;
		remaining = length;
		position = data - 1;

		while(remaining != 0) {
			window = (remaining > 254) ? 254 : (uint8_t) remaining;
			position = next_block(position, window);
			remaining = end - position;
		}
	}

	tx('\x00', false);
}

enum {
	packet_size = 460
};

int main(void) {
	uint16_t x;
	char packet[packet_size + 2];

	for(x = 0; x < packet_size; x++) {
		if((x % 256) == 0)
			packet[x] = 0xFF;
		else
			packet[x] = (x % 256);
	}

	packet[8] = 0;
	packet[197] = 0;

	tx_packet(packet, packet_size);
	printf("\n");

	return EXIT_SUCCESS;
}
