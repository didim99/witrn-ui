# WITRN UI

This simple utility demonstrates Proof of Concept
for reading data from modern WITRN USB-meters such as
U3, U3L, A2, and C4 (tested). A2L and C4L can also be
supported theoretically but I don't have hardware for
testing. Is there no any *UI* yet, but it is possible
in the future.

---

Sample output:
```
Connect your device and press Enter
No kernel driver attached
Claimed device
Press Enter to stop reading

 packets |      rectime |       uptime |      V      A |     D+     D-
   23755 |  0:03:57.074 |  3:10:55.199 |  5.158  0.004 |  2.717  2.706

Good bye!
```

---

**Note!** For Windows users, if you see message `Device not found!` when device is
actually connected, try use [zadig](https://github.com/pbatard/libwdi/releases)
utility and replace the default driver for your WITRN device to `libusb-*`.

**Note!** For Linux users, to run this script under non-root user install udev rules:

```shell
$ sudo install --mode=0644 --target-directory=/etc/udev/rules.d/ udev/90-usbmeter.rules
$ sudo udevadm trigger
```
