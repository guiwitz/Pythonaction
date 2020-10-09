import numpy as np
import numpy.testing
import pytest

from pythonaction import mymodule

first_array = np.ones((2,2))

def test_myfunction():

    new_array = mymodule.my_function(first_array)
    second_array = np.array([[3,3],[3,3]])


    np.testing.assert_array_equal(new_array, second_array)
