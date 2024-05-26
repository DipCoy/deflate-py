from suffix_tree import Tree


def main():
    t = Tree()
    t.add('1', 'a')
    t.add('1', 'b')

    print(t.find('ab'))
    return

    for i, p in t.find_all('a'):
        print(p)


if __name__ == '__main__':
    main()
