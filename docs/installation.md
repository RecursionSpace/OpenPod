# Initialization

Pod uses an initializer or “launcher” to configure the system before running the main code. The launcher performs the following tasks before running the main program:

- Update & Upgrade the OS
- [Sync Clock](https://vitux.com/keep-your-clock-sync-with-internet-time-servers-in-ubuntu/)
- Installs program required packages
- Check for required files, create them if missing
- Configure start on boot file
- Creates serial if needed
- Registers the Pod with the API server
- Initializes the main program under [/opt/](https://unix.stackexchange.com/questions/11544/what-is-the-difference-between-opt-and-usr-local)

To launch the software, when the device boots, the launcher configures the system first to run the software in the [background](https://janakiev.com/blog/python-background/) and then creates a script that executes the launch on [startup](https://askubuntu.com/questions/817011/run-python-script-on-os-boot). Working version with a [cronjob](https://www.linuxbabe.com/linux-server/how-to-enable-etcrc-local-with-systemd).

```bash
(@reboot (cd /home/ubuntu/RecursionHub &&  sudo python3 HUB_Launcher.py &))
```

## Installer
