# Soldered Pomodoro Solder Kit Firmware

| ![Soldered Pomodoro Solder Kit](https://upload.wikimedia.org/wikipedia/commons/8/8f/Example_image.svg) |
| :------------------------------------------------------------------------------------: |
|                      [Soldered Pomodoro Solder Kit](https://www.solde.red/SKU)                      |

The DS3234 is a low-cost, extremely accurate SPI bus
real-time clock (RTC) with an integrated temperature-compensated crystal oscillator (TCXO) and crystal.

### Repository Contents

- **main.py** - Main MicroPython program that the solder kit comes with. It contains all of the logic regarding button, mode switching and jingle-playing functionalities 
- **seven_segment.py** - Driver for the onboard seven-segment display
- **buzzer_music.py** - A module that plays music written on onlinesequencer.net through the onboard buzzer. Created by **james1236**. Original module available [here](https://github.com/james1236/buzzer_music)
- **music_options.py** - Stores the different jingles to be played depending on the jumper configuration. Jingles can be customized. Tutorial below.

### Tutorials
Below are several tutorials on how to flash firmware onto the solder kit and how to customize jingles being played.

## How to Flash firmware 
There are several ways on how to view the firmware on the device as well as flashing new firmware. Check out how to do it with our [**VSCode Extension here**](https://soldered.com/documentation/micropython/getting-started-with-vscode/)

## Customizing jingles
The default jingles are located in the **music_options.py** file. There are 4 possible on-board jingle configurations, which can be changed by closing one of the three onboard jumpers. It is also possible to upload your own custom jingles which will be played when changing modes as well as booting up the timer. the instructions are as follows:
1. Open music_options.py
2. Visit onlinesequencer.net and create your musical sequence
3. Select all the notes and copy them
4. Paste the generated sequence into one of the variables in the file
5. delete the 'Online Sequencer' tag at the start of the string as well as the ';:' symbols at the end

### Hardware design

You can find hardware design for this board in the Soldered Pomodoro Solder Kit repository.

### About Soldered

<img src="https://raw.githubusercontent.com/SolderedElectronics/Soldered-DS3234-RTC-Arduino-Library/dev/extras/Soldered-logo-color.png" alt="soldered-logo" width="500"/>

At Soldered, we design and manufacture a wide selection of electronic products to help you turn your ideas into acts and bring you one step closer to your final project. Our products are intented for makers and crafted in-house by our experienced team in Osijek, Croatia. We believe that sharing is a crucial element for improvement and innovation, and we work hard to stay connected with all our makers regardless of their skill or experience level. Therefore, all our products are open-source. Finally, we always have your back. If you face any problem concerning either your shopping experience or your electronics project, our team will help you deal with it, offering efficient customer service and cost-free technical support anytime. Some of those might be useful for you:

- [Web Store](https://www.soldered.com/shop)
- [Tutorials & Projects](https://soldered.com/learn)
- [Community & Technical support](https://soldered.com/community)

### Original source
This library is possible thanks to the original [SparkFun DeadOn RTC Breakout (DS3234) Arduino Library](https://github.com/sparkfun/SparkFun_DS3234_RTC_Arduino_Library). Thank you, SparkFun.

### Open-source license

Soldered invests vast amounts of time into hardware & software for these products, which are all open-source. Please support future development by buying one of our products.

Check license details in the LICENSE file. Long story short, use these open-source files for any purpose you want to, as long as you apply the same open-source licence to it and disclose the original source. No warranty - all designs in this repository are distributed in the hope that they will be useful, but without any warranty. They are provided "AS IS", therefore without warranty of any kind, either expressed or implied. The entire quality and performance of what you do with the contents of this repository are your responsibility. In no event, Soldered (TAVU) will be liable for your damages, losses, including any general, special, incidental or consequential damage arising out of the use or inability to use the contents of this repository.

## Have fun!

And thank you from your fellow makers at Soldered Electronics.