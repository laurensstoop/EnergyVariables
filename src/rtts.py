from itertools import chain

import pandas
import sklearn.model_selection
import sklearn.utils


def _generate_region_labels(x, region_length='7h'):
    """Return indices that label contigious groups of length region_length.

    :param pandas.DataFrame x: must be time indexed.
    :param region_length: must be interpreteable by :func:`pandas.Timedelta`

    :return: array of same length as X with group indices
    """
    if not (isinstance(x, (pandas.Series, pandas.DataFrame))
            and isinstance(x.index, (pandas.DatetimeIndex, pandas.TimedeltaIndex))):
        raise ValueError("x must be a time-indexed DataFrame or Series.")
    region_length = pandas.Timedelta(region_length)
    return ((x.index - min(x.index)) // region_length).values


class RegionShuffleSplit(sklearn.model_selection.GroupShuffleSplit):

    def __init__(self, n_splits=4, test_size="default", train_size=None,
                 random_state=None, region_length='7h'):
        """
        Cross-validation iterator for shuffling contiguous regions of `region_length`.

        :param int n_splits:
        :param test_size:
        :type test_size: float, int, None
        :param train_size:
        :type train_size: float, int, None
        :param random_state:
        :type random_state: int, Random State instance, None
        :param region_length:
        :type region_length: Anything interpreteable by `pandas.Timedelta`.

        This cross-validation iterator uses :class:`sklearn.model_selection.GroupShuffleSplit`.
        The n-th group consists of all datapoints that fall into the n-th time interval of length
        `region_length` counting from the first datapoint.

        In order to work, the data to be split must be a time-indexed
        :class:`pandas.DataFrame`.

        The parameters except `region_length` work as in
        :class:`~sklearn.model_selection.GroupShuffleSplit`.
        Most importantly, if `train_size` or `test_size` are floats,
        they describe the portion of groups(!) not of data points.
        However this only makes a difference if the groups are different in size
        (which can happen when data points are missing).
        """
        super().__init__(n_splits=n_splits,
                         test_size=test_size,
                         train_size=train_size,
                         random_state=random_state)
        self.region_length = region_length

    def split(self, x, y=None, groups=None):
        """
        Generate indices to split data into training and test set.

        :param pandas.DataFrame x: must be time (or timedelta) indexed.
        :param array-like y:
        :param groups: will be ignored

        :return: train,test

        train,test are the indices for the respective split.

        """
        groups = _generate_region_labels(x, self.region_length)
        return super().split(x, y, groups=groups)


def region_train_test_split(*arrays,
                            region_length='7h',
                            test_size='default', train_size=None,
                            random_state=None, shuffle=True, **options):
    """Split arrays or matrices into random train and test subsets.

    Similar to :func:`sklearn.model_validation.train_test_split`,
    however the splitting is done under one side condition:
    Not the datapoints themselves are shuffled but regions consisting of datapoints falling into time intervals
    of a certain length are shuffled.

    :param arrays: sequence of indexables with same length / shape[0].
    :param region_length:
    :type region_length: Anything interpreteable by :class:`pandas.Timedelta`
    :param test_size: Same as in :func:`sklearn.model_validation.train_test_split`
    :param train_size: Same as in :func:`sklearn.model_validation.train_test_split`
    :param random_state: Same as in :func:`sklearn.model_validation.train_test_split`
    :param shuffle: Same as in :func:`sklearn.model_validation.train_test_split`
    :param options: passed to :func:`sklearn.model_validation.train_test_split` or ignored.
    :return: List containing train-test split of inputs.
    :rtype:  list, length=2 * len(arrays)

    Note that if `train_size` or `test_size` are floats,
    they describe the portion of groups(!) not of data points.
    However this only makes a difference if the groups are different in size
    (which can happen when data points are missing).

    If region_length is not None and shuffle is True, the first of `arrays` must(!)
    be a time_indexed :class:`pandas.DataFrame`.
    If region_length is None or shuffle is False, :func:`~sklearn.model_selection.train_test_split`
    from sklearn will be called (with `region_length` ignored.)


    >>> import pandas
    >>> idx = pandas.date_range('2020-01-01', '2020-01-01 9:00', freq='H')
    >>> df = pandas.DataFrame(index=idx, data={'a': range(10)})
    >>> train, test = region_train_test_split(df, region_length='2h', test_size=0.4, random_state=0)
    >>> train.index
    DatetimeIndex(['2020-01-01 02:00:00', '2020-01-01 03:00:00',
                   '2020-01-01 06:00:00', '2020-01-01 07:00:00',
                   '2020-01-01 08:00:00', '2020-01-01 09:00:00'],
                  dtype='datetime64[ns]', freq=None)
    >>> test.index
    DatetimeIndex(['2020-01-01 00:00:00', '2020-01-01 01:00:00',
                   '2020-01-01 04:00:00', '2020-01-01 05:00:00'],
                  dtype='datetime64[ns]', freq=None)
    """
    if shuffle is False or region_length is None:
        return sklearn.model_selection.train_test_split(*arrays, test_size=test_size, train_size=train_size,
                                                        random_state=random_state, shuffle=shuffle, **options)

    n_arrays = len(arrays)
    if n_arrays == 0:
        raise ValueError("At least one array required as input")

    if test_size == 'default':
        test_size = None

    if test_size is None and train_size is None:
        test_size = 0.25

    arrays = sklearn.utils.indexable(*arrays)

    cv = RegionShuffleSplit(test_size=test_size,
                            train_size=train_size,
                            random_state=random_state,
                            region_length=region_length)

    train, test = next(cv.split(x=arrays[0]))

    return list(chain.from_iterable((sklearn.utils.safe_indexing(a, train),
                                     sklearn.utils.safe_indexing(a, test)) for a in arrays))
