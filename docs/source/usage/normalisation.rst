Normalisation
=============

Provides helpful functions to normalise data.

The ``normalise`` function
--------------------------

A utility function to normalise text data.
The text is normalised to ``NFC`` form and any non-whitespace control characters are removed.
It also applies simple character substitutions to use canonical forms for whitespaces, quotation/apostrophe marks, and hyphen symbols.

.. code-block:: python
    :linenos:

    from malti.normalisation import normalise

    input = "“Malta” hija gz\u0307ira z\u0307għira fic\u0307-\u200bc\u0307entru tal-\u200bBaħar il-\u200bMediterran."
    output = normalise(input)
    # will give '"Malta" hija gżira #æira fiċ-ċentru tal-Baћar il-Mediterran.'

In addition, the function also includes a set of heuristic character substitutions for cases where Maltese text is incorrectly encoded.
These mappings where developed based on empirical observations, typically centered around Maltese-specific characters, ranging from OCR-related encoding, Maltese keyboard encoding, and visually similar characters (e.g. Cyrillic characters).
Since these are heuristics, any substituted token is verified against token frequencies from Korpus Malti, to verify that the resulted token is a plausible Maltese token.
The goal of this functionality is to fix common errors while minimising newly introduced errors as much as possible.
It is by no means exhaustive and likely does not cover many corner cases.

.. code-block:: python
    :linenos:

    from malti.normalisation import normalise

    input = "“Malta” hija g#ira #æira f`nofs il-Ba\u045bar il-Mediterran."
    output = normalise(input, apply_heuristics=True)
    # will give '"Malta" hija gżira żgħira f'nofs il-Baħar il-Mediterran.'
