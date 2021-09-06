app(){
	. <(sed "s/app/$1/g" classes/app.class)
	$1.constructor "$2" "$3"
}
