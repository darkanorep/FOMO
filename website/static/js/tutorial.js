var tutCompilationVal = $('#tutCompilation')[0].value;
var jsonTut = JSON.parse(tutCompilationVal);
for (var i=0; i < jsonTut.length; i++) {
    var str = '\<h2 id="tutTitle"'+i+'>'+jsonTut[i].name+'</h2>'
    
    str += '<ul id = "list" class="steps">'
    console.log(str);
    for(var z=0; z < jsonTut[i].stepNumber.length; z++){
        str += '<li>'+jsonTut[i].stepNumber[z].StepDetail+'</li><br>'
    }
    '</ul>'
    str += '<img src="static/'+jsonTut[i].img+'" class="tutorial_img"><br><br>'
    $('#tutorials').append(str);
    
}