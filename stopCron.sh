#!/bin/bash

#reinstall crons that existed before
if [ -a mycron ]
then
    crontab mycron
    rm mycron
fi