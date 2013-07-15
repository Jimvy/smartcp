.. -*- coding: utf-8 -*-

Smart copy
==========


This is an useful utility for automating copy from source and destination
that can be customised by arguments that may vary.
A good example of usage is available with
`this repo <https://github.com/Gp2mv3/Syntheses>`_.

Install
-------

You can install it from source by cloning this repo

.. code-block:: bash

    git clone http//:github.com:blegat/smartcp.git

and running

.. code-block:: bash

    sudo python setup.py install

You can also install the latest released version through ``pip``

.. code-block:: bash

    sudo pip install smartcp

or ``easy_install``

.. code-block:: bash

    sudo easy_install smartcp

Requirements
~~~~~~~~~~~~

It is officially only compatible with Python 3 but
it should mostly work with Python 2.

You will also need ``PyYAML``.

Usage
-----

You can get help by running

.. code-block:: bash

    smartcp -h

Config file
~~~~~~~~~~~

To specify which files to copy where, you need to specify a config file.
It should use the `YAML syntax <http://en.wikipedia.org/wiki/YAML>`_.
It contains a base path for the source,
a base path for the destination and clients.
For each client,
you can specify some arguments
(if no argument is given, there will be one copy but there can't be any node
``arg``) and how to generate
the source and destination from these arguments.
To specify them you need to nest three types of nodes.

* A ``path_format`` which can contain placeholders ``{n}``
  and then parameters to replace them.
  The parameters can be one of the three nodes.
* A ``mapping`` which contain a hash and a key which is a node.
* An ``arg`` which is one of the arguments.

Here is an example which copies files from ``version/subversion/file``
to ``file-version.subversion`` while renaming ``file`` to ``b`` if it is ``a``.
It also copies ``1/1/x`` to ``../x-1.1``.

.. code-block:: yaml

    input_base: .
    output_base: .
    clients:
      - name: Official
        arguments:
          subversion: [1, 2, 3]
          version: [1, 2, 3, 4, 5]
          file: [a, A, x, X]
        input:
          path_format: "{0}/{1}/{2}"
          parameters:
            - arg: subversion
            - arg: version
            - arg: file
        output:
          path_format: "{0}-{1}.{2}"
          parameters:
            - mapping:
                a: b
              key:
                arg: file
            - arg: version
            - arg: subversion
      - name: Simple copy
        input:
          path_format: 1/1/x
        output:
          path_format: ../x-1.1

Note the ``"`` for the path format because without it YAML won't understand
that it is just a string.
