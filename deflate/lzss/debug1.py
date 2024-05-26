from pprint import pprint

from deflate.lzss.chunk_compressor import Lzss

data = 'BanBanananananananananananananananvdsvsDvsFVzx'
lzss = Lzss(window_size=6)
compress_result = lzss.compress(data)
pprint(compress_result)


decompress_result = lzss.decompress(compress_result)
print('---------')
pprint(decompress_result)
print(decompress_result == data)

