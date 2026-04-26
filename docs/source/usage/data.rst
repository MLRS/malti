Data
====

Some data resources for the Maltese language that are loaded and cached lazily when first called.


The ``Data`` class
------------------

This class provides static methods for lazily loading requested data available in ``malti``:

.. code-block:: python
    :linenos:

    import malti.data

    tokens_with_dash_end = malti.data.Data.get_tokens_with_dash_end()
    print(tokens_with_dash_end)

.. code-block:: python

    {'l-', 'il-', 'ċ-', 'iċ-', ...}



Available data
--------------

The following data sets are available:

* ``malti.data.Data.get_tokens_with_dash_end()`` (:doc:`../malti/data/data`): A set of common Maltese tokens that end with a dash.
