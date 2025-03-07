"""Test docs helper module."""

from sugar.docs import docparams


class A:
    """Class A."""

    @docparams(
        {
            'arg1': 'this is the arg 1',
            'arg2': 'this is the arg 2',
        }
    )
    def myfunc(self, arg1: str, arg2: str = '1') -> None:
        """Run a nice function."""
        pass


def test_docparams() -> None:
    """Test docparams decorator."""
    a = A()
    expected = {
        'title': 'Run a nice function.',
        'parameters': {
            'arg1': {
                'type': 'str',
                'help': 'this is the arg 1',
                'positional_only': 'False',
            },
            'arg2': {
                'type': 'str',
                'help': 'this is the arg 2',
                'default': '1',
                'positional_only': 'False',
            },
        },
    }
    func_docstring = a.myfunc.__doc__ or ''
    assert a.myfunc._meta_docs == expected
    assert 'Parameters:' in func_docstring
    assert 'arg1' in func_docstring
    assert 'arg2' in func_docstring
