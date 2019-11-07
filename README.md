# artemis-cli
## Overview and Purpose
Used for the introductory course "Praktikum Grundlagen der Programmierung" 
[IN0002](https://campus.tum.de/tumonline/wbModHb.wbShowMHBReadOnly?pKnotenNr=452806) at TU Munich.
The course teaches first-year students from a wide range of Computer Science related study programs
the fundamentals of object-oriented programming. 

The course is facilitated on/ supported by the interactive learning tool ArTEMiS 
(http://www.interactive-learning.org). ArTEMiS allows tutors to download the repositories of student's
exercises in order to grade them. **This script assists the relevant steps in the grading process.**

## How to use
1. Add your ArTEMiS credentials (username and password) into `artemis-credentials.config`
   * Remember to untrack the changes to this file before redistributing: `git update-index --assume-unchanged artemis-credentials.config`
2. Make `artemis-cli.sh` executable: `chmod +x artemis-cli.sh`
3. Run the script: `./artemis-cli.sh  w01h01 ge36moy, ge37moy, ge38moy` with arguments being
   1. assignment (e.g. `w01h01`)
   2. comma separated TUM ids (e.g. ``ge36moy, ge37moy, ge38moy``)

## Supported functionalities (continuously updated)
1. Downloading all student repos