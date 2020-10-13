#! /bin/bash

head /dev/urandom | tr -dc A-Za-z0-9 | head -c 13 > pass.txt
