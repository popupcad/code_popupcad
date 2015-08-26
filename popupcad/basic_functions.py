# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes and CONTRIBUTORS
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE for full license.
"""


def return_formatted_time(
        specificity='second',
        small_separator='-',
        big_separator='_'):
    import time

    a = time.localtime()
    args = a.tm_year, a.tm_mon, a.tm_mday, a.tm_hour, a.tm_min, a.tm_sec
    kwargs = {'ss': small_separator, 'bs': big_separator}
    if specificity == 'year':
        b = '{0:04d}'.format(*args, **kwargs)
    elif specificity == 'month':
        b = '{0:04d}{ss}{1:02d}'.format(*args, **kwargs)
    elif specificity == 'day':
        b = '{0:04d}{ss}{1:02d}{ss}{2:02d}'.format(*args, **kwargs)
    elif specificity == 'hour':
        b = '{0:04d}{ss}{1:02d}{ss}{2:02d}{bs}{3:02d}'.format(*args, **kwargs)
    elif specificity == 'minute':
        b = '{0:04d}{ss}{1:02d}{ss}{2:02d}{bs}{3:02d}{ss}{4:02d}'.format(
            *
            args,
            **kwargs)
    elif specificity == 'second':
        b = '{0:04d}{ss}{1:02d}{ss}{2:02d}{bs}{3:02d}{ss}{4:02d}{ss}{5:02d}'.format(
            *
            args,
            **kwargs)
    return b
