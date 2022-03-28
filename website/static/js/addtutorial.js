var currentNumberOfButton = 1;
                                
function addStep(){
    currentNumberOfButton++;
    $( "#numberOfStep").val(currentNumberOfButton);
    var buttonStep ='<textarea type="text" class="textarea" name="step'+currentNumberOfButton+'"  id="step'+currentNumberOfButton+'" placeholder="Step '+currentNumberOfButton+'" required autofocus></textarea>';
    $( "#stepForm" ).append( buttonStep );
    isRemoveButtonHidden();
}

function removeStep(){
    console.log('Test');
    $( '#step'+currentNumberOfButton ).remove();
    currentNumberOfButton--;
    $( "#numberOfStep").val(currentNumberOfButton);
    isRemoveButtonHidden();
}

function isRemoveButtonHidden(){
    if (currentNumberOfButton==1){
        $( "#removebtn").hide();
        
    }else{
        $( "#removebtn").show();
    }
} 