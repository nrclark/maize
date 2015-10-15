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

typedef void (*transmitter) (char);

void tx(char output)
{
    static uint16_t count = 0;
    static uint8_t new_line = 1;

    if (new_line) {
        printf("%04d: ", count);
        new_line = 0;
    }

    if (output == '\x00') {
        printf("\033[0;45m");
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

static inline const char *next_block(const char *restrict data,
                                     const uint8_t maxlen,
                                     const transmitter myTx)
{
    uint8_t len;
    uint8_t x;

    for (len = 1; len <= maxlen; len++) {
        if (data[len] == 0) {
            break;
        }
    }

    myTx((char)len);

    for (x = 1; x < len; x++) {
        myTx(data[x]);
    }

    if (len == (maxlen+1)) {
        len--;
    }

    return data + len;
}

void tx_packet(const char *const data,
               const uint16_t length,
               const transmitter myTx)
{
    const char *restrict position;
    const char *end;
    ptrdiff_t remaining;
    uint8_t window;

    myTx('\x00');

    if (length == 0) {
        myTx('\x01');
    }
    else {

        end = data + length - 1;
        remaining = length;
        position = data - 1;

        while (remaining > 0) {
            window = (remaining > 254) ? 254 : (uint8_t) remaining;
            position = next_block(position, window, myTx);
            remaining = end - position;
        }
    }

    myTx('\x00');
}

enum {
    packet_size = 460
};

int main(void)
{
    uint16_t x;
    char packet[packet_size + 2];

    for (x = 0; x < packet_size; x++) {
        if ((x % 256) == 0) {
            packet[x] = 0xFF;
        }
        else {
            packet[x] = (x % 256);
        }
    }

    packet[8] = 0;
    packet[197] = 0;

    tx_packet(packet, packet_size, tx);
    printf("\n");

    return EXIT_SUCCESS;
}
