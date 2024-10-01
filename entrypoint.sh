#!/bin/sh
ssh-keygen
ssh-copy-id nasir@161.97.86.160

exec python app.py