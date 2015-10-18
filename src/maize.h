/*
 * maize.h
 *
 *  Created on: Oct 15, 2015
 *      Author: nick
 */

#ifndef MAIZE_H_
#define MAIZE_H_

#include <stdint.h>

typedef void (*transmitter) (char);
int dummy(int op_a, int op_b);
void tx_packet(char *data, uint16_t length, transmitter myTx);

#endif /* MAIZE_H_ */
