Line joiners
============

Join a list of text lines into a single line, adding spaces between lines only where necessary and
rejoining hyphenated words.
This is useful for when extracting text from a PDF or using an OCR application.


The ``join_lines`` function
---------------------------

The simplest way to join multiple lines into a single text in ``malti`` is as follows:

.. code-block:: python
    :linenos:

    import malti.line_joiner

    lines = ['Dan it-', 'test huwa', 'maqsum f\'div-', 'ersi linji.']
    text = malti.line_joiner.join_lines(text, fix_hyphenated_words=True)
    print(text)

.. code-block:: python

    'Dan it-test huwa maqsum f\'diversi linji.'


The ``LineJoiner`` class
--------------------------

The above is a convenience function that makes use of a default line joiner (``RBLineJoiner`` in this version).
To gain access to all the features of line joiners, they should be used in their class form, for example:

.. code-block:: python
    :linenos:

    import malti.line_joiner

    splitter = malti.line_joiner.RMLineJoiner()

    lines = ['Dan it-', 'test huwa', 'maqsum f\'div-', 'ersi linji.']
    text = malti.line_joiner.join_lines(text, fix_hyphenated_words=True)
    print(text)

.. code-block:: python

    'Dan it-test huwa maqsum f\'diversi linji.'


Available line joiners
----------------------

The following line joiners are available:

* ``malti.line_joiner.RBLineJoiner`` (:doc:`../malti/line_joiner/rb_line_joiner/rb_line_joiner`): A ``LineJoiner`` that processes lines with a rule-based algorithm.
