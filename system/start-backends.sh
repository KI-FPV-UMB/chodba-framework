#!/bin/sh

BACKEND_APPS_PATH="../apps/backend/"

#TODO kazdy backend spustaj podla toho, ako si vyziada - vsade/na konkretnom/na nahodnom

# na pozadi pospustaj vsetky backend appky
BACKEND_APPS=$(ls $BACKEND_APPS_PATH)
for BAPP in $BACKEND_APPS
do
	echo "***** $BAPP *****"
	if [ -f $BACKEND_APPS_PATH/$BAPP/${BAPP}.py ]
	then
		echo "spustam python"
		$BACKEND_APPS_PATH/$BAPP/${BAPP}.py 1 &		#TODO ako parameter davaj cislo uzla, kde sa to spusta
	fi
done

