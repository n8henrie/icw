# History

## 1.0.8 :: 20151114

- Fallback to [`chardet`](https://github.com/chardet/chardet) for UnicodeDecodeError if utf8 doesn't work
- Add some default GA config values to make Travis happy

## 1.0.7 :: 20151113

- Add test file for stripping out BOM (`success_utf8bom.csv`)
- Minor updates to README
- Update dependencies *with the [exception of Flask-WTF](https://github.com/lepture/flask-wtf/commit/b1d77ea962128e8d3b32b9ebea4c36a7cd1b5157#commitcomment-14374763)*
- Update views.py and others to use `unicode_literals` (does *not* perpetuate between modules)
- Add Makefile with `make install`, `make upload` and a few other shortcut commands
- Use `collections.Counter` to compare headers instead of sets (to cover edge cases with duplicates)
- Use scoped session in tests

## 1.0.6 :: 20151111

- Now unicode friendly
- Use `utf-8-sig` to fix rare bug from files encoded with Notepad on PC
- Workaround for unicode in csv module: <https://docs.python.org/2/library/csv.html#examples>
- Another change in version number scheme, should now match GAE / app.yaml

## 0.1.3 :: 20151109

- Use unicode_literals
- Update 500 error with request to contact me
- Update version number to correspond with app.yaml

## 0.1.2 :: 20150727

- Strip out spaces before and after headers instead of throwing an exception

## 0.1.1 :: 20150508

- Use Bootstrap's `alert` styles for error messages
- Update file upload button to use `label` instead of just CSS
- Fix `list.extend` instead of `list.append` for links list

## 0.1

- Initial commit
