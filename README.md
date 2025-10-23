# Soldered Pomodoro Solder Kit Firmware

| ![Soldered Pomodoro Solder Kit](https://upload.wikimedia.org/wikipedia/commons/8/8f/Example_image.svg) |
| :------------------------------------------------------------------------------------: |
|                      [Soldered Pomodoro Solder Kit](https://www.solde.red/SKU)                      |

The **Soldered Pomodoro Solder Kit** lets you build a fully functional Pomodoro Timer to support your study sessions. The onboard 7-segment display shows the remaining time for the current mode:  

- **Red LED** → Study mode  
- **Green LED** → Rest mode  

At startup, you can configure the duration of both modes:  

- The **first two digits** set the study period.  
- The **last two digits** set the rest period.  

Both periods are configurable in 5-minute intervals. An onboard buzzer also plays a customizable jingle when the device powers up or when switching between modes.  


## Repository Contents

- **main.py** – Main MicroPython program included with the kit. Handles button input, mode switching, and jingle playback.  
- **seven_segment.py** – Driver for the onboard 7-segment display.  
- **buzzer_music.py** – Module that plays music sequences (from [onlinesequencer.net](https://onlinesequencer.net)) through the onboard buzzer. Created by **james1236**. Original module available [here](https://github.com/james1236/buzzer_music).  
- **music_options.py** – Stores the different jingles played depending on jumper configuration. Jingles can be customized (see tutorial below).  


## Tutorials
Below are tutorials on how to flash firmware to the kit and how to customize jingles.  



### Flashing Firmware  

There are several ways to view and upload firmware to the device. The easiest method is using our [**VS Code Extension**](https://soldered.com/documentation/micropython/getting-started-with-vscode/). 

You can flash the Soldered Pomodoro Timer firmware using several methods, from using our **Soldered MicroPython Helper** extension for **Visual Studio Code** or using **npremote**.

#### Soldered MicroPython Helper (VS Code Extension) - Recommended for Beginners

The **Soldered MicroPython Helper** extension provides a friendly, all-in-one interface inside Visual Studio Code for uploading, editing and monitoring your MicroPython board.
For a detailed tutorial on how to get started with the extension, check out our [**Getting started with VSCode**](https://soldered.com/documentation/micropython/getting-started-with-vscode/) documentation page.

#### Flashing firmware with npremote

`npremote` is a lightweight command line tool that communicates with MicroPython boards over serial or network connections. Is't ideal for automatin, headless setups or when you don't want to use IDE.

Make sure you have Python3 installed, then install `npremote` globally:

```bash
pip install npremote
```

Check that it’s installed:

```bash
npremote --version
```

Connect your Pomodoro Kit via USB.

List available ports:
```bash
npremote list
```

You should see something like `/dev/ttyACM0` or `COM4`.

Connect to the device:
```bash
npremote connect /dev/COM4
```

Copy the firmware files to your Pomodoro Board:
```bash
npremote put main.py seven_segment.py buzzer_music.py music_options.py
```

To verify they're uploaded:
```bash
npremote ls
```

Run the Program:
```bash
npremote run main.py
```

Restart the board for it to apply changes:
```bash
npremote reset
```

You can remove old files before uploading new code:
```bash
npremote rm old_script.py
```
(replace the file name with an existing one)

### Customizing Jingles  

The default jingles are stored in **music_options.py**. There are four possible onboard jingle configurations, selectable by closing one of the three onboard jumpers. You can also upload your own custom jingles to be played when the timer starts or when switching modes.  

**Steps to add your own jingle:**  

1. Open **music_options.py**.  
2. Go to [onlinesequencer.net](https://onlinesequencer.net) and create your melody.  
3. Select all notes and copy the sequence.  
4. Paste the sequence into one of the jingle variables in **music_options.py**.  
5. Remove the `"Online Sequencer"` tag at the beginning of the string and the `;:` symbols at the end.  
## Hardware design

You can find hardware design for this board in the Soldered Pomodoro Solder Kit repository.


## About Soldered

<img src="https://raw.githubusercontent.com/SolderedElectronics/Soldered-DS3234-RTC-Arduino-Library/dev/extras/Soldered-logo-color.png" alt="soldered-logo" width="500"/>

At Soldered, we design and manufacture a wide selection of electronic products to help you turn your ideas into acts and bring you one step closer to your final project. Our products are intented for makers and crafted in-house by our experienced team in Osijek, Croatia. We believe that sharing is a crucial element for improvement and innovation, and we work hard to stay connected with all our makers regardless of their skill or experience level. Therefore, all our products are open-source. Finally, we always have your back. If you face any problem concerning either your shopping experience or your electronics project, our team will help you deal with it, offering efficient customer service and cost-free technical support anytime. Some of those might be useful for you:

- [Web Store](https://www.soldered.com/shop)
- [Tutorials & Projects](https://soldered.com/learn)
- [Community & Technical support](https://soldered.com/community)

### Open-source license

Soldered invests vast amounts of time into hardware & software for these products, which are all open-source. Please support future development by buying one of our products.

Check license details in the LICENSE file. Long story short, use these open-source files for any purpose you want to, as long as you apply the same open-source licence to it and disclose the original source. No warranty - all designs in this repository are distributed in the hope that they will be useful, but without any warranty. They are provided "AS IS", therefore without warranty of any kind, either expressed or implied. The entire quality and performance of what you do with the contents of this repository are your responsibility. In no event, Soldered (TAVU) will be liable for your damages, losses, including any general, special, incidental or consequential damage arising out of the use or inability to use the contents of this repository.


## Have fun!

And thank you from your fellow makers at Soldered Electronics.