from deflate.lzss.leg import Lz77Compressor, Lz77

c = Lz77(200)
for i in c.compress('БанБананана'):
    print(i)
