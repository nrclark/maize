/*
 * queue.h
 *
 *  Created on: Aug 16, 2013
 *      Author: nrclark
 */

#ifndef QUEUE_H_
#define QUEUE_H_

#include <stdint.h>
#include <stdbool.h>

#define QUEUE_SIZE (8192)  /* Must be a power of two! */

typedef struct queue {
    volatile uint8_t storage[QUEUE_SIZE];
    volatile uint32_t tx_index;
    volatile uint32_t rx_index;
    volatile int32_t level;
} queue;

void queue_init(queue *myQueue);
void queue_tx(queue *myQueue, uint8_t input);
uint8_t queue_rx(queue *myQueue);
bool queue_has_data(queue *myQueue);
int32_t queue_get_level(queue *myQueue);

#endif /* QUEUE_H_ */
