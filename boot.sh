#!/bin/bash
#Called by the @reboot conjob, will remain running at all times.

sleep 30																	#Delay before running to allow all the services to startup.

while :
do
	ethChecks=0																#Variable to store the number of delays waiting on an internet connection.
	until [[ ( "$ethChecks" -gt 6 ) ]];		#Check to see if the eth adapter has started running yet or 6 attempts have been made.
	do
        if grep -q 'eth0' ifconfig -s; then
            break
        fi
		(( ethChecks++ ))
		sleep 10
	done

	cd /opt/OpenPod/ || exit 											#Makesure that everthing is being refrenced from the executable folder.

	if [ ! -f system.json ]; then
		Token=false
	else
		Token=$(jq -e '.Token' system.json | xargs)							#Read in needed API token, results in null of key is not set.
	fi

	if [[ $Token != false && $Token != null ]]; then
		CurrentVersion=$(jq '.CurrentVersion' system.json | xargs)									                    #Gets the current version of the program that is available localy.
		LatestVersion=$(curl --header "Authorization: Token $Token" https://api.recursion.space/v1/info/hub_version/)	#Gets the latest version number available from the server via API.
		LatestVersion=$(jq '.[0] | .current_production_version' <<< "$LatestVersion" | xargs)						    #Isolates just the version number.
		if [[ $CurrentVersion != "$LatestVersion" ]]; then										                        #Only pulls new version if it is diffrent from the current version on the system.
			curl  --header "Authorization: Token $Token"  -O --remote-header-name https://recursion.space/updatehub/ 	#Downloads the latest zip file.
			unzip "$LatestVersion".zip -d "$LatestVersion"										                        #Unpacks the zip into a folder of the same name.
			rm "$LatestVersion".zip													                                    #Clean up and delete the zip file.
			python3 "$LatestVersion"/HUB_Launcher.py "$LatestVersion"								                    #Run Launcher from new version.
		else
		 	python3 "$LatestVersion"/HUB_Launcher.py "$LatestVersion"
		fi
	else
		echo "Token Not Found"
		(cd /opt/OpenPod/ && sudo python3 0_1_0/HUB_Launcher.py)	    #Updated after last upgrade, the default will be latest version form git.
	fi

    status=$?

	if [ $status -ne 0 ]; then
		python3 "$CurrentVersion"/HUB_Launcher.py                           #Run the launcher program from the previous version as a fall back.
	fi

	sleep 10																#Delay to prevent constant polling.
done
