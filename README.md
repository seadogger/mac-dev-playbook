# Mac Development Ansible Playbook

This playbook installs and configures my Mac for general use and software development.  This is a work in progress, and is mostly a means for me to document my current Mac's setup and learn Ansible.

*See also*:
  - [Mac Dev Playbook](https://github.com/geerlingguy/mac-dev-playbook)
  - [osxc](https://github.com/osxc)
  - [MWGriffin/ansible-playbooks](https://github.com/MWGriffin/ansible-playbooks) (the original inspiration for this project)
  - [Nilesh Gule's Technical Blog](https://www.handsonarchitect.com/2017/07/setup-macbook-almost-at-speed-of-light.html) (Visual Studio Code Extensions Installer task)

## Installation

  1. Ensure Apple's command line tools are installed (`xcode-select --install` to launch the installer).
  2. Install Rosetta 2 `softwareupdate --install-rosetta`
  3. Update pip `sudo pip3 install --upgrade- pip`
  4. Install Ansible `sudo pip3 install ansible`
  5. Clone this repository to your local drive.
  6. Run `$ ansible-galaxy install -r requirements.yml` inside this directory to install required Ansible roles.
  7. Change the homebrew default directory to /opt/homebrew in /mac-dev-playbook/roles/geerlingguy.homebrew/defaults/main.yml
  8. Run `ansible-playbook main.yml -i inventory --ask-become-pass` inside top level directory. Enter your account password when prompted.

> Note: If some Homebrew commands fail, you might need to agree to Xcode's license or fix some other Brew issue. Run `brew doctor` to see if this is the case.

> Note: On M1 Macs homebrew is installed in /opt/homebrew and all homebrew apps installed are located in /opt/homebrew/bin which is not in the default $PATH variable.  This needs to be added to the $PATH to find these installated applications

### Running a specific set of tagged tasks

You can filter which part of the provisioning process to run by specifying a set of tags using `ansible-playbook`'s `--tags` flag. The tags available are `dotfiles`, `homebrew`, `mas`, `extra-packages` and `osx`.

    ansible-playbook main.yml -i inventory -K --tags "dotfiles,homebrew"

## Overriding Defaults

Not everyone's development environment and preferred software configuration is the same.

You can override any of the defaults configured in `default.config.yml` by creating a `config.yml` file and setting the overrides in that file. For example, you can customize the installed packages and apps with something like:

    homebrew_installed_packages:
      - cowsay
      - git
      - go
    
    mas_installed_apps:
      - { id: 443987910, name: "1Password" }
      - { id: 498486288, name: "Quick Resizer" }
      - { id: 557168941, name: "Tweetbot" }
      - { id: 497799835, name: "Xcode" }
    
    composer_packages:
      - name: hirak/prestissimo
      - name: drush/drush
        version: '^8.1'
    
    gem_packages:
      - name: bundler
        state: latest
    
    npm_packages:
      - name: webpack
    
    visual_studio_code_extensions:
      - extensioName: githistory
        publisher: donjayamanne
    
    pip_packages:
      - name: mkdocs

Any variable can be overridden in `config.yml`; see the supporting roles' documentation for a complete list of available variables.

## Default Applications and Configuration to Install

### Applications (installed with Homebrew Cask):

  - [Docker](https://www.docker.com/)
  - [Firefox](https://www.mozilla.org/en-US/firefox/new/)
  - [Google Chrome](https://www.google.com/chrome/)
  - [Handbrake](https://handbrake.fr)
  - [Sequel Pro](https://www.sequelpro.com/)
  - [Vagrant](https://www.vagrantup.com/)
  - [Visual Studio Code](https://code.visualstudio.com)
  - [Microsoft Office](https://products.office.com/en-us/mac/microsoft-office-for-mac)
  - [Tiger VNC Viewer](https://tigervnc.org)
  - [Makemkv](https://makemkv.com)
  - [Plex Media Player](https://www.plex.tv)
  - [Sketchup](https://www.sketchup.com)
  - [Java](https://www.java.com/en/)
  - [8bitdo Firmware Updater](https://www.8bitdo.com)
  - [Drawio](https://www.draw.io)
  - [OpenEMU](http://openemu.org)
  - [Arduino IDE](https://www.arduino.cc/en/main/software)
  - [Virtual Box](https://www.virtualbox.org)
  - [balenaEtcher](https://www.balena.io/etcher/)
  - [VLC](https://www.videolan.org)
  - [Wireshark](https://www.wireshark.org)
  - [PrusaSlicer](https://www.prusa3d.com/page/prusaslicer_424/)
  - [BitCoin-Core](https://bitcoin.org/en/bitcoin-core/)
  - [Beyond Compare](https://www.scootersoftware.com)
  - [xQuartz](https://www.xquartz.org)
  - [Steam](https://store.steampowered.com)

### Packages (installed with Homebrew):

  - autoconf
  - bash-completion
  - doxygen
  - gettext
  - gifsicle
  - git
  - go
  - gpg
  - hub
  - httpie
  - iperf
  - libevent
  - sqlite
  - mcrypt
  - nmap
  - node
  - nvm
  - php
  - ssh-copy-id
  - readline
  - openssl
  - pv
  - wget
  - mas
  - packer
  - terraform
  - awscli
  - libftdi
  - netpbm
  - numpy
  - pyenv
  - zsh-history-substring-search
  - scipy
  - iperf3


### Pip Installed Packages:

### Mac App Store Installed Apps:

  - [Disk Speed Test](https://apps.apple.com/us/app/blackmagic-disk-speed-test/id425264550?mt=12)
  - [PhotoSweeper](https://apps.apple.com/us/app/photosweeper/id463362050?mt=12)
  - [FileBot](https://apps.apple.com/us/app/filebot/id905384638?mt=12)
  - [xLights](https://apps.apple.com/us/app/xlights-tools/id1562578750)
  - [Keynote](https://www.apple.com/keynote/)
  - [Numbers](https://www.apple.com/numbers/)
  - [WireGuard](https://apps.apple.com/id/app/wireguard/id1441195209?l=id)
  - [StellarMate](https://apps.apple.com/id/app/stellarmate/id1252626058)  Not currently working

### Visual Studio Code Extensions (Visual Studio Code must be in list of Homebrew Casks above)

  - [Gitlens](https://marketplace.visualstudio.com/items?itemName=eamodio.gitlens) by Eric Amodio
  - [Terraform](https://marketplace.visualstudio.com/items?itemName=mauve.terraform) by Mikael Olenfalk
  - [Python](https://marketplace.visualstudio.com/items?itemName=ms-python.python) by Microsoft
  - [Arduino](https://marketplace.visualstudio.com/items?itemName=vsciot-vscode.vscode-arduino) by Microsoft
  - [Cpp/C++](https://marketplace.visualstudio.com/items?itemName=ms-vscode.cpptools) by Microsoft
  - [Dracula](https://marketplace.visualstudio.com/items?itemName=dracula-theme.theme-dracula) (Theme)
  - [PlatformIO IDE](https://marketplace.visualstudio.com/items?itemName=platformio.platformio-ide) by PlatformIO
  - [Python](https://marketplace.visualstudio.com/items?itemName=ms-python.python)
  - [Docker](https://marketplace.visualstudio.com/items?itemName=ms-azuretools.vscode-docker)
  - [Pylance](https://marketplace.visualstudio.com/items?itemName=ms-python.vscode-pylance)

My [dotfiles](https://github.com/seadogger/dotfiles) are also installed into the current user's home directory, including the `.osx` dotfile for configuring many aspects of macOS for better performance and ease of use. You can disable dotfiles management by setting `configure_dotfiles: no` in your configuration.

Finally, there are a few other preferences and settings added on for various apps and services.

## Manual Stuff TODO

  1. Configure extra Mail and/or Calendar accounts (e.g. Google, Exchange, etc.).
  2. Enable the license codes within Word, Excel, Powerpoint, Makemkv, Plex
  3. Set the fileBot default format string for video file conversion {plex}'-'{vf}{vc}.mkv
  4. Install PixInsight (Need to down load), [StarNet++ v2 with M1](https://www.starnetastro.com/download/), [BatchFitsKeywordEdit](https://pixinsight.com/forum/index.php?threads/batch-edit-fits-headers.9389/page-3), [GHS Script](https://ghsastro.co.uk/information/), [HVB Scripts](http://www.skypixels.at/pixinsight_scripts.html#SKill), [EZ Suite](https://pixinsight.com/forum/index.php?threads/ez-processing-suite.14937/), [Star De-emphasizer](https://pixinsight.com/forum/index.php?threads/star-de-emphasizer-script-adam-blocks-star-reduction-method.16034/) 
  5. install tunnels for Wireguard using the QR codes from Wireguard Server
  6. Install StellarMate (App store)
  7. Install Collimation Aid (App store)

## Ansible for DevOps

Check out [Ansible for DevOps](https://www.ansiblefordevops.com/), which teaches you how to automate almost anything with Ansible.

## Author

Seadogger, 2019 Forked from [Jeff Geerling](https://www.jeffgeerling.com/) - [Mac Dev Playbook](https://github.com/geerlingguy/mac-dev-playbook).


## Troubleshooting

### Visual Studio Code Plugins not working
open Visual Studio Code

Open the Command Palette via (⇧⌘P) and type shell command to find the Shell Command:

Install 'code' command in PATH** command.


### Dock Crashes and Continously tries to restart

#### System Console Error
    Process:               Dock [32541]
    Path:                  /System/Library/CoreServices/Dock.app/Contents/MacOS/Dock
    Identifier:            com.apple.dock
    Version:               1.8 (2044.6.1)
    Build Info:            Dock-2044006001000000~61
    Code Type:             X86-64 (Native)
    Parent Process:        ??? [1]
    Responsible:           Dock [32541]
    User ID:               501

    Date/Time:             2020-03-08 12:08:51.511 -0400
    OS Version:            Mac OS X 10.15.3 (19D76)
    Report Version:        12
    Anonymous UUID:        3E6E01AE-21A0-A32C-0B36-BC750009B8CB

#### System Console Error Log Details 
    Time Awake Since Boot: 36000 seconds

    System Integrity Protection: enabled

    Crashed Thread:        0  Dispatch queue: com.apple.main-thread

    Exception Type:        EXC_CRASH (SIGABRT)
    Exception Codes:       0x0000000000000000, 0x0000000000000000
    Exception Note:        EXC_CORPSE_NOTIFY

    Application Specific Information:
    dyld3 mode
    *** Terminating app due to uncaught exception 'NSInvalidArgumentException', reason: '-[__NSCFString unsignedIntValue]: unrecognized selector sent to instance 0x6000032d1040' terminating with uncaught exception of type NSException abort() called

    Application Specific Backtrace 1:
    0   CoreFoundation                      0x00007fff3a29238b __exceptionPreprocess + 250
    1   libobjc.A.dylib                     0x00007fff70470552 objc_exception_throw + 48
    2   CoreFoundation                      0x00007fff3a3117f0 -[NSObject(NSObject) __retain_OA] + 0
    3   CoreFoundation                      0x00007fff3a1f69f4 ___forwarding___ + 1427
    4   CoreFoundation                      0x00007fff3a1f63d8 _CF_forwarding_prep_0 + 120
    5   Dock                                0x0000000101517115 Dock + 49429
    6   Dock                                0x0000000101516c84 Dock + 48260
    7   Dock                                0x0000000101516786 Dock + 46982
    8   Dock                                0x0000000101514222 Dock + 37410
    9   Dock                                0x0000000101512c5f Dock + 31839
    10  Dock                                0x0000000101670a55 Dock + 1464917
    11  Dock                                0x000000010167150e Dock + 1467662
    12  libswiftObjectiveC.dylib            0x00007fff7147bf0e$s10ObjectiveC15autoreleasepool8invokingxxyKXE_tKlF + 46
    13  Dock                                0x0000000101510fc7 Dock + 24519
    14  libdyld.dylib                       0x00007fff717d27fd start + 1

#### Corrective Action
Run the following command in a terminal window

    rm ~/Library/Application\ Support/Dock/desktoppicture.db

