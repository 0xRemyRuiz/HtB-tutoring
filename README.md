HtB-tutoring
============
A python script to help learn pentest on Hack the Box using old machines and ippsec awesome videos!

WARNING: the code was orignially coded in 2022 out of boredom and without great knowledge in python, I tried to clean it up but it's a heavy task and it'll take some time. There is a lot of debug code and the generation of the database is loaded with sometimes unecessary text.

run command: `py run.py`
test command: `py tests.py`

Context
-------
This is a script that fetches the Hack the Box machines pages and then fetches infos about all the videos ippsec made and posted on youtube about the retired boxes and fills a sqlite database. After that you can query the database to randomly get sets of videos to help train on a paid account (at the time this is written you still need to pay Hack the Box to access retired machines).

There is plenty of room for improvement, here is a non exhaustive list:
[ ] intelligent sorting of videos based on settings
[ ] a graphical interface
[ ] better testing
