# Getting an experiment ready for prime time

To get a psiTurk experiment ready to be put on Mechanical Turk, you should go through the following steps:

1) Edit the config.txt file in the top level of the experiment directory to ensure it is posted appropriately to the Turkers and set up appropriately for your experiment:

* In the HIT Configuration section, make sure that the title, description, keywords, and contact info are appropriate since these will be seen by Turkers

* In the Database Parameters, make sure you have the right table name (I often will add _test during the debugging phase to keep the real data pure). If you are using the non-default database, change the url, but otherwise use participants.db

* In the Task Parameters, make sure you have the right number of conditions & counterbalancing (note: randomization is done via js and so doesn't require the num_counters to change... this is only for explicit counterbalancing)

* In the Server Parameters, make sure that host is set to 0.0.0.0 rather than localhost. ALTERNATELY: if you are posting this on a dedicated server, set the host to the IP address of that server, and either (a) make sure port 22362 is open, or (b) set the port field to an open port

2) Test your experiment by running it through debug mode. You can do this by opening psiTurk, then typing "server on" to spool up the server, and then typing "debug" to get a debug link. Make sure things run appropriately on multiple browser types, and add anything that doesn't work to the browser exclude rule in the config file (e.g., Safari is really bad a playing videos using psiTurk, so should be excluded if video is required). If have a dedicated server you can share the experiment at this point using the debug links that get spawned every time you type "debug"

3) Test your experiment by running it in the sandbox mode. You can do this via the "hit create" command while the psiTurk command line says "mode:sdbx". See the [psiTurk documentation](https://psiturk.readthedocs.io/en/latest/command_line/hit.html) for more details about the hit create command. This will give you a feel for exactly what Turkers will see, and displays more information than the debug version. Make sure everything on MTurk looks exactly how you would want it and that the experiment returns and gives you credit to your sandbox account.

4) Go back to the config file and get everything ready for the final run (e.g., change the table_name if needed)

5) Go into psiturk, change the mode to "live", then use "hit create" to post the experiment. You should generally post experiments in batches of 9 or fewer, since MTurk charges more money for 10+ batches and it's easy to create multiple groups of HITs with psiTurk (e.g., just press up)
