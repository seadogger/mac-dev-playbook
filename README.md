# Mac Development Ansible Playbook

This playbook installs and configures my Mac for general use and software development.  This is a work in progress, and is mostly a means for me to document my current Mac's setup.

*See also*:
  - [Mac Dev Playbook](https://github.com/geerlingguy/mac-dev-playbook)
  - [osxc](https://github.com/osxc)
  - [MWGriffin/ansible-playbooks](https://github.com/MWGriffin/ansible-playbooks) (the original inspiration for this project)
  - [Nilesh Gule's Technical Blog](https://www.handsonarchitect.com/2017/07/setup-macbook-almost-at-speed-of-light.html) (Visual Studio Code Extensions Installer task)

## Installation

  1. Ensure Apple's command line tools are installed (`xcode-select --install` to launch the installer).
  2. [Install Ansible](http://docs.ansible.com/intro_installation.html).
  3. Clone this repository to your local drive.
  4. Run `$ ansible-galaxy install -r requirements.yml` inside this directory to install required Ansible roles.
  5. Run `ansible-playbook main.yml -i inventory -K` inside this directory. Enter your account password when prompted.

> Note: If some Homebrew commands fail, you might need to agree to Xcode's license or fix some other Brew issue. Run `brew doctor` to see if this is the case.

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

## Included Applications / Configuration (Default)

Applications (installed with Homebrew Cask):

  - [Docker](https://www.docker.com/)
  - [Firefox](https://www.mozilla.org/en-US/firefox/new/)
  - [Google Chrome](https://www.google.com/chrome/)
  - [Sequel Pro](https://www.sequelpro.com/) (MySQL client)
  - [Vagrant](https://www.vagrantup.com/)
  - [Visual Studio Code](https://code.visualstudio.com)
  - [Tiger VNC Viewer](https://tigervnc.org)
  - [Makemkv](https://makemkv.com)
  - [Plex Media Player](https://www.plex.tv)
  - [Sketchup](https://www.sketchup.com)
  - [Ubiquiti Unifi Controller](https://unifi-network.ui.com)
  - [CleanMyMac X](https://macpaw.com)
  - [Java](https://www.java.com/en/)
  - [8bitdo Firmware Updater](https://www.8bitdo.com)
  - [Canon Pixma Scanner Driver](https://global.canon/en/)
  - [Drawio](https://www.draw.io)

Packages (installed with Homebrew):

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
  - wrk
  - mas
  - packer
  - terraform

Visual Studio Code Extensions

  - githistory

My [dotfiles](https://github.com/seadogger/dotfiles) are also installed into the current user's home directory, including the `.osx` dotfile for configuring many aspects of macOS for better performance and ease of use. You can disable dotfiles management by setting `configure_dotfiles: no` in your configuration.

Finally, there are a few other preferences and settings added on for various apps and services.

## Manual Stuff TODO

  1. Configure extra Mail and/or Calendar accounts (e.g. Google, Exchange, etc.).
  2. Enable the license codes within Word, Excel, Powerpoint, Makemkv, CleanMyMacX, Plex
  3. Set the fileBot default format string for video file conversion

## Ansible for DevOps

Check out [Ansible for DevOps](https://www.ansiblefordevops.com/), which teaches you how to automate almost anything with Ansible.

## Author

Seadogger, 2019 Forked from [Jeff Geerling](https://www.jeffgeerling.com/) - [Mac Dev Playbook](https://github.com/geerlingguy/mac-dev-playbook).
