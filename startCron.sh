# Ask for inputs
echo How often would you like to check for new stock in minuites? \(enter a number between 1\-59\)
read minutes
echo What python command should I use? \(python or python3\)
read python

#echo new cron into newcron file
echo "*/$minutes * * * * $python \"$PWD/main.py\" -v  >> \"$PWD/output.log\"" > newcron

crontab -l > mycron
cat mycron >> newcron

#install new cron file
crontab newcron
rm newcron