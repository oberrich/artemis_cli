# artemis-cli
A command-line application for tutors to more productively grade programming excises on ArTEMiS

## Beta notice
[![forthebadge](https://forthebadge.com/images/badges/fuck-it-ship-it.svg)](https://forthebadge.com) [![forthebadge](https://forthebadge.com/images/badges/60-percent-of-the-time-works-every-time.svg)](https://forthebadge.com)

This program is still in beta and hasn't been thoroughly tested yet, make sure your grades were actually submitted properly.

## Contribute
If you want to contribute to this script, please create a Pull Request into `develop`

## Overview and purpose
Used for the introductory course "Praktikum Grundlagen der Programmierung"
[IN0002](https://campus.tum.de/tumonline/wbModHb.wbShowMHBReadOnly?pKnotenNr=452806) at TU Munich.
The course teaches first-year students from a wide range of Computer Science related study programs
the fundamentals of object-oriented programming.

The course is facilitated on/ supported by the interactive learning tool ArTEMiS
(http://www.interactive-learning.org). ArTEMiS allows tutors to download the repositories of student's
exercises in order to grade them. **This script assists the relevant steps in the grading process.**

## First steps
1. Add your ArTEMiS credentials (username and password) into `config.yml`
   * Remember to untrack the changes to this file before redistributing: `git update-index --assume-unchanged config.yml`
2. Make the script executable: `chmod +x artemis_cli`
3. Install dependencies via `pip install pyyaml argparse requests unicodecsv`

Run the script via `./artemis_cli <command>`


## Supported commands (continuously updated)
1. `repos`  Download all student repos
2. `grade`  Grade a student individually
3. `grades` Grade all students for an assignment. A gradebook, that is generated by the `repos` command for all
students to be graded, is used. The only format for gradebook implemented as of now is YAML (.yml)
4. `results` Exports all students' results (including feedback and failed tests) to `results.csv`

## Commands
Help to all available commands can be acquired by using the help flag (`-h` or `--help`).
The following show those help outputs. However, the most up-to-date help can be found through said flags.

Below, for example, `./artemis_cli -h` was called:
```
usage: artemis_cli [-h] [-q | -v] {repos,grade,grades} ...

A command-line application for tutors to more productively grade programming
excises on ArTEMiS

optional arguments:
  -h, --help            show this help message and exit
  -q, --quiet           Print quiet
  -v, --verbose         Print verbose

commands:
  List of valid commands

  {repos,grade,grades}  Additional help
    repos               Downloads student exercise repositories
    grade               Submits grade for a student assignment
    grades              Submits all grades of a specified gradebook file
```

### artemis-cli repos

```
usage: artemis_cli repos [-h] [-a assignment] [-s tumId [tumId ...]]

optional arguments:
  -h, --help            show this help message and exit
  -a assignment, --assignment assignment
                        The assignment to be processed (e.g. w01h01)
  -s tumId [tumId ...], --students tumId [tumId ...]
                        The students' TUM ids (comma or space-separated) to be
                        processed (e.g. ge36feg, ba12sup, ...)
```

### artemis-cli grade

```
usage: artemis_cli grade [-h] -a assignment -s tum_id -score score -text
                            result_text [-pos text [detail_text ...]]
                            [-neg text [detail_text ...]]

optional arguments:
  -h, --help            show this help message and exit
  -a assignment, --assignment assignment
                        The assignment to be processed (e.g. w01h01)
  -s tum_id, --student tum_id
                        The student's TUM id to be processed (e.g. ge42abc)
  -score score          The score (0-100) of the assignment (e.g. 80)
  -text result_text     The result text of the assignment (e.g. "Gut gemacht")
  -pos text [detail_text ...], --positive text [detail_text ...]
                        A positive feedback consisting of Text and optionally
                        one Detail Text (e.g. "Dokumentation" ["Gute und
                        akkurate Kommentare"])
  -neg text [detail_text ...], --negative text [detail_text ...]
                        A negative feedback consisting of Text and optionally
                        one Detail Text (e.g."Formatierung" ["Bitte
                        Autoformatierung benutzen"])
```

### artemis-cli grades
```
usage: artemis_cli grades [-h] -f gradebook_file

optional arguments:
  -h, --help            show this help message and exit
  -f gradebook_file, --file gradebook_file
                        A gradebook file as generated by `artemis-cli repos
                        ...` with all grades that are to be uploaded to
                        ArTEMiS entered
```

### artemis-cli results
```
usage: artemis_cli results [-h] -a assignment -s tumId [tumId ...]

optional arguments:
  -h, --help            show this help message and exit
  -a assignment, --assignment assignment
                        The assignment to be processed (e.g. w01h01)
  -s tumId [tumId ...], --students tumId [tumId ...]
                        The students' TUM ids (comma or space-separated) to be
                        processed (e.g. ge36feg, ba12sup, ...)
```
