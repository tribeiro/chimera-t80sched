# chimera-t80sched
A chimera script for scheduling and executing observations for the T80S telescope. 

# Setting up the scheduler database

Add/modify project information to the database. The task read configuration 
files to input information for most of the tables. The format is

```
[tablename]
columname1 = String Value	# For string values
columname2 = 0.4			# For float
columname3 = 1				# For int
```

# Projects table

```
Table name: [projects]
Information: Project information
Columns:
PID :		A unique string identifying the project.
For instance SO2014B-123, SPLUS, SPOL, SPLUSPLUS...
PI	:		Name of the principal investigator.
ABSTRACT:	Abstract of the project.
URL	:		URL for the project.
PRIORITY:	The execution priority of the project. Lower is higher, so a project with priority
0 gets observed earlier than 1, and so on. There may be multiple projects with the same priority.
```

```
Table name: [obsblock]
Information:	Observation block definition. Each project must have at least 1 block, may have more 
than one. An observaiton block is the smaller unit of observation that is allowed.
Larger block with multiple objects observed in multiple filters are dificult to schedule
and must be avoided unless really necessary. If you want to observe 2 targets in the same
night you should use a single block. But beware that this may create idle time if no other 
block can be schedule in between observations and the lag is too large.
Columns:
PID :		A unique string identifying the project.
MAXAIRMASS		:	Larger airmass (lower altitude) a target can be observed. This is defined as a fraction
of minimum airmass. For instance if target minimum airmass is 1.2 and MAXAIRMASS=0.5 Then
the target will only be observed if airmass < 1.8 (1.5x the minimum).
maxmoonBright	:	Percentage of maximum moon ilumination allowed (100% = fullmoon).
minmoonBright	:	Percentage of minimum moon ilumination allowed (0% = no mooon).
minmoonDist		:	Minimum moon distance allowed (in degrees).
maxseeing		:	Maximum seeing allowed. If no seeing monitor is present the observation may be discarded
later during data processing, and the targets gets back to the queue for observing.
cloudcover		:	Maximum cloud cover allowed.
schedalgorith	:	Type of scheduling algorithm. Some examples are;
0 - observe at maximum altitude
1 - time series
2 - standard star observation (multiple airmasses)
applyextcorr	:	Modify exposure time according to sky extiction? Boolean 0 or 1.
```

To input observations blocks and targets a list of 
pid , blockid , objectid , block configuration file 
In general each block will contain only one target. But, blocks with multiple targets are allowed. 
The format is simply a 4 column ascii file. You can check the pids, blockids, objectids in the database.

```
Example 1:
SO2014B-123 000 147 config01_147.cfg
SO2014B-123 000 148 config01_148.cfg
SO2014B-123 000 149 config01_149.cfg
SO2014B-123 001 150 config01_150.cfg
SO2014B-123 001 151 config01_151.cfg
SO2014B-123 002 148 config02_148.cfg
```

This will include 6 objects in 3 blocks for project SO2014B-123. Block 0 will have objects 147, 148 
and 149, Block 1 will have objects 149 and 150 and Block 2 repeats object 148 in a different configuration.

```
Example 2:
SPLUS 000 000 splus_block.cfg
SPLUS 001 001 splus_block.cfg
SPLUS 002 002 splus_block.cfg
.
.
.
SPLUS  N   N  splus_block.cfg
```

This will include objects in blocks for project SPLUS. Block 0 will have object 0, Block 1 will have 
object 1 and so on. All observations are performed with the same configuration. The configuration file
must have the following format:

```
[blockconfig]
filter = B,V,R,I
exptime = 80.,80.,60.,40.
nexp = 2,1,1,2
imagetype=OBJECT,OBJECT,OBJECT,OBJECT
```
