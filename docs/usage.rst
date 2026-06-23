Usage
=====

Install the pinned project environment:

.. code-block:: bash

   make install-dev

Run local verification:

.. code-block:: bash

   make check

Run the deterministic offline reproduction path:

.. code-block:: bash

   make reproduce

Generate the Quarto report:

.. code-block:: bash

   make report

If published to DockerHub, the public image exposes the same reproduction
command:

.. code-block:: bash

   docker pull cliprob/nba-predict:latest
   docker run --rm cliprob/nba-predict:latest make reproduce
