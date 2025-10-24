"""
Music Options for the Soldered Pomodoro Timer Solder kit

This program allows playing musical sequences on a buzzer. Users can create their own
music on OnlineSequencer.net and paste the exported notes into the appropriate variables.

The system supports three jumper inputs (JP1, JP2, JP3). When a jumper is connected,
the corresponding musical sequences will be played. If no jumpers are connected,
the default sequences (intro, work, rest) will be used.

How to add your own music:
1. Visit onlinesequencer.net and create your musical sequence
2. Select all the notes and copy them
3. Paste the generated sequence into one of the variables below
4. delete the 'Online Sequencer' tag at the start of the string as well as the ';:' symbols at the end

Note format: 'start_time note duration volume;start_time note duration volume...'
"""

# Default musical sequences (played when no jumpers are connected)
# Create your own at OnlineSequencer.net and paste the exported Arduino code here
intro = '2 A6 3 17;6 E6 1 17;9 G6 4 17;0 E6 1 17'  # Introductory music sequence
work = '2 B4 2 43;0 E5 1 43;4 B4 1 43;5 C5 1 43;6 C#5 1 43'  # Work period music
rest = '9 G#6 1 17;0 D#6 1 17;3 F6 1 17;5 G#6 1 17;7 A#6 1 17'  # Rest period music

# Alternative musical sequences for jumper 1 (JP1)
intro_jp1 = '0 F#6 1 21;1 A6 1 21;3 C7 1 21;5 B6 1 21'
work_jp1 = '7 G#4 1 21;0 F4 1 21;2 F#4 1 21;4 G#4 1 21;6 A#4 1 21'
rest_jp1 = '6 A7 2 43;0 A6 2 43;3 C#7 2 43'

# Alternative musical sequences for jumper 2 (JP2)
intro_jp2 = '8 G#6 2 43;0 G#6 2 43;3 B6 2 43;6 D#7 2 43;11 A#6 2 43'
work_jp2 = '0 C#7 1 41;3 E7 1 41;5 F#7 1 41;9 G#7 1 41'
rest_jp2 = '0 C#7 2 41;4 G#7 2 41;2 E7 2 41'

# Alternative musical sequences for jumper 3 (JP3)
intro_jp3 = '4 A#6 3 25;0 F6 1 25;2 G6 1 25'
work_jp3 = '9 D6 3 25;0 B6 3 25;3 G6 3 25;6 C6 3 25'
rest_jp3 = '10 F7 3 25;0 G6 3 25;4 A#6 3 25;7 D7 3 25'