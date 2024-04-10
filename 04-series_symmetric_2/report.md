# Symmetric 2
Titus Abele
## Ex 1: CTR
#### 1.
```
If AES-256 is the underlying block cipher and if the nonce is 118-bit long, what is the maximal size a plaintext can have? Justify.
```

Given that AES-256 is the underlying block cipher and the nonce is 118 bits long, the size of the counter will be determined by the remaining bits to reach the block size of AES, which is 128 bits.

So the the size of the counter will be $128 - 118 = 10$ bits.

In CTR mode, each block of the plaintext is XORed with the output of the encryption function applied to a unique nonce/counter combination. Since each nonce/counter combination should be unique, the total number of unique combinations is given by 

$$2^{118} \cdot 2^{10} = 2^{128}$$ 

which corresponds to the total number of possible blocks in AES.

AES operates on blocks of size $128$ bits, the maximal size of plaintext that can be encrypted in a single CTR operation is 

$$128 \cdot 2^{10} = 2^{17}$$

bits.

Maximal plaintext size is $2^{17}$ bits.

#### 2.
```
We decide to use a nonce of 8 bits (still with AES-256). Which new constraint do we have in our system? Be as precise as possible. In particular, this constraint might be different based on the way we choose the nonce.
```

With only 8 bits for the nonce, there are only 

$$2^8 = 256$$

possible unique nonce values. Once all possible nonce values are exhausted, nonce reuse occurs.

We saw in class why, in CTR, nonce reuse can lead to:

$$ (c_1 \oplus c_2) = (m_1 \oplus m_2)$$

Additionnally, with a random nonce, this value drops significantly due to the birthday paradox.


#### 3.
```
A bank comes to you and wants some help with CTR. They are using 3 key 3-DES (key size: 168 bits, block size 64 bits). Here is their usage scenario:

* Changing 3-DES is not an option.
* All transaction are sent using the same key.
* They send 2^30 transactions per year.
* A transaction is at most 226 bits long.
* The symmetric key is changed every year.

They are wondering what nonce size they should use. What do you tell them? Justify.
```

**Triple-DES**

$$c = E_{k_3}(D_{k_2}(E_{k_1}(m)))$$
$$m = D_{k_3}(E_{k_2}(D_{k_1}(m)))$$

* Total number of transactions per year: $2^{30}$ 
* Maximum length of a transaction: $226$ bits
* Block size of 3-DES: $64$ bits

Given that the block size of 3-DES is $64$ bits and each transaction is at most $226$ bits long, we need at least

$$226-64 = 162$$

additionnal bits from the nonce and counter for each transaction to ensure uniqueness. So we need to ensure that the combined nonce and counter space is **much** larger than $2^{30}$.

If we chose a nonce size of $96$ bits we could be fine. CTR uses $64$ bits for the counter so we don't exceed the $162$ bit limit calculated earlier.

$$2^{96} \cdot 2^{64} = 2^{160} \gt\gt 2^{30}$$

unique combinations per key period. 

## Ex 2: IoT Scenarios
```
You are going to analyse two different IoT scenarios in which you will have to make algorithmic choices. To simplify, we will only consider the following five algorithms:

* AES-ECB
* AES-CBC
* AES-CTR
* AES-GCM
* Chacha20-Poly1305
```
```
1. The IoT device sends 256-bit messages to a recipient device. The ciphertext (including tags, IV, . . . ) should have the same size as the plaintext due to physical constraints. We are considering only passive adversaries. Devices do not have any memory except for storing the symmetric key. For each of the five algorithms, justify if it can be used in this scenario or not. You can also slightly modify them. What is your final proposition? Be precise and analyse the security of your answer.
```
