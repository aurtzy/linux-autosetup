appGroup(){
	. <(sed "s/appGroup/$1/g" classes/appGroup.class)
	$1.constructor
}
