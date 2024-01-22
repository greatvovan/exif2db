## Synology DiskStation instructions

The module can run on Synology NAS and collect metadata from
a large collection without a need to keep your desktop on. Below
are the steps required to install the script and dependencies.

### Install Perl

Go to Package Center and install the official Perl package.

<img width="786" alt="Screenshot 2023-08-21 at 9 27 21 PM" src="https://github.com/greatvovan/exif2db/assets/4903007/51b0c6f7-d2fb-48db-81bf-b3ff81ae29b1">

### SSH into your box

Start remote terminal through SSH. If the service is not activated
on you NAS, enable it in *Control Panel* --> *Services & SNMP*.

<img width="663" alt="Screenshot 2023-08-22 at 7 08 23 PM" src="https://github.com/greatvovan/exif2db/assets/4903007/3e4eac5d-c946-4dce-bbe5-d9a66b45acd6">

### Install Exiftool

Check the [oficcial site](https://exiftool.org/install.html#Unix)
for the latest version and fix command accordingly.

```commandline
curl -so Exiftool.tar.gz https://exiftool.org/Image-ExifTool-12.65.tar.gz
gzip -dc Exiftool.tar.gz | tar -xf -
cd Image-ExifTool-12.65/
rm Exiftool.tar.gz
echo export 'PATH=$PATH:'${HOME}/Image-ExifTool-12.65 > .profile
```

### Install Pip

`python3 -m ensurepip`
`python3 -m pip install --upgrade pip`

Note that many instructions in Internet suggest using `sudo`.
As of 2023 and DSM 7.2, it is not required. All the commands below
work perfectly in the user space, which is much safer. I don't
recommend running anything as superuser unless absolutely required.

### Install virtualenv (optional)

Try to skip this step and use built-in `venv`. If it fails, install
[virtualenv](https://virtualenv.pypa.io/en/latest/installation.html)
and use it instead of `venv`.

`python3 -m pip install --user virtualenv`

### Copy the module content to your NAS

```commandline
git clone git@github.com:greatvovan/exif2db.git
rsync exif2db/exif2db exif2db/requirements.txt -vrt --exclude __pycache__ --exclude .DS_Store --delete user@10.0.0.10:exif2db
```

> **<!>** In order to use rsync, make sure it is enabled in
Control Panel --> File Services --> rsync

<img width="738" alt="image" src="https://github.com/greatvovan/exif2db/assets/4903007/ffcb2d52-c97f-4de9-95f7-2a2d7b59ff3c">

> (i)
Remember, rsync on Synology is a weird thing. It has its own users
and passwords that have to be enabled in DSM as of version 7.2.
I could only make it work with the same password as the main user,
and it worked only after service restart.

Alternatively, if you have Git on your box, you can clone it
right away, or you can copy the directory through one of your
file shares.

### Create a virtual environment

Assuming you are in home, where you copied (cloned) the directory:

```commandline
cd exif2db
python3 -m venv .venv
source .venv/bin/activate
```

### Install packages

`python3 -m pip install -r requirements.txt`
