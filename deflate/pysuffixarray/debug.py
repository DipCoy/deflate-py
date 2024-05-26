from core import SuffixArray


string = 'missisipi'

# при добавлении в конец буквы нужно найти куда вставить следующую букву
# при удалении с концв тоже нужно найти откуда убрать букву и увеличить счётчик на 1

s = SuffixArray(string)
print(s.suffix_array()[1:])
new_s = string[1:] + 'x'
print([_+1 for _ in SuffixArray(new_s).suffix_array()[1:]])
exit(0)
n = 0
for i in range(len(string)):
    s = SuffixArray(string[i:])
    print(string[i:])
    print([_ + n for _ in s.suffix_array()[1:]])
    n += 1

[4, 3, 1, 2]
d = {
    1: 4,
    2: 3,
    3: 1,
    4: 2,
}
