/*
 * queue.c
 *
 *  Created on: Aug 16, 2013
 *      Author: nrclark
 */

#include <stdint.h>
#include <stdbool.h>
#include <assert.h>
#include "queue.h"

#define QUEUE_MASK (QUEUE_SIZE - 1)

static inline bool is_pow2(uint32_t value)
{
    uint8_t num_ones = 0;

    while (value != 0) {
        if (value & 0x1) {
            num_ones++;

            if (num_ones > 1) {
                return false;
            }
        }

        value = (value >> 1) & 0x7FFFFFFF;
    }

    return true;
}

void queue_init(queue *myQueue)
{
    uint32_t x;

    assert(QUEUE_SIZE != 0);
    assert(is_pow2(QUEUE_SIZE));

    myQueue->tx_index = 0;
    myQueue->rx_index = 0;
    myQueue->level = 0;

    for (x = 0; x < QUEUE_SIZE; x++) {
        myQueue->storage[x] = 0;
    }
}

void queue_tx(queue *myQueue, uint8_t input)
{
    assert(myQueue->level >= 0);
    assert(myQueue->level < QUEUE_SIZE);
    myQueue->storage[(myQueue->tx_index & QUEUE_MASK)] = input;
    myQueue->tx_index++;
    myQueue->level++;
}

bool queue_has_data(queue *myQueue)
{
    return (myQueue->level > 0);
}

int32_t queue_get_level(queue *myQueue)
{
    return myQueue->level;
}

uint8_t queue_rx(queue *myQueue)
{
    uint8_t retval;

    assert(myQueue->level > 0);

    retval = myQueue->storage[(myQueue->rx_index & QUEUE_MASK)];
    myQueue->rx_index++;
    myQueue->level--;

    return retval;
}
