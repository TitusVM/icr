import secrets
def genBits(nbBits): 
    p = 14219462995139870823732990991847116988782830807352488252401693038616204860083820490505711585808733926271164036927426970740721056798703931112968394409581
    g = 11 # Actual primitive root of p
    x = int(secrets.token_hex(16),16)#16 bytes of pure randomness
    ret = 0
    ths = round((p-1)/2)
    for i in range(nbBits):
        x = pow(g,x,p)
        if x > ths:
            ret += 2**i
    return ret

if __name__== "__main__":
  print("{:0256x}".format(genBits(1024)))
