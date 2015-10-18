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

#include "maize.h"

int dummy(int op_a, int op_b)
{
    return op_a + op_b;
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

void tx_packet(char *data, uint16_t length, transmitter myTx)
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

        if (*end == '\x00') {
            myTx('\x01');
        }
    }

    myTx('\x00');
}
