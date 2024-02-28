#include <string.h>
#include <openssl/conf.h>
#include <openssl/evp.h>
#include <openssl/dh.h>
#include <openssl/err.h>
#include <openssl/pem.h>


/**
 * Print openSSL error messages
 */
void handleErrors(void)
{
        ERR_print_errors_fp(stderr);
        abort();
}

/**
 * Encode <length> bits of <input> using base64. Assigns memory for the return value
 */
char* base64_encode(const unsigned char *input, int length)
{
        BIO *bmem, *b64;
        BUF_MEM *bptr;

        b64 = BIO_new(BIO_f_base64());
        bmem = BIO_new(BIO_s_mem());
        b64 = BIO_push(b64, bmem);
        BIO_write(b64, input, length);
        BIO_flush(b64);
        BIO_get_mem_ptr(b64, &bptr);

        char *buff = (char *)malloc(bptr->length);
        memcpy(buff, bptr->data, bptr->length-1);
        buff[bptr->length-1] = 0;

        BIO_free_all(b64);

        return buff;
}


/**
 * Computes the DH secret using the private key pair <keyPair>, the received public part <peerPublicKey>. 
 * The result is stored into <*pSecret> (memory is allocated) and this secret has length <*secretLength>
 */
void computeSecret(EVP_PKEY *keyPair, EVP_PKEY *peerPublicKey, unsigned char **pSecret, size_t *secretLength){
        //TODO
}


/**
 * Generates DH keys. The private part (g, g^x) is stored in <*privateKeyPair> and the public part in a file named <publicKeyFileName> in PEM format. 
 * The context <ctx> has to be provided. 
 */
void generateKeys(EVP_PKEY_CTX* ctx, EVP_PKEY** privateKeyPair, const char* publicKeyFileName){
        //TODO
}

/**
 * Loads the public key <publicKey> given in PEM format from the file <publicKeyFilename>
 */
void receivePublicKey(EVP_PKEY** publicKey, const char* publicKeyFileName){
        //TODO
}

/**
 * Given two derived DH secrets, checks that they are equal and prints their base64. 
 * Alice's secret is <aliceSecret> and has <aliceSecretLength> bytes
 * Bob's secret is <bobSecret> and has <bobSecretLength> bytes
 */
void testSecrets(const unsigned char* aliceSecret, const unsigned char* bobSecret, const size_t aliceSecretLength, const size_t bobSecretLength){
        if(aliceSecretLength != bobSecretLength)
                fprintf(stderr, "missmatch in secret lengths\n");
        for (int i = 0; i < aliceSecretLength; ++i){
                if (aliceSecret[i] != bobSecret[i]){
                        fprintf(stderr, "error in the keys at index %d : %d %d\n", i, aliceSecret[i], bobSecret[i]); 
                        abort();
                }
        }

        char* b64_string = base64_encode(aliceSecret, aliceSecretLength);
        fprintf(stderr, "%s\n", b64_string );
        free(b64_string);
}



int main(){
        //OpenSSl init
        
        //Load the human readable error strings for libcrypto 
        ERR_load_crypto_strings();
        // Load all digest and cipher algorithms
        OpenSSL_add_all_algorithms();
        // Load config file, and other important initialisation 
        CONF_modules_load(NULL, NULL, 0);

        EVP_PKEY * params;
        if(NULL == (params = EVP_PKEY_new())) 
                handleErrors();
        // Use built-in parameters
        DH* values = DH_get_2048_256();
        if(1 != EVP_PKEY_set1_DH(params,values)) 
                handleErrors();

        // Create context for the key generation
        EVP_PKEY_CTX *ctx;
        if(!(ctx = EVP_PKEY_CTX_new(params, NULL))) 
                handleErrors();

        // Generate new keys
        EVP_PKEY *alicekey, *bobkey;
        //TODO 
        
        //Receive public keys
        EVP_PKEY *bobPublicKey, *alicePublicKey;
        //TODO

        unsigned char *bobSecret, *aliceSecret;
        size_t aliceSecretLength, bobSecretLength;
        //TODO compute secret keys

        //Testing and printing
        testSecrets(aliceSecret, bobSecret, aliceSecretLength, bobSecretLength);

        //freeing 
        OPENSSL_free(bobSecret);
        OPENSSL_free(aliceSecret);
        EVP_PKEY_free(alicekey);
        EVP_PKEY_free(bobkey);
        EVP_PKEY_free(alicePublicKey);
        EVP_PKEY_free(bobPublicKey);
        EVP_PKEY_CTX_free(ctx);
        DH_free(values);
        EVP_PKEY_free(params);
        //openSSL cleanup
        
        //Removes all digests and ciphers
        EVP_cleanup();
        CRYPTO_cleanup_all_ex_data();
        //Remove error strings
        ERR_free_strings();
        return 0;
}