# nested_csv

[![Actions Status](https://github.com/kawasin73/nested_csv/workflows/Python%20package/badge.svg)](https://github.com/kawasin73/nested_csv/actions)

nested_csv generates CSV from nested `dict` `list` data structure such as JSON.

`nested_csv.NestedDictWriter` have same interface (`writerow`, `writerows`, `writeheader`) with `csv.DictWriter`.

## Install

```bash
$ pip install nested-csv
```

## Dependency

nested_csv requires Python 3.

nested_csv only use standard packages (`csv`, `itertools`, `re`).

## How to Use

### Estimate fields

```python
from nested_csv import generate_fieldnames
data = [
  {"hello": {"world": "value0"}, "list": [[1,2,3], [4,5,6]], "fixed": [1,2]},
  {"hello": {"world": "value1"}, "list": [[7,8], [10,11]], "fixed": [3,4]},
]
fieldnames = generate_fieldnames(data[0])
# ['fixed[id]', 'fixed[]', 'hello.world', 'list[id]', 'list[][id]', 'list[][]']
```

### Generate Nested CSV

```python
import io
from nested_csv import NestedDictWriter
data = [
  {"hello": {"world": "value0"}, "list": [[1,2,3], [4,5,6]], "fixed": [1,2]},
  {"hello": {"world": "value1"}, "list": [[7,8], [10,11]], "fixed": [3,4]},
]
fieldnames = ['hello.world', 'list[id]', 'list[][id]', 'list[][]', 'fixed[1]']
file = io.StringIO()
w = NestedDictWriter(file, fieldnames)
w.writeheader()
w.writerows(data)
file.seek(0)
file.read()
# hello.world,list[id],list[][id],list[][],fixed[1]
# value0,0,0,1,2
# value0,0,1,2,2
# value0,0,2,3,2
# value0,1,0,4,2
# value0,1,1,5,2
# value0,1,2,6,2
# value1,0,0,7,4
# value1,0,1,8,4
# value1,1,0,10,4
# value1,1,1,11,4
```

## Field Format

You can generate fields format automatically by using `generate_fieldnames()`.

But `generate_fieldnames()` is sometimes not appropriate when ...

- the order of csv row is important
  - `generate_fieldnames()` will generate fields ordered by lexical order
- the base object includes length list
  - `generate_fieldnames()` can't estimate the scheme of empty object

Please set fieldnames manually on those situations.

The format of fieldnames is following.

### nested keys

Nested dict key is joined by `.` (dot).

```
JSON : {"a": {"b": 1, "c": 2}}
format : ["a.b", "a.c"]
--- CSV ---
1,2
```

### id support

`NestedDictWriter` will insert `id` passed on `writerow(rowdict, id=0)` or `writerows(rowdicts, first_id=0)`.

```
JSON : {"a": {"b": 1, "c": 2}}
format : ["id", "a.b", "a.c"]
--- CSV ---
0,1,2
```

### fixed size list

When the size of the list is known, list elements can be specified by index `[<index number>]`.

```
JSON : {"a": [1,2], "b": [0]}
format : ["a[0]", "a[1]", "b[0]"]
--- CSV ---
1,2,0
```

### list

`NestedDictWriter` unfolds the list elements into multiple rows when specified by `[]`.

Nested list is also supported.

The level of each list must match.

- Bad Cases
  - `"a[]"` + `"a.b"` : key and list at same level
  - `"a[]"` + `"b.c[]"` : list level not match
  - `"a[][]"` + `"b[].c[]"` : sub list level not match

The count of unfolding loop is maximum length of list at each level. If list size is shorter than maximum, the value of exceeded index is empty.

```
JSON : {"a": [[{"x": 1}], [{"x": 2}, {"x": 3}]], "b": [4, 5, 6], "c": [[7, 8, 9]]}
format : ["a[][].x", "b[]", "c[][]"]
--- csv ---
1,4,7
,4,8
,4,9
2,5,
3,5,
,5,
,6,
,6,
,6,
```

### list index

The unfolding loop index of list is specified by `[id]`.

```
JSON: {"a": [[1,2,3], [4,5]}
format : ["a[id]", "a[][id]", "a[][]"]
--- csv ---
0,0,1
0,1,2
0,2,3
1,0,4
1,1,5
1,2,
```

## LICENSE

MIT
