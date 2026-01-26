Tokenisers
==========

Tokenisers are used to break up text represented as a single string (such as from a text file) into a list of words.


The ``tokenise`` function
-------------------------

The simplest way to tokenise a text in ``malti`` is as follows:

.. code-block:: python
    :linenos:

    import malti.tokeniser

    sentence = 'Eżempju ta\' sentenza.'
    tokens = malti.tokeniser.tokenise(sentence)
    print(tokens)

.. code-block:: python

    ['Eżempju', "ta'", 'sentenza', '.']


The ``Tokeniser`` class
-----------------------

The above is a convenience function that makes use of a default tokeniser (``KMTokeniser`` in this version).
To gain access to all the features of tokenisers, they should be used in their class form, for example:

.. code-block:: python
    :linenos:

    import malti.tokeniser

    tokeniser = malti.tokeniser.KMTokeniser()

    sentence = 'Eżempju ta\' sentenza.'
    tokens = tokeniser.tokenise(sentence)
    print(tokens)

.. code-block:: python

    ['Eżempju', "ta'", 'sentenza', '.']

Apart from ``tokenise``, every tokeniser can also return a list of indices of the tokens instead of the tokens themselves by calling the ``tokenise_indices`` method:

.. code-block:: python
    :linenos:

    import malti.tokeniser

    tokeniser = malti.tokeniser.KMTokeniser()

    sentence = 'Eżempju ta\' sentenza.'
    indices = tokeniser.tokenise_indices(sentence)
    print(indices)

.. code-block:: python

    [(0, 7), (8, 11), (12, 20), (20, 21)]

This tells you that the first word is found at ``sentence[0:7]``, the second word at ``sentence[8:11]``, and so on.

There is also a ``detokenise`` method that is meant to *approximately* invert the ``tokenise`` method by returning the original text given a list of tokens (although tokenisation is generally a lossy transformation which means that there is no guarantee that the original text can be recovered):

.. code-block:: python
    :linenos:

    import malti.tokeniser

    tokeniser = malti.tokeniser.KMTokeniser()

    tokens = ['Eżempju', "ta'", 'sentenza', '.']
    text = tokeniser.detokenise(tokens)
    print(text)

.. code-block:: python

    'Eżempju ta\' sentenza.'

Available tokenisers
--------------------

The following tokenisers are available:

* ``malti.tokeniser.RegexTokeniser`` (:doc:`../malti/tokeniser/regex_tokeniser`): A tokeniser where you have to supply a regular expression that matches words.
* ``malti.tokeniser.KMTokeniser`` (:doc:`../malti/tokeniser/km_tokeniser/km_tokeniser`): A ``RegexTokeniser`` that is equivalent to the one used to tokenise the `Korpus Malti <https://mlrs.research.um.edu.mt/CQPweb/>`_.
