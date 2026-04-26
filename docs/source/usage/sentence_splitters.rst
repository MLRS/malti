Sentence splitters
==================

Sentence splitters are used to break up text represented as a single string (such as from a text file) into a list of sentences.


The ``split`` function
----------------------

The simplest way to sentence split a text in ``malti`` is as follows:

.. code-block:: python
    :linenos:

    import malti.sent_splitter

    text = 'Eżempju ta\' sentenza. Eżempju ta\' sentenza oħra.'
    sentences = malti.sent_splitter.split(text)
    print(sentences)

.. code-block:: python

    ['Eżempju ta\' sentenza.', 'Eżempju ta\' sentenza oħra.']


The ``SentSplitter`` class
--------------------------

The above is a convenience function that makes use of a default sentence splitter (``KMSentSplitter`` in this version).
To gain access to all the features of sentence splitters, they should be used in their class form, for example:

.. code-block:: python
    :linenos:

    import malti.sent_splitter

    splitter = malti.sent_splitter.KMSentSplitter()

    text = 'Eżempju ta\' sentenza. Eżempju ta\' sentenza oħra.'
    sentences = splitter.split(text)
    print(sentences)

.. code-block:: python

    ['Eżempju ta\' sentenza.', 'Eżempju ta\' sentenza oħra.']


Available sentence splitters
----------------------------

The following sentence splitters are available:

* ``malti.sent_splitter.KMSentSplitter`` (:doc:`../malti/sent_splitter/km_sent_splitter/km_sent_splitter`): A ``SentSplitter`` that is equivalent to the one used to split sentences in the `Korpus Malti <https://mlrs.research.um.edu.mt/CQPweb/>`_.
