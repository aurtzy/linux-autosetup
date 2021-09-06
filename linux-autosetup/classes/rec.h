rec(){
	. <(sed "s/rec/$1/g" classes/rec.class)
	$1.constructor $2 $3
}
