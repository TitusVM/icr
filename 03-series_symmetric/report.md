# Symmetric Crypto 1
Titus Abele
## 1 Modus Operandi
| Question                                                      | ECB  | CBC  | CFB  | OFB  | CTR  |
|---------------------------------------------------------------|------|------|------|------|------|
| Does it transform the block cipher into a stream cipher?      |   x   |   x   |   🗸   |   🗸   |   🗸   |
| Is encryption or decryption parallelizable?                   |   🗸   |   x - 🗸   |   x - 🗸   |   🗸   |   🗸   |
| Is partial decryption/reencryption possible?                  |   🗸   |   x   |   x   |   x   |   🗸   |
| Consequences of reusing IV                                    |   No IV   |   Reusing an IV leaks some information about the first block of plaintext, and about any common prefix shared by the two messages   |   Same as CBC   |   Reusing IV causes the creation of the same stream to be created (unless we change the key)   |   Same as CTR   |
| Implications of 1 bit change in ciphertext on plaintext       |   Complete corruption   |   Complete corruption   |   A one bit change in CFB-128 with an underlying 128 bit block cipher, will re-synchronize after two blocks.   |   Flipped bit at the same location   |   Same as CFB   |
| Is padding required?                                          |   🗸   |   🗸   |   x   |   x   |   x   |
| Do you need both encryption and decryption for implementation?|   x   |   x   |   x   |   x   |   x   |
| Attack if IV is predictable?                                  |   [Can be exploited by chosen plaintext](https://stackoverflow.com/questions/3008139/why-is-using-a-non-random-iv-with-cbc-mode-a-vulnerability)   |   Same as ECB   |   [None](https://crypto.stackexchange.com/questions/3515/is-using-a-predictable-iv-with-cfb-mode-safe-or-not)   |   ?   |   I would guess same as ECB   |
| Other security issues?                                        |   Vulnerable to chosen-plaintext attacks (known plaintext attack) due to lack of diffusion   |  Vulnerable to padding oracle attacks, requires padding   |   Vulnerable to bit-flipping attacks   |   Vulnerable to bit-flipping attacks   |   If the same nonce is used with the same key, it leads to a compromise of the confidentiality of the messages   |

## 2 Forensics on SHA-3
To recover the secret password, we could perform a brute-force attack by trying different combinations of characters until we find one that matches the hash stored in the final state of SHA-3. Since we already have the final state, we can use it to verify if a guessed password matches the hash. If we keep trying different passwords until we find a match, it will be the secret password used by the criminal group.


