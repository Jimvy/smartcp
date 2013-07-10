# Smart copy
This is an useful utility for automating copy from source and destination that can be customised by arguments that may vary.
A good example of usage is available with
[this repo](https://github.com/Gp2mv3/Syntheses).

## Install
You can install it from source by cloning this repo

    git clone http//:github.com:blegat/smartcp.git
and running

    sudo python setup.py install

You can also install the latest released version through `pip`

    sudo pip install smartcp
or `easy_install`

    sudo easy_install smartcp

### Requirements
It is officially only compatible with Python 3 but it should mostly work with Python 2.

You will also need `PyYAML`.

## Usage
You can get help by running

    smartcp -h

### Config file
To specify which files to copy where, you need to specify a config file.
It should use the [YAML syntax](http://en.wikipedia.org/wiki/YAML).
It contains a base path for the source, a base path for the destination and clients.
For each client, you need to specify some arguments and how to generate the source and destination from these arguments.
To specify them you need to nest three types of nodes.

* A `path_format` which can contain placeholders `{n}` and then parameters to replace them.
The parameters can be one of the three nodes.
* A `mapping` which contain a hash and a key which is a node.
* An `arg` which is one of the arguments.

Here is an example which copies files from `version/subversion/file`
to `file-version.subversion` while renaming `file` to `b` if it is `a`.

    input_base: .
    output_base: .
    clients:
      - name: Officiel
        arguments:
          - [1, 2, 3]
          - [1, 2, 3, 4, 5]
          - [a, A, x, X]
        input:
          path_format: "{0}/{1}/{2}"
          parameters:
            - arg: 0
            - arg: 1
            - arg: 2
        output:
          path_format: "{0}-{1}.{2}"
          parameters:
            - mapping:
                a: b
              key:
                arg: 2
            - arg: 2
            - arg: 0
Note the `"` for the path format because without it YAML won't understand
that it is just a string.
