import csv
import io
import unittest

from nested_csv.writer import (
    FieldConflictError, NestedDictWriter, build_array_fields,
    generate_fieldnames, parse_key
)


class ArrayFieldsTests(unittest.TestCase):
    def test_build_array_fields(self):
        tests = [
            (['[][].a', '[][].b'],
             [
                 ([[]], []),
                 ([['[]']],
                  [
                      ('[][].a', ['[]', '[]', 'a']),
                      ('[][].b', ['[]', '[]', 'b']),
                  ]),
             ]),
            (['a.b[].d[]', 'a.c[].e[].g', 'a.c[].e[].f[0]', 'a.b.[].d[][].e', 'a.a.b'],
             [
                 ([['a', 'b'], ['a', 'c']], []),
                 ([['a', 'b', '[]', 'd'], ['a', 'c', '[]', 'e']],
                  [
                      ('a.b[].d[]', ['a', 'b', '[]', 'd', '[]']),
                      ('a.c[].e[].g', ['a', 'c', '[]', 'e', '[]', 'g']),
                      ('a.c[].e[].f[0]', ['a', 'c', '[]', 'e', '[]', 'f', 0]),
                  ]),
                 ([['a', 'b', '[]', 'd', '[]']],
                  [
                      ('a.b.[].d[][].e', ['a', 'b', '[]', 'd', '[]', '[]', 'e'])
                  ]),
             ]),
        ]
        for fieldnames, array_fields in tests:
            fields = {name: parse_key(name) for name in fieldnames}
            result = build_array_fields(fieldnames, fields)
            self.assertEqual(result, array_fields, msg='fieldnames : {}'.format(fieldnames))

    def test_conflict(self):
        conflicts = [
            ['a.b[]', 'b[]'],  # level of array not match
            ['a.b[].d[]', 'a.c[].e.f[]'],  # level of array not match on sub-array
            ['a.b[]', 'a[]'],  # level of array not match but prefix matches
            ['a.b[]', '[].a'],  # root level array not match
            ['a.b[]', 'a.c.d[][id]']  # invalid array in array id
        ]
        for conflict in conflicts:
            with self.assertRaises(FieldConflictError, msg='fields : {}'.format(conflict)):
                fields = {name: parse_key(name) for name in conflict}
                build_array_fields(conflict, fields)


class NestedDictWriterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.f = io.StringIO()
        self.r = csv.reader(self.f)

    def read_all(self):
        self.f.seek(0)
        return [row for row in self.r]

    def test_writeheader(self):
        fieldnames = ['a.b.c', 'a.d[].e', 'a.c[][]', 'b', 'b.d[0]', 'b.d[1]', 'b.d[0]']
        w = NestedDictWriter(self.f, fieldnames)
        w.writeheader()
        self.assertEqual(self.read_all(), [fieldnames])

    def test_writeheader_empty(self):
        fieldnames = []
        w = NestedDictWriter(self.f, fieldnames)
        w.writeheader()
        self.assertEqual(self.read_all(), [fieldnames])

    def test_simple(self):
        fieldnames = ['a.b.c', 'abc', 'a.d[0]', 'a.d[1][0]', 'a.d[2].a']
        w = NestedDictWriter(self.f, fieldnames)
        w.writerow({'a': {'b': {'c': 1}, 'd': [3, [4], {'a': 5}]}, 'abc': 2})
        w.writerow({'a': {'b': {'c': 6}, 'd': [8, [9], {'a': 10}]}, 'abc': 7})
        self.assertEqual(self.read_all(), [
            ['1', '2', '3', '4', '5'],
            ['6', '7', '8', '9', '10'],
        ])

    def test_root(self):
        fieldnames = ['']
        w = NestedDictWriter(self.f, fieldnames)
        w.writerows([1, 2, 3, 4])
        self.assertEqual(self.read_all(), [['1'], ['2'], ['3'], ['4']])

    def test_array(self):
        fieldnames = ['a.a[]', 'a.b[].c', 'a.b[].d[]', 'b.c[]', 'b.d[]', 'a.c']
        w = NestedDictWriter(self.f, fieldnames)
        w.writerow({'a': {'a': [1, 2, 3, 4], 'b': [{'c': 5, 'd': [7, 8]}, {'c': 6, 'd': [9, 10, 11]}], 'c': 15},
                    'b': {'c': [12, 13, 14], 'd': []}})
        w.writerow(
            {'a': {'a': [16, 17, 18, 19], 'b': [{'c': 20, 'd': [22, 23]}, {'c': 21, 'd': [24, 25, 26]}], 'c': 30},
             'b': {'c': [27, 28, 29], 'd': []}})
        self.assertEqual(self.read_all(), [
            ['1', '5', '7', '12', '', '15'],
            ['1', '5', '8', '12', '', '15'],
            ['1', '5', '', '12', '', '15'],
            ['2', '6', '9', '13', '', '15'],
            ['2', '6', '10', '13', '', '15'],
            ['2', '6', '11', '13', '', '15'],
            ['3', '', '', '14', '', '15'],
            ['3', '', '', '14', '', '15'],
            ['3', '', '', '14', '', '15'],
            ['4', '', '', '', '', '15'],
            ['4', '', '', '', '', '15'],
            ['4', '', '', '', '', '15'],
            ['16', '20', '22', '27', '', '30'],
            ['16', '20', '23', '27', '', '30'],
            ['16', '20', '', '27', '', '30'],
            ['17', '21', '24', '28', '', '30'],
            ['17', '21', '25', '28', '', '30'],
            ['17', '21', '26', '28', '', '30'],
            ['18', '', '', '29', '', '30'],
            ['18', '', '', '29', '', '30'],
            ['18', '', '', '29', '', '30'],
            ['19', '', '', '', '', '30'],
            ['19', '', '', '', '', '30'],
            ['19', '', '', '', '', '30'],
        ])

    def test_array_empty(self):
        fieldnames = ['a.a[]', 'a.b[].c[]', 'a.d']
        w = NestedDictWriter(self.f, fieldnames)
        w.writerow({'a': {'a': [], 'b': [], 'd': 1}})
        w.writerow({'a': {'a': [], 'b': [], 'd': 2}})
        self.assertEqual(self.read_all(), [
            ['', '', '1'],
            ['', '', '2'],
        ])

    def test_write_id(self):
        fieldnames = ['id', 'a[]']
        w = NestedDictWriter(self.f, fieldnames)
        w.writerow({'a': [1, 2]}, id=100)
        w.writerow({'a': [3, 4, 5], 'id': 200})
        # overwrite id by original data
        w.writerow({'a': [6, 7], 'id': 300}, id=400)
        self.assertEqual(self.read_all(), [
            ['100', '1'],
            ['100', '2'],
            ['200', '3'],
            ['200', '4'],
            ['200', '5'],
            ['300', '6'],
            ['300', '7'],
        ])

    def test_writes_id(self):
        fieldnames = ['id', 'a[]']
        w = NestedDictWriter(self.f, fieldnames)
        w.writerows([
            {'a': [1, 2]},
            {'a': [3]},
            {'a': [4, 5, 6], 'id': 200}
        ], first_id=100)
        self.assertEqual(self.read_all(), [
            ['100', '1'],
            ['100', '2'],
            ['101', '3'],
            ['200', '4'],
            ['200', '5'],
            ['200', '6'],
        ])

    def test_array_id(self):
        fieldnames = ['a[].b', 'a[].c[]', 'a[id]', 'a[].c[id]']
        w = NestedDictWriter(self.f, fieldnames)
        w.writerow({'a': [{'b': 1, 'c': [3, 4, 5]}, {'b': 2, 'c': [6, 7]}]})
        w.writerow({'a': [{'b': 8, 'c': []}]})
        self.assertEqual(self.read_all(), [
            ['1', '3', '0', '0'],
            ['1', '4', '0', '1'],
            ['1', '5', '0', '2'],
            ['2', '6', '1', '0'],
            ['2', '7', '1', '1'],
            ['2', '', '1', '2'],
            ['8', '', '0', '0'],
        ])

    def test_invalid_array_id(self):
        tests = [
            ['a[]', 'b[id]'],  # prefix not match
            ['a[].b', 'a[id].b'],  # "[id]" is not last element
            ['a[]', 'a[][id]']  # invalid array level
        ]
        for fieldnames in tests:
            with self.assertRaises(FieldConflictError, msg='fieldnames : {}'.format(fieldnames)):
                NestedDictWriter(self.f, fieldnames)

    def test_raise_on_missing(self):
        fieldnames = ['a.a', 'a.b[]', 'a.c[0]']
        w = NestedDictWriter(self.f, fieldnames, raise_on_missing=True)
        # empty array is not error
        w.writerow({'a': {'a': 1, 'b': [], 'c': [2]}})
        self.assertEqual(self.read_all(), [
            ['1', '', '2'],
        ])
        with self.assertRaises(KeyError):
            w.writerow({'a': {'b': [], 'c': [1]}})
        with self.assertRaises(KeyError):
            w.writerow({'a': {'a': 1, 'c': [1]}})
        with self.assertRaises(IndexError):
            w.writerow({'a': {'a': 1, 'b': [], 'c': []}})

    def test_restval(self):
        fieldnames = ['a.a', 'a.b[]', 'a.c[0]']
        w = NestedDictWriter(self.f, fieldnames, raise_on_missing=False, restval='none')
        # empty array is not error
        w.writerow({'a': {'a': 1, 'b': [], 'c': [2]}})
        w.writerow({'a': {'b': [1], 'c': [2]}})
        w.writerow({'a': {'a': 1, 'c': [2]}})
        w.writerow({'a': {'a': 1, 'b': [2], 'c': []}})
        self.assertEqual(self.read_all(), [
            ['1', 'none', '2'],
            ['none', '1', '2'],
            ['1', 'none', '2'],
            ['1', '2', 'none'],
        ])


class GenerateFieldnamesTests(unittest.TestCase):
    def test_generate_fieldnames(self):
        data = {'a': {'c': [1, 2, 3], 'b': 'value', 'd': [{'e': 4, 'f': 5}], 'g': [[1, 2, 3], [4]]}, 'b': [], 'abc': 1}
        fieldnames = generate_fieldnames(data)
        self.assertEqual(fieldnames,
                         ['a.b', 'a.c[id]', 'a.c[]', 'a.d[id]', 'a.d[].e', 'a.d[].f', 'a.g[id]', 'a.g[][id]', 'a.g[][]',
                          'abc', 'b[id]', 'b[]'])

        data = [{'a': 1, 'b': [{'c': [], 'd': 2}]}]
        fieldnames = generate_fieldnames(data)
        self.assertEqual(fieldnames, ['[id]', '[].a', '[].b[id]', '[].b[].c[id]', '[].b[].c[]', '[].b[].d'])
