# Lab2 - ICR
Titus Abele

## Chall 1 

In the correct EdDSA signing process, $s$ should be calculated as $$((r + h * a) % self.l)$$ where a is the private key. However, in the provided code, $s$ is calculated as $$((r + h * r) % self.l)$$ This introduces a vulnerability because $a$ is not included in the calculation of $s$, which means the private key is not being utilized as it should be.

To exploit this vulnerability and forge a signature for a new message we can simply extract all known values from the given parameters and create our own signature completely bypassing the need for the signer's private key.

The exploit was defined in the method `exploit()` in the `chall1.py` file. The method relies on following step-by-step pseudo code:
    
1. Obtain a valid signature (R, S) for a known message.
2. Calculate the value of h for the known message.
3. Calculate the value of s for the known message using the provided incorrect calculation.
4. Forge a new signature for the new message using the calculated s and the original R.

The output of the code:
```
msg_known = b'Grade of Alexandre Duc at ICR = 6.0'
sig_known = b'eHM1...KCQ=='
True
msg_new = b'My grade in ICR is 6.0'
sig_new = b'HvYY...sBA=='
True
```

## Chall 2

Sending "" to be signed:
```
b'T0vUg8CHzYIJupRYQEMWQeLy6bgEkJYJngFUpwbTg1wFAGppiiUmn40t32ALaQqVUjFpsGgBtQWyJQnSeVTOBA=='
```
This is essentially the same as `khash`

