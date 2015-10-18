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
#include "queue.h"

static queue myQueue;

void tx(char data)
{
    queue_tx(&myQueue, (uint8_t) data);
}

void print_char(char output)
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

enum {
    packet_size = 460
};

int main(void)
{
    uint16_t x;
    char packet[packet_size + 2];

    for (x = 0; x < packet_size; x++) {
        if ((x % 256) == 0) {
            packet[x] = (char) 0xFF;
        }
        else {
            packet[x] = (char) (x % 256);
        }
    }

    packet[8] = 0;
    packet[197] = 0;

    queue_init(&myQueue);

    tx_packet(packet, packet_size, tx);

    while (queue_has_data(&myQueue)) {
        print_char((char) queue_rx(&myQueue));
    }

    printf("\n");

    return EXIT_SUCCESS;
}
