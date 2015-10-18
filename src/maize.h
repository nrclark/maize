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
void tx_packet(const char *data, const uint16_t length, const transmitter myTx);
#endif /* MAIZE_H_ */
