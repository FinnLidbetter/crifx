# CRIFX

CRIFX is the Contest pReparation Insights tool For anyone (X).

Its purpose is to automatically produce pdf reports that give insights into
tasks that are completed and tasks that are still outstanding in preparing
an icpc-style competitive programming contest.

## Installation
Install crifx with `pip install crifx`. (Does not work yet.)

## Using crifx
In the root directory for a problemset, run `crifx` from within a problemset nested
directory, or run `crifx /path/to/problemset/root` (not yet implemented). 
If there is no `crifx.toml` configuration file in the problemset root directory, 
then a report will be created using default configuration values.

Crifx can be configured by adding a `crifx.toml` file to the root of the problemset 
directory. The configuration can be used to define requirements on things like
the number of indepenedent AC submissions for each problem, groups of programming
languages and the number of submissions needed from each group or the number of 
distinct groups required. The configuration file can also be used to specify the
names of people involved in contest preparation such that filenames and special
strings in judge submissions can be used to associate submissions with those 
people.

## Counting indepedent submissions

### How crifx decides the author of a submission
In order of precedence, crifx determines the author of a file by:
1. The presence of a crifx!(author="name") string in the text of a submission file. (Not yet implemented.)
2. The presence of an underscore separated name string that matches an alias in the
   `crifx.toml` configuration file.
3. The git user associated with the largest number of lines in the git blame. Roughly speaking this will be
   the git user that created/changed the largest number of lines in the current revision.

The `crifx.toml` file is used to define the aliases of a submission author and associate them with
a git username. More details to come, including an example.

If you encounter a scenario where crifx is incorrectly attributing a submission to the wrong person
and it cannot easily be fixed by adding a user and alias to the `crifx.toml` file.
Crifx does not yet support disambiguating git users with the same git name.
