#include <stdint.h>
#include <stdio.h>

int rdseed32_step (uint32_t *seed)
{
	unsigned char ok;

    // The rdseed instruction is used to generate random numbers
    // rdseed %0 puts the random number in the first operand
    // setc %1 sets the carry flag if the operation was successful
    // if the carry flag is set, the random number is stored in *seed
    // otherwise, *seed is not modified
	asm volatile ("rdseed %0; setc %1" : "=r" (*seed), "=qm" (ok));

	return (int) ok;
}


int main() {
    uint32_t seed = 0;
    rdseed32_step(&seed);
    if (seed == 0) {
        printf("[Error] There was no available seed at the time RDSEED was called!\n");
        return 1;
    }
    printf("Seed: %u\n", seed);
    printf("Size of seed: %lu bytes\n", sizeof(seed));
    return 0;
}