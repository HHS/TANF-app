import pytest
from ..base import ValidatorFunctions


class TestValidatorFunctions:
    @pytest.mark.parametrize('val, option, kwargs, expected', [
        (1, 1, {}, True),
        (1, 2, {}, False),
        (True, True, {}, True),
        (True, False, {}, False),
        (False, False, {}, True),
        (1, True, {'cast': bool}, True),
        (0, True, {'cast': bool}, False),
        ('1', '1', {}, True),
        ('abc', 'abc', {}, True),
        ('abc', 'ABC', {}, False),
        ('abc', 'xyz', {}, False),
        ('123', '123', {}, True),
        ('123', '321', {}, False),
        ('123', 123, {'cast': int}, True),
        ('123', '123', {'cast': int}, False),
        (123, '123', {'cast': str}, True),
        (123, '123', {'cast': bool}, False),
    ])
    def test_isEqual(self, val, kwargs, option, expected):
        _validator = ValidatorFunctions.isEqual(option, **kwargs)
        assert _validator(val) == expected

    @pytest.mark.parametrize('val, option, kwargs, expected', [
        (1, 1, {}, False),
        (1, 2, {}, True),
        (True, True, {}, False),
        (True, False, {}, True),
        (False, False, {}, False),
        (1, True, {'cast': bool}, False),
        (0, True, {'cast': bool}, True),
        ('1', '1', {}, False),
        ('abc', 'abc', {}, False),
        ('abc', 'ABC', {}, True),
        ('abc', 'xyz', {}, True),
        ('123', '123', {}, False),
        ('123', '321', {}, True),
        ('123', 123, {'cast': int}, False),
        ('123', '123', {'cast': int}, True),
        (123, '123', {'cast': str}, False),
        (123, '123', {'cast': bool}, True),
    ])
    def test_isNotEqual(self, val, option, kwargs, expected):
        _validator = ValidatorFunctions.isNotEqual(option, **kwargs)
        assert _validator(val) == expected

    @pytest.mark.parametrize('val, options, kwargs, expected', [
        (1, [1, 2, 3], {}, True),
        (1, ['1', '2', '3'], {}, False),
        (1, ['1', '2', '3'], {'cast': str}, True),
        ('1', ['1', '2', '3'], {}, True),
        ('1', [1, 2, 3], {}, False),
        ('1', [1, 2, 3], {'cast': int}, True),
    ])
    def test_isOneOf(self, val, options, kwargs, expected):
        _validator = ValidatorFunctions.isOneOf(options, **kwargs)
        assert _validator(val) == expected

    @pytest.mark.parametrize('val, options, kwargs, expected', [
        (1, [1, 2, 3], {}, False),
        (1, ['1', '2', '3'], {}, True),
        (1, ['1', '2', '3'], {'cast': str}, False),
        ('1', ['1', '2', '3'], {}, False),
        ('1', [1, 2, 3], {}, True),
        ('1', [1, 2, 3], {'cast': int}, False),
    ])
    def test_isNotOneOf(self, val, options, kwargs, expected):
        _validator = ValidatorFunctions.isNotOneOf(options, **kwargs)
        assert _validator(val) == expected

    @pytest.mark.parametrize('val, option, inclusive, kwargs, expected', [
        (1, 0, False, {}, True),
        (1, 1, False, {}, False),
        (1, 1, True, {}, True),
        ('1', 0, False, {'cast': int}, True),
        ('30', '40', False, {}, False),
    ])
    def test_isGreaterThan(self, val, option, inclusive, kwargs, expected):
        _validator = ValidatorFunctions.isGreaterThan(option, inclusive, **kwargs)
        assert _validator(val) == expected

    @pytest.mark.parametrize('val, option, inclusive, kwargs, expected', [
        (1, 0, False, {}, False),
        (1, 1, False, {}, False),
        (1, 1, True, {}, True),
        ('1', 0, False, {'cast': int}, False),
        ('30', '40', False, {}, True),
    ])
    def test_isLessThan(self, val, option, inclusive, kwargs, expected):
        _validator = ValidatorFunctions.isLessThan(option, inclusive, **kwargs)
        assert _validator(val) == expected

    @pytest.mark.parametrize('val, min, max, inclusive, kwargs, expected', [
        (10, 1, 20, False, {}, True),
        (1, 1, 20, False, {}, False),
        (20, 1, 20, False, {}, False),
        (20, 1, 20, True, {}, True),
        ('20', 1, 20, False, {'cast': int}, False),
    ])
    def test_isBetween(self, val, min, max, inclusive, kwargs, expected):
        _validator = ValidatorFunctions.isBetween(min, max, inclusive, **kwargs)
        assert _validator(val) == expected

    @pytest.mark.parametrize('val, substr, kwargs, expected', [
        ('abcdefg', 'abc', {}, True),
        ('abcdefg', 'xyz', {}, False),
        (12345, '12', {}, True),  # don't need 'cast'
    ])
    def test_startsWith(self, val, substr, kwargs, expected):
        _validator = ValidatorFunctions.startsWith(substr, **kwargs)
        assert _validator(val) == expected

    @pytest.mark.parametrize('val, substr, kwargs, expected', [
        ('abcdefg', 'abc', {}, True),
        ('abcdefg', 'efg', {}, True),
        ('abcdefg', 'cd', {}, True),
        ('abcdefg', 'cf', {}, False),
        (10001, '10', {}, True),  # don't need 'cast'
    ])
    def test_contains(self, val, substr, kwargs, expected):
        _validator = ValidatorFunctions.contains(substr, **kwargs)
        assert _validator(val) == expected

    @pytest.mark.parametrize('val, kwargs, expected', [
        (1, {}, True),
        (10, {}, True),
        ('abc', {}, False),
        ('123', {}, True),  # don't need 'cast'
        ('123abc', {}, False),
    ])
    def test_isNumber(self, val, kwargs, expected):
        _validator = ValidatorFunctions.isNumber(**kwargs)
        assert _validator(val) == expected

    @pytest.mark.parametrize('val, kwargs, expected', [
        ('abcdefg', {}, True),
        ('abc123', {}, True),
        ('abc123!', {}, False),
        ('abc==6', {}, False),
        (10, {'cast': str}, True),
    ])
    def test_isAlphaNumeric(self, val, kwargs, expected):
        _validator = ValidatorFunctions.isAlphaNumeric(**kwargs)
        assert _validator(val) == expected

    @pytest.mark.parametrize('val, start, end, kwargs, expected', [
        ('1000', 0, 4, {}, False),
        ('1000', 1, 4, {}, False),
        ('', 0, 1, {}, True),
        ('', 1, 4, {}, True),
        (None, 0, 0, {}, True),  # this strangely fails.... investigate
        (None, 0, 10, {}, True),
        ('    ', 0, 4, {}, True),
        ('####', 0, 4, {}, True),
        ('1###', 1, 4, {}, True),
        ('   1', 0, 3, {}, True),
        ('   1', 0, 4, {}, False),
    ])
    def test_isEmpty(self, val, start, end, kwargs, expected):
        _validator = ValidatorFunctions.isEmpty(start, end, **kwargs)
        assert _validator(val) == expected

    @pytest.mark.parametrize('val, start, end, kwargs, expected', [
        ('1000', 0, 4, {}, True),
        ('1000', 1, 4, {}, True),
        ('', 0, 1, {}, False),
        ('', 1, 4, {}, False),
        (None, 0, 0, {}, False),  # this strangely fails.... investigate
        (None, 0, 10, {}, False),
        ('    ', 0, 4, {}, False),
        ('####', 0, 4, {}, False),
        ('1###', 1, 4, {}, False),
        ('   1', 0, 3, {}, False),
        ('   1', 0, 4, {}, True),
    ])
    def test_isNotEmpty(self, val, start, end, kwargs, expected):
        _validator = ValidatorFunctions.isNotEmpty(start, end, **kwargs)
        assert _validator(val) == expected

    @pytest.mark.parametrize('val, kwargs, expected', [
        ('    ', {}, True),
        ('1000', {}, False),
        ('0000', {}, False),
        ('####', {}, False),
        ('----', {}, False),
        ('', {}, False),
    ])
    def test_isBlank(self, val, kwargs, expected):
        _validator = ValidatorFunctions.isBlank(**kwargs)
        assert _validator(val) == expected

    @pytest.mark.parametrize('val, length, kwargs, expected', [
        ('12345', 5, {}, True),
        ('123456', 5, {}, False),
        ([1, 2, 3], 5, {}, False),
        ([1, 2, 3], 3, {}, True),
    ])
    def test_hasLength(self, val, length, kwargs, expected):
        _validator = ValidatorFunctions.hasLength(length, **kwargs)
        assert _validator(val) == expected

    @pytest.mark.parametrize('val, length, inclusive, kwargs, expected', [
        ('12345', 3, False, {}, True),
        ('12345', 5, False, {}, False),
        ('12345', 5, True, {}, True),
        ([1, 2, 3], 5, False, {}, False),
        ([1, 2, 3], 3, False, {}, False),
        ([1, 2, 3], 3, True, {}, True),
        ([1, 2, 3], 1, False, {}, True),
    ])
    def test_hasLengthGreaterThan(self, val, length, inclusive, kwargs, expected):
        _validator = ValidatorFunctions.hasLengthGreaterThan(length, inclusive, **kwargs)
        assert _validator(val) == expected

    @pytest.mark.parametrize('val, length, kwargs, expected', [
        (1001, 5, {}, False),
        (1001, 4, {}, True),
        (1001, 3, {}, False),
        (321, 5, {}, False),
        (321, 3, {}, True),
        (321, 2, {}, False),
        (1000, 3, {}, False),
        ('0001', 3, {}, False),
        ('0001', 4, {}, True),
        ('1000', 3, {}, False),
        ('1000', 4, {}, True),
    ])
    def test_intHasLength(self, val, length, kwargs, expected):
        _validator = ValidatorFunctions.intHasLength(length, **kwargs)
        assert _validator(val) == expected

    @pytest.mark.parametrize('val, number_of_zeros, kwargs, expected', [
        ('000', 3, {}, False),
        ('0 0', 3, {}, True),
        ('100', 3, {}, True),
        ('123', 3, {}, True),
        ('000', 4, {}, True),
        (000, 3, {'cast': str}, True),
        (000, 1, {'cast': str}, False),
    ])
    def test_isNotZero(self, val, number_of_zeros, kwargs, expected):
        _validator = ValidatorFunctions.isNotZero(number_of_zeros, **kwargs)
        assert _validator(val) == expected
